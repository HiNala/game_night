"""
Enhanced Flight Physics System
Realistic aerodynamic simulation for flying squirrel gliding mechanics.
"""

import math
from ursina import *
import random

class FlightPhysics:
    """Advanced flight physics engine with realistic aerodynamics"""
    
    def __init__(self, entity, config):
        self.entity = entity
        self.config = config
        
        # Physics state
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.forces = Vec3(0, 0, 0)
        self.torques = Vec3(0, 0, 0)
        
        # Aerodynamic properties
        self.mass = config['mass']
        self.wing_area = config['wing_area']
        self.lift_coefficient = config['lift_coefficient']
        self.drag_coefficient = config['drag_coefficient']
        self.moment_coefficient = 0.1
        
        # Environmental factors
        self.air_density = 1.225  # kg/m³
        self.wind_velocity = Vec3(0, 0, 0)
        self.thermal_map = {}
        
        # Flight envelope
        self.stall_angle = math.radians(15)  # 15 degrees
        self.max_g_force = 4.0
        
        self.generate_thermal_map()
    
    def generate_thermal_map(self):
        """Generate thermal updraft locations"""
        for i in range(20):  # 20 thermal zones
            x = random.uniform(-100, 100)
            z = random.uniform(-100, 100)
            strength = random.uniform(2, 8)  # m/s updraft
            radius = random.uniform(15, 30)
            
            self.thermal_map[(x, z)] = {
                'strength': strength,
                'radius': radius,
                'turbulence': random.uniform(0.1, 0.5)
            }
    
    def get_thermal_effect(self, position):
        """Calculate thermal updraft at given position"""
        thermal_force = Vec3(0, 0, 0)
        
        for (tx, tz), thermal in self.thermal_map.items():
            distance = math.sqrt((position.x - tx)**2 + (position.z - tz)**2)
            
            if distance < thermal['radius']:
                # Thermal strength decreases with distance from center
                strength_factor = max(0, 1 - (distance / thermal['radius']))
                updraft = thermal['strength'] * strength_factor
                
                # Add some turbulence
                turbulence = random.uniform(-thermal['turbulence'], thermal['turbulence'])
                
                thermal_force.y += updraft + turbulence
                
                # Add slight horizontal components for realism
                thermal_force.x += random.uniform(-0.5, 0.5)
                thermal_force.z += random.uniform(-0.5, 0.5)
        
        return thermal_force
    
    def calculate_aerodynamic_forces(self, dt):
        """Calculate lift, drag, and moment forces"""
        # Relative wind velocity (velocity relative to air mass)
        relative_velocity = self.velocity - self.wind_velocity
        airspeed = distance(relative_velocity, Vec3(0, 0, 0))
        
        if airspeed < 0.1:
            return Vec3(0, 0, 0), Vec3(0, 0, 0)
        
        # Dynamic pressure
        q = 0.5 * self.air_density * airspeed**2
        
        # Angle of attack (simplified)
        pitch = self.entity.rotation_x * math.pi / 180
        angle_of_attack = pitch
        
        # Lift calculation
        if abs(angle_of_attack) < self.stall_angle:
            cl = self.lift_coefficient * math.sin(2 * angle_of_attack)
        else:
            # Post-stall behavior
            cl = self.lift_coefficient * math.cos(angle_of_attack) * 0.5
        
        lift_magnitude = cl * q * self.wing_area
        
        # Lift direction (perpendicular to velocity)
        if airspeed > 0:
            velocity_normalized = relative_velocity.normalized()
            # Simplified lift direction (upward component)
            lift_direction = Vec3(0, 1, 0)
            lift_force = lift_direction * lift_magnitude
        else:
            lift_force = Vec3(0, 0, 0)
        
        # Drag calculation
        cd = self.drag_coefficient + (cl**2) / (math.pi * 8)  # Induced drag
        drag_magnitude = cd * q * self.wing_area
        
        # Drag direction (opposite to velocity)
        if airspeed > 0:
            drag_direction = -relative_velocity.normalized()
            drag_force = drag_direction * drag_magnitude
        else:
            drag_force = Vec3(0, 0, 0)
        
        # Combine aerodynamic forces
        aero_force = lift_force + drag_force
        
        # Moment calculation (simplified)
        moment = Vec3(0, 0, 0)
        if airspeed > 0:
            moment.x = -self.moment_coefficient * q * self.wing_area * angle_of_attack
        
        return aero_force, moment
    
    def update(self, dt):
        """Update physics simulation"""
        # Reset forces and torques
        self.forces = Vec3(0, 0, 0)
        self.torques = Vec3(0, 0, 0)
        
        # Gravity
        gravity_force = Vec3(0, self.mass * -9.81, 0)
        self.forces += gravity_force
        
        # Thermal effects
        thermal_force = self.get_thermal_effect(self.entity.position)
        self.forces += thermal_force * self.mass
        
        # Aerodynamic forces
        aero_force, aero_moment = self.calculate_aerodynamic_forces(dt)
        self.forces += aero_force
        self.torques += aero_moment
        
        # Wind effects
        wind_force = self.get_wind_force()
        self.forces += wind_force
        
        # Update velocity and position
        acceleration = self.forces / self.mass
        self.velocity += acceleration * dt
        
        # Limit terminal velocity
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > 50:  # Terminal velocity
            self.velocity = self.velocity.normalized() * 50
        
        # Update position
        self.entity.position += self.velocity * dt
        
        # Update angular motion (simplified)
        angular_acceleration = self.torques / (self.mass * 0.5)  # Simplified moment of inertia
        self.angular_velocity += angular_acceleration * dt
        
        # Apply angular damping
        self.angular_velocity *= 0.95
        
        return {
            'speed': speed,
            'altitude': self.entity.position.y,
            'g_force': distance(acceleration, Vec3(0, 0, 0)) / 9.81,
            'thermal_strength': thermal_force.y
        }
    
    def get_wind_force(self):
        """Calculate wind effects"""
        # Simple wind model
        wind_speed = Vec3(
            math.sin(time.time() * 0.1) * 2,
            0,
            math.cos(time.time() * 0.15) * 1.5
        )
        
        # Wind force proportional to relative velocity
        relative_wind = wind_speed - self.velocity
        wind_force = relative_wind * 0.1 * self.air_density
        
        return wind_force
    
    def apply_control_input(self, pitch_input, yaw_input, roll_input):
        """Apply pilot control inputs"""
        # Control surface effectiveness based on airspeed
        airspeed = distance(self.velocity, Vec3(0, 0, 0))
        effectiveness = min(1.0, airspeed / 10)  # Full effectiveness at 10 m/s
        
        # Apply control moments
        control_authority = 5.0  # Control power
        
        self.torques.x += pitch_input * control_authority * effectiveness
        self.torques.y += yaw_input * control_authority * effectiveness
        self.torques.z += roll_input * control_authority * effectiveness 