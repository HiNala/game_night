"""
🚁 ENHANCED FLIGHT PHYSICS ENGINE 🚁
Next-generation realistic aerodynamics with advanced environmental simulation.
Built for maximum realism and epic gameplay.
"""

import math
import random
import numpy as np
from ursina import *

class AdvancedFlightPhysics:
    """State-of-the-art flight physics with realistic aerodynamics"""
    
    def __init__(self, entity, config):
        self.entity = entity
        self.config = config
        
        # Advanced physics state
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.angular_acceleration = Vec3(0, 0, 0)
        
        # Mass properties
        self.mass = config.get('mass', 1.5)
        self.moment_of_inertia = Vec3(0.5, 0.3, 0.8) * self.mass  # Realistic MOI
        
        # Aerodynamic properties
        self.wing_area = config.get('wing_area', 2.5)
        self.wing_span = config.get('wing_span', 3.0)
        self.aspect_ratio = self.wing_span ** 2 / self.wing_area
        
        # Lift and drag coefficients (more realistic curves)
        self.cl_alpha = 0.11  # Lift curve slope (per degree)
        self.cd_0 = 0.015     # Zero-lift drag coefficient
        self.cd_induced_factor = 1 / (math.pi * self.aspect_ratio * 0.8)  # Oswald efficiency
        
        # Flight envelope
        self.stall_angle = math.radians(18)  # 18 degrees stall
        self.max_g_force = 6.0
        self.never_exceed_speed = 45  # m/s
        
        # Environmental simulation
        self.air_density = 1.225  # kg/m³
        self.temperature = 15.0   # °C
        self.pressure_altitude = 0
        
        # Advanced wind and turbulence
        self.wind_layers = self.create_wind_layers()
        self.thermal_map = self.generate_enhanced_thermal_map()
        self.turbulence_intensity = 0.0
        
        # Control system
        self.control_inputs = Vec3(0, 0, 0)  # pitch, yaw, roll
        self.control_authority = Vec3(8.0, 6.0, 10.0)  # Control power per axis
        self.control_damping = 0.85
        
        # Flight state tracking
        self.angle_of_attack = 0
        self.sideslip_angle = 0
        self.airspeed = 0
        self.ground_speed = 0
        self.climb_rate = 0
        self.g_force = 1.0
        
        # Performance tracking
        self.energy_altitude = 0  # Total energy expressed as altitude
        self.glide_performance = 0
        self.thermal_strength = 0
        
        print("🚁 Advanced Flight Physics initialized with realistic aerodynamics")
    
    def create_wind_layers(self):
        """Create realistic wind layers at different altitudes"""
        wind_layers = []
        
        # Surface layer (0-100m)
        wind_layers.append({
            'altitude_min': 0,
            'altitude_max': 100,
            'base_wind': Vec3(2, 0, 1),
            'turbulence': 0.3,
            'gusts': True
        })
        
        # Boundary layer (100-500m)
        wind_layers.append({
            'altitude_min': 100,
            'altitude_max': 500,
            'base_wind': Vec3(5, 0, 3),
            'turbulence': 0.2,
            'gusts': False
        })
        
        # Free atmosphere (500m+)
        wind_layers.append({
            'altitude_min': 500,
            'altitude_max': 2000,
            'base_wind': Vec3(8, 0, 4),
            'turbulence': 0.1,
            'gusts': False
        })
        
        return wind_layers
    
    def generate_enhanced_thermal_map(self):
        """Generate realistic thermal updraft map based on terrain"""
        thermal_map = {}
        
        # Thermals over heated areas (cities, south-facing slopes)
        thermal_locations = [
            # Strong thermals over urban areas
            (-45, 45, 8.0, 40),    # Downtown SF
            (-60, 60, 6.0, 30),    # Telegraph Hill
            (-40, 30, 7.0, 35),    # Nob Hill
            
            # Moderate thermals over open areas
            (0, 0, 5.0, 50),       # Twin Peaks area
            (20, -20, 4.5, 25),    # Open hills
            (-80, 80, 3.5, 20),    # Near water (weaker)
            
            # Weak thermals scattered around
            (30, 40, 3.0, 15),
            (-20, -40, 3.5, 18),
            (60, 0, 4.0, 22),
        ]
        
        for i, (x, z, strength, radius) in enumerate(thermal_locations):
            thermal_map[f'thermal_{i}'] = {
                'position': Vec3(x, 0, z),
                'strength': strength,
                'radius': radius,
                'core_radius': radius * 0.3,
                'height_max': strength * 15,  # Thermal top
                'turbulence': strength * 0.1,
                'time_variation': random.uniform(0, 2 * math.pi),
                'active': True
            }
        
        return thermal_map
    
    def get_air_density(self, altitude):
        """Calculate air density based on altitude (ISA atmosphere)"""
        # Standard atmosphere model (simplified)
        if altitude < 11000:  # Troposphere
            temperature_k = 288.15 - 0.0065 * altitude
            pressure_ratio = (temperature_k / 288.15) ** 5.256
            density = 1.225 * pressure_ratio * (288.15 / temperature_k)
        else:
            # Simplified for higher altitudes
            density = 1.225 * math.exp(-altitude / 8000)
        
        return max(0.1, density)  # Minimum density
    
    def get_wind_at_position(self, position):
        """Get wind vector at specific position and altitude"""
        altitude = position.y
        base_wind = Vec3(0, 0, 0)
        turbulence = 0
        
        # Find appropriate wind layer
        for layer in self.wind_layers:
            if layer['altitude_min'] <= altitude <= layer['altitude_max']:
                base_wind = layer['base_wind']
                turbulence = layer['turbulence']
                break
        
        # Add time-varying components
        time_factor = time.time() * 0.1
        wind_variation = Vec3(
            math.sin(time_factor * 0.8) * 1.5,
            0,
            math.cos(time_factor * 1.2) * 1.2
        )
        
        # Add turbulence
        if turbulence > 0:
            turb_x = random.uniform(-turbulence, turbulence) * 2
            turb_y = random.uniform(-turbulence * 0.5, turbulence * 0.5)
            turb_z = random.uniform(-turbulence, turbulence) * 2
            wind_variation += Vec3(turb_x, turb_y, turb_z)
        
        # Add terrain effects
        terrain_effect = self.get_terrain_wind_effect(position)
        
        return base_wind + wind_variation + terrain_effect
    
    def get_terrain_wind_effect(self, position):
        """Calculate wind effects from terrain (slope winds, channeling)"""
        terrain_wind = Vec3(0, 0, 0)
        
        # Simplified terrain wind effects
        # Valley channeling near Golden Gate
        if -100 < position.x < -60 and 100 < position.z < 140:
            # Channel wind through Golden Gate
            terrain_wind += Vec3(-2, 0, 1)
        
        # Slope winds on hills
        if position.y > 50:  # On hillsides
            # Upslope wind during day
            slope_factor = (position.y - 50) / 100
            terrain_wind += Vec3(0, slope_factor * 1.5, 0)
        
        return terrain_wind
    
    def get_thermal_effect(self, position):
        """Advanced thermal calculation with realistic behavior"""
        total_thermal = Vec3(0, 0, 0)
        max_thermal_strength = 0
        
        for thermal_id, thermal in self.thermal_map.items():
            if not thermal['active']:
                continue
            
            # Distance from thermal center
            distance = distance_2d(position, thermal['position'])
            
            if distance < thermal['radius']:
                # Height factor - thermals weaken with altitude
                height_factor = max(0, 1 - (position.y / thermal['height_max']))
                
                # Radial distance factor
                if distance < thermal['core_radius']:
                    # Strong core
                    radial_factor = 1.0
                else:
                    # Gradual falloff outside core
                    radial_factor = max(0, 1 - ((distance - thermal['core_radius']) / 
                                              (thermal['radius'] - thermal['core_radius'])))
                
                # Time variation for realistic thermal behavior
                time_var = math.sin(time.time() * 0.3 + thermal['time_variation']) * 0.3 + 0.7
                
                # Calculate thermal strength
                thermal_strength = thermal['strength'] * radial_factor * height_factor * time_var
                
                # Updraft component
                thermal_updraft = Vec3(0, thermal_strength, 0)
                
                # Add some realistic turbulence and circulation
                angle = math.atan2(position.z - thermal['position'].z, 
                                 position.x - thermal['position'].x)
                circulation_strength = thermal_strength * 0.2
                circulation = Vec3(
                    -math.sin(angle) * circulation_strength,
                    0,
                    math.cos(angle) * circulation_strength
                )
                
                # Add turbulence
                if thermal['turbulence'] > 0:
                    turbulence = Vec3(
                        random.uniform(-thermal['turbulence'], thermal['turbulence']),
                        random.uniform(-thermal['turbulence'] * 0.5, thermal['turbulence'] * 0.5),
                        random.uniform(-thermal['turbulence'], thermal['turbulence'])
                    )
                    thermal_updraft += turbulence
                
                total_thermal += thermal_updraft + circulation
                max_thermal_strength = max(max_thermal_strength, thermal_strength)
        
        self.thermal_strength = max_thermal_strength
        return total_thermal
    
    def calculate_aerodynamic_forces(self):
        """Advanced aerodynamic force calculation"""
        # Relative airspeed
        wind = self.get_wind_at_position(self.entity.position)
        relative_velocity = self.velocity - wind
        self.airspeed = distance(relative_velocity, Vec3(0, 0, 0))
        
        if self.airspeed < 0.5:
            return Vec3(0, 0, 0), Vec3(0, 0, 0)
        
        # Air density at current altitude
        air_density = self.get_air_density(self.entity.position.y)
        
        # Dynamic pressure
        q = 0.5 * air_density * self.airspeed ** 2
        
        # Angle of attack calculation (more sophisticated)
        if self.airspeed > 1.0:
            velocity_normalized = relative_velocity.normalized()
            
            # Body-fixed reference frame
            body_x = self.entity.forward
            body_y = self.entity.up
            body_z = self.entity.right
            
            # Angle of attack (angle between velocity and body x-axis)
            self.angle_of_attack = math.asin(max(-1, min(1, velocity_normalized.dot(body_y))))
            
            # Sideslip angle
            self.sideslip_angle = math.asin(max(-1, min(1, velocity_normalized.dot(body_z))))
        else:
            self.angle_of_attack = 0
            self.sideslip_angle = 0
        
        # Lift coefficient calculation with stall behavior
        aoa_deg = math.degrees(self.angle_of_attack)
        
        if abs(self.angle_of_attack) < self.stall_angle:
            # Linear region
            cl = self.cl_alpha * aoa_deg
        else:
            # Post-stall region with gradual loss
            stall_factor = math.cos(self.angle_of_attack * 2)
            cl = self.cl_alpha * math.degrees(self.stall_angle) * stall_factor
        
        # Drag coefficient with induced drag
        cd = self.cd_0 + self.cd_induced_factor * cl ** 2
        
        # Add compressibility effects at high speed
        mach_effect = min(1.2, 1 + (self.airspeed / 100) ** 2 * 0.1)
        cd *= mach_effect
        
        # Force magnitudes
        lift_magnitude = cl * q * self.wing_area
        drag_magnitude = cd * q * self.wing_area
        
        # Force directions in world coordinates
        if self.airspeed > 1.0:
            # Lift perpendicular to relative velocity, in plane of symmetry
            velocity_normalized = relative_velocity.normalized()
            lift_direction = self.entity.up - velocity_normalized * velocity_normalized.dot(self.entity.up)
            if distance(lift_direction, Vec3(0, 0, 0)) > 0:
                lift_direction = lift_direction.normalized()
            else:
                lift_direction = Vec3(0, 1, 0)
            
            # Drag opposite to relative velocity
            drag_direction = -velocity_normalized
        else:
            lift_direction = Vec3(0, 1, 0)
            drag_direction = Vec3(0, 0, 0)
        
        # Apply forces
        lift_force = lift_direction * lift_magnitude
        drag_force = drag_direction * drag_magnitude
        
        # Side force due to sideslip
        side_force_magnitude = 0.5 * q * self.wing_area * self.sideslip_angle * 2.0
        side_force = self.entity.right * side_force_magnitude
        
        total_aero_force = lift_force + drag_force + side_force
        
        # Aerodynamic moments
        # Pitching moment (stability)
        cm_alpha = -0.05  # Stable aircraft
        pitching_moment = cm_alpha * self.angle_of_attack * q * self.wing_area * 2.0
        
        # Rolling moment due to sideslip (dihedral effect)
        rolling_moment = -self.sideslip_angle * 0.1 * q * self.wing_area * self.wing_span
        
        # Yawing moment (weathercock stability)
        yawing_moment = self.sideslip_angle * 0.05 * q * self.wing_area * self.wing_span
        
        aero_moments = Vec3(pitching_moment, yawing_moment, rolling_moment)
        
        return total_aero_force, aero_moments
    
    def update(self, dt):
        """Advanced physics update with all effects"""
        # Reset accelerations
        self.acceleration = Vec3(0, 0, 0)
        self.angular_acceleration = Vec3(0, 0, 0)
        
        # Gravity
        gravity_force = Vec3(0, -9.81 * self.mass, 0)
        
        # Aerodynamic forces and moments
        aero_force, aero_moments = self.calculate_aerodynamic_forces()
        
        # Thermal and environmental effects
        thermal_force = self.get_thermal_effect(self.entity.position)
        environmental_force = thermal_force * self.mass
        
        # Control moments
        control_moments = Vec3(
            self.control_inputs.x * self.control_authority.x,
            self.control_inputs.y * self.control_authority.y,
            self.control_inputs.z * self.control_authority.z
        )
        
        # Total forces and moments
        total_force = gravity_force + aero_force + environmental_force
        total_moments = aero_moments + control_moments
        
        # Linear motion
        self.acceleration = total_force / self.mass
        self.velocity += self.acceleration * dt
        
        # Speed limiting for safety
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > self.never_exceed_speed:
            self.velocity = self.velocity.normalized() * self.never_exceed_speed
        
        # Angular motion
        self.angular_acceleration = Vec3(
            total_moments.x / self.moment_of_inertia.x,
            total_moments.y / self.moment_of_inertia.y,
            total_moments.z / self.moment_of_inertia.z
        )
        
        self.angular_velocity += self.angular_acceleration * dt
        
        # Angular damping
        self.angular_velocity *= self.control_damping
        
        # Update position and orientation
        self.entity.position += self.velocity * dt
        
        # Convert angular velocity to rotation (simplified)
        self.entity.rotation_x += math.degrees(self.angular_velocity.x) * dt
        self.entity.rotation_y += math.degrees(self.angular_velocity.y) * dt
        self.entity.rotation_z += math.degrees(self.angular_velocity.z) * dt
        
        # Calculate performance metrics
        self.ground_speed = distance(self.velocity, Vec3(0, 0, 0))
        self.climb_rate = self.velocity.y
        self.g_force = distance(self.acceleration, Vec3(0, 0, 0)) / 9.81
        
        # Energy calculations
        kinetic_energy = 0.5 * self.mass * self.ground_speed ** 2
        potential_energy = self.mass * 9.81 * self.entity.position.y
        total_energy = kinetic_energy + potential_energy
        self.energy_altitude = total_energy / (self.mass * 9.81)
        
        # Glide performance
        if abs(self.climb_rate) > 0.1:
            self.glide_performance = self.ground_speed / abs(self.climb_rate)
        else:
            self.glide_performance = 50  # Max displayed value
        
        return {
            'speed': self.ground_speed,
            'airspeed': self.airspeed,
            'altitude': self.entity.position.y,
            'climb_rate': self.climb_rate,
            'g_force': self.g_force,
            'angle_of_attack': math.degrees(self.angle_of_attack),
            'thermal_strength': self.thermal_strength,
            'energy_altitude': self.energy_altitude,
            'glide_ratio': self.glide_performance,
            'wind_speed': distance(self.get_wind_at_position(self.entity.position), Vec3(0, 0, 0))
        }
    
    def apply_control_input(self, pitch_input, yaw_input, roll_input, dt):
        """Apply pilot control inputs with realistic response"""
        # Control input filtering and rate limiting
        max_rate = 5.0  # Maximum control input rate
        
        self.control_inputs.x = max(-1, min(1, 
            self.control_inputs.x + (pitch_input - self.control_inputs.x) * max_rate * dt))
        self.control_inputs.y = max(-1, min(1, 
            self.control_inputs.y + (yaw_input - self.control_inputs.y) * max_rate * dt))
        self.control_inputs.z = max(-1, min(1, 
            self.control_inputs.z + (roll_input - self.control_inputs.z) * max_rate * dt))
        
        # Control effectiveness varies with airspeed
        airspeed_factor = min(1.0, self.airspeed / 8.0)
        self.control_inputs *= airspeed_factor

def distance_2d(pos1, pos2):
    """Calculate 2D distance between two positions"""
    return math.sqrt((pos1.x - pos2.x)**2 + (pos1.z - pos2.z)**2) 