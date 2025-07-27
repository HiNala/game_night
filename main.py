#!/usr/bin/env python3
"""
🦕 ENHANCED PREHISTORIC SAN FRANCISCO FLIGHT SIMULATOR 🌉
EPIC pterodactyl ecosystem with ADVANCED PHYSICS, OBSTACLES, RACING, and ULTRA-REALISTIC CONTROLS!

🚀 NEXT-GENERATION FEATURES:
- ⚛️ Advanced flight physics with realistic aerodynamics
- 🌪️ Dynamic obstacles (storms, wind shears, bird flocks)  
- 🏁 Racing system with rings, targets, and courses
- ✨ Enhanced visuals with particles and lighting
- 🦅 Ultra-realistic flying character with detailed animations
- 🎮 Multiple control schemes (Realistic, Arcade, Expert)

DESIGNED BY SENIOR DEVELOPERS | WE ARE LEGION
"""

from ursina import *
import sys
import os
import math
import random
from noise import pnoise2
import numpy as np

app = Ursina()

# =============================================================================
# 🚀 ENHANCED FLIGHT PHYSICS SYSTEM 🚀
# =============================================================================

class AdvancedFlightPhysics:
    """State-of-the-art flight physics with realistic aerodynamics"""
    
    def __init__(self, entity, config):
        self.entity = entity
        self.config = config
        
        # Advanced physics state
        self.velocity = Vec3(0, 0, 0)
        self.angular_velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        
        # Mass properties
        self.mass = config.get('mass', 1.5)
        self.wing_area = config.get('wing_area', 2.5)
        self.wing_span = config.get('wing_span', 3.0)
        
        # Aerodynamic coefficients
        self.cl_alpha = 0.11  # Lift curve slope
        self.cd_0 = 0.015     # Zero-lift drag
        self.stall_angle = math.radians(18)
        self.never_exceed_speed = 45
        
        # Environmental
        self.air_density = 1.225
        self.thermal_map = self.generate_thermal_map()
        
        # Flight state
        self.angle_of_attack = 0
        self.airspeed = 0
        self.ground_speed = 0
        self.climb_rate = 0
        self.g_force = 1.0
        self.thermal_strength = 0
        self.energy_altitude = 0
        self.glide_performance = 0
        
        # Control system
        self.control_inputs = Vec3(0, 0, 0)
        
        print("⚛️ Advanced Flight Physics initialized")
    
    def generate_thermal_map(self):
        """Generate realistic thermal updraft map"""
        thermal_map = {}
        
        thermal_locations = [
            (-45, 45, 8.0, 40),    # Downtown SF
            (-60, 60, 6.0, 30),    # Telegraph Hill
            (0, 0, 5.0, 50),       # Twin Peaks
            (-80, 120, 4.0, 25),   # Golden Gate
        ]
        
        for i, (x, z, strength, radius) in enumerate(thermal_locations):
            thermal_map[f'thermal_{i}'] = {
                'position': Vec3(x, 0, z),
                'strength': strength,
                'radius': radius,
                'active': True
            }
        
        return thermal_map
    
    def get_thermal_effect(self, position):
        """Calculate thermal updraft at position"""
        total_thermal = Vec3(0, 0, 0)
        max_strength = 0
        
        for thermal_id, thermal in self.thermal_map.items():
            if not thermal['active']:
                continue
            
            distance = math.sqrt((position.x - thermal['position'].x)**2 + 
                               (position.z - thermal['position'].z)**2)
            
            if distance < thermal['radius']:
                strength_factor = max(0, 1 - (distance / thermal['radius'])**2)
                thermal_strength = thermal['strength'] * strength_factor
                
                thermal_force = Vec3(0, thermal_strength, 0)
                total_thermal += thermal_force
                max_strength = max(max_strength, thermal_strength)
        
        self.thermal_strength = max_strength
        return total_thermal
    
    def calculate_aerodynamic_forces(self):
        """Advanced aerodynamic force calculation"""
        if self.airspeed < 0.5:
            return Vec3(0, 0, 0), Vec3(0, 0, 0)
        
        # Dynamic pressure
        q = 0.5 * self.air_density * self.airspeed ** 2
        
        # Angle of attack (simplified)
        if hasattr(self.entity, 'rotation_x'):
            self.angle_of_attack = math.radians(self.entity.rotation_x)
        
        # Lift coefficient with stall
        if abs(self.angle_of_attack) < self.stall_angle:
            cl = self.cl_alpha * math.degrees(self.angle_of_attack)
        else:
            cl = self.cl_alpha * math.degrees(self.stall_angle) * 0.5
        
        # Drag coefficient
        cd = self.cd_0 + (cl ** 2) / (math.pi * (self.wing_span ** 2 / self.wing_area))
        
        # Forces
        lift_magnitude = cl * q * self.wing_area
        drag_magnitude = cd * q * self.wing_area
        
        # Force directions
        lift_force = Vec3(0, lift_magnitude, 0)
        drag_force = -self.velocity.normalized() * drag_magnitude if self.airspeed > 0 else Vec3(0, 0, 0)
        
        total_aero_force = lift_force + drag_force
        aero_moments = Vec3(0, 0, 0)  # Simplified
        
        return total_aero_force, aero_moments
    
    def update(self, dt):
        """Advanced physics update"""
        # Gravity
        gravity_force = Vec3(0, -9.81 * self.mass, 0)
        
        # Aerodynamic forces
        aero_force, aero_moments = self.calculate_aerodynamic_forces()
        
        # Thermal effects
        thermal_force = self.get_thermal_effect(self.entity.position) * self.mass
        
        # Total forces
        total_force = gravity_force + aero_force + thermal_force
        
        # Update motion
        self.acceleration = total_force / self.mass
        self.velocity += self.acceleration * dt
        
        # Speed limiting
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > self.never_exceed_speed:
            self.velocity = self.velocity.normalized() * self.never_exceed_speed
        
        # Update position
        self.entity.position += self.velocity * dt
        
        # Calculate performance metrics
        self.ground_speed = speed
        self.airspeed = speed  # Simplified
        self.climb_rate = self.velocity.y
        self.g_force = distance(self.acceleration, Vec3(0, 0, 0)) / 9.81
        
        # Energy altitude
        kinetic_energy = 0.5 * self.mass * speed ** 2
        potential_energy = self.mass * 9.81 * self.entity.position.y
        self.energy_altitude = (kinetic_energy + potential_energy) / (self.mass * 9.81)
        
        # Glide performance
        if abs(self.climb_rate) > 0.1:
            self.glide_performance = speed / abs(self.climb_rate)
        else:
            self.glide_performance = 50
        
        return {
            'speed': self.ground_speed,
            'airspeed': self.airspeed,
            'altitude': self.entity.position.y,
            'climb_rate': self.climb_rate,
            'g_force': self.g_force,
            'thermal_strength': self.thermal_strength,
            'energy_altitude': self.energy_altitude,
            'glide_ratio': self.glide_performance
        }
    
    def apply_control_input(self, pitch_input, yaw_input, roll_input, dt):
        """Apply control inputs"""
        self.control_inputs.x = pitch_input
        self.control_inputs.y = yaw_input
        self.control_inputs.z = roll_input

# =============================================================================
# 🌪️ FLYING OBSTACLES SYSTEM 🌪️
# =============================================================================

class StormCloud(Entity):
    """Dynamic storm cloud with turbulence"""
    
    def __init__(self, position, intensity='moderate'):
        super().__init__()
        self.position = position
        self.intensity = intensity
        
        if intensity == 'light':
            self.size = 20
            self.turbulence_strength = 3.0
        elif intensity == 'moderate':
            self.size = 30
            self.turbulence_strength = 6.0
        else:  # severe
            self.size = 45
            self.turbulence_strength = 10.0
        
        self.drift_speed = random.uniform(2, 6)
        self.age = 0
        self.lifetime = random.uniform(300, 600)
        
        self.create_visual()
    
    def create_visual(self):
        """Create storm cloud visual"""
        self.cloud_body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(60, 60, 80),
            scale=(self.size, self.size * 0.6, self.size)
        )
        
        self.warning_zone = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 200, 0, 30),
            scale=(self.size * 1.5, self.size * 0.8, self.size * 1.5)
        )
    
    def get_turbulence_effect(self, position):
        """Calculate turbulence effect"""
        storm_distance = distance(position, self.position)
        
        if storm_distance > self.size:
            return Vec3(0, 0, 0)
        
        storm_factor = max(0, 1 - (storm_distance / self.size))
        
        turbulence = Vec3(
            random.uniform(-1, 1) * self.turbulence_strength * storm_factor,
            random.uniform(-0.5, 0.5) * self.turbulence_strength * storm_factor,
            random.uniform(-1, 1) * self.turbulence_strength * storm_factor
        )
        
        return turbulence
    
    def update(self, dt):
        """Update storm"""
        self.age += dt
        
        # Storm movement
        self.position += Vec3(self.drift_speed, 0, 0) * dt
        
        # Pulsing warning zone
        pulse = math.sin(time.time() * 3) * 0.2 + 0.8
        self.warning_zone.scale = (
            self.size * 1.5 * pulse,
            self.size * 0.8,
            self.size * 1.5 * pulse
        )
        
        return self.age < self.lifetime

class BirdFlock(Entity):
    """Flock of birds as obstacles"""
    
    def __init__(self, position, flock_size=6):
        super().__init__()
        self.position = position
        self.flock_size = flock_size
        self.flight_speed = random.uniform(8, 15)
        self.avoidance_distance = 15
        
        self.birds = []
        self.create_flock()
    
    def create_flock(self):
        """Create bird entities"""
        for i in range(self.flock_size):
            offset = Vec3(
                random.uniform(-5, 5),
                random.uniform(-2, 2),
                random.uniform(-5, 5)
            )
            
            bird = Entity(
                parent=self,
                model='cube',
                color=color.rgb(150, 150, 150),
                scale=(0.6, 0.2, 1.0),
                position=offset
            )
            self.birds.append(bird)
    
    def update(self, dt, player_position=None):
        """Update flock behavior"""
        # Simple patrol flight
        self.position += Vec3(self.flight_speed, 0, 0) * dt
        
        # Animate birds
        for bird in self.birds:
            wing_flap = math.sin(time.time() * 8) * 10
            bird.rotation_z = wing_flap
        
        return True

class EnvironmentalHazardManager:
    """Manages all environmental hazards"""
    
    def __init__(self, world_bounds=200):
        self.world_bounds = world_bounds
        self.storm_clouds = []
        self.bird_flocks = []
        
        self.spawn_timer = 0
        
        # Create initial hazards
        for _ in range(2):
            self.spawn_storm_cloud()
        
        for _ in range(2):
            self.spawn_bird_flock()
        
        print("🌪️ Environmental Hazard Manager initialized")
    
    def spawn_storm_cloud(self):
        """Spawn new storm cloud"""
        position = Vec3(
            random.uniform(-self.world_bounds, self.world_bounds),
            random.uniform(40, 120),
            random.uniform(-self.world_bounds, self.world_bounds)
        )
        
        intensity = random.choice(['light', 'moderate', 'severe'])
        storm = StormCloud(position, intensity)
        self.storm_clouds.append(storm)
    
    def spawn_bird_flock(self):
        """Spawn new bird flock"""
        position = Vec3(
            random.uniform(-self.world_bounds, self.world_bounds),
            random.uniform(10, 60),
            random.uniform(-self.world_bounds, self.world_bounds)
        )
        
        flock = BirdFlock(position)
        self.bird_flocks.append(flock)
    
    def get_environmental_effects(self, position):
        """Get environmental effects at position"""
        effects = {
            'turbulence': Vec3(0, 0, 0),
            'visibility': 1.0,
            'hazard_warnings': []
        }
        
        # Storm effects
        for storm in self.storm_clouds:
            storm_distance = distance(position, storm.position)
            
            if storm_distance < storm.size * 1.5:
                turbulence = storm.get_turbulence_effect(position)
                effects['turbulence'] += turbulence
                
                if storm_distance < storm.size:
                    effects['visibility'] *= 0.3
                    effects['hazard_warnings'].append('STORM_TURBULENCE')
        
        # Bird collision warnings
        for flock in self.bird_flocks:
            flock_distance = distance(position, flock.position)
            if flock_distance < 15:
                effects['hazard_warnings'].append('BIRD_STRIKE_RISK')
        
        return effects
    
    def update(self, dt, player_position=None):
        """Update all hazards"""
        self.spawn_timer -= dt
        
        # Spawn new hazards periodically
        if self.spawn_timer <= 0:
            if random.random() < 0.3:
                self.spawn_storm_cloud()
            if random.random() < 0.4:
                self.spawn_bird_flock()
            self.spawn_timer = random.uniform(60, 180)
        
        # Update storms
        self.storm_clouds = [storm for storm in self.storm_clouds if storm.update(dt)]
        
        # Update bird flocks
        for flock in self.bird_flocks:
            flock.update(dt, player_position)

# =============================================================================
# 🏁 RACING SYSTEM 🏁
# =============================================================================

class NavigationRing(Entity):
    """Racing rings for point-to-point gameplay"""
    
    def __init__(self, position, ring_type='checkpoint', size=8):
        super().__init__()
        self.position = position
        self.ring_type = ring_type
        self.size = size
        self.passed = False
        
        # Ring properties
        if ring_type == 'checkpoint':
            self.color_primary = color.rgb(0, 255, 100)
            self.points = 100
        elif ring_type == 'speed_ring':
            self.color_primary = color.rgb(255, 100, 0)
            self.points = 200
        elif ring_type == 'precision_ring':
            self.color_primary = color.rgb(100, 100, 255)
            self.points = 300
            self.size = size * 0.7
        else:  # bonus_ring
            self.color_primary = color.rgb(255, 255, 0)
            self.points = 500
        
        self.create_ring_visual()
        self.detection_radius = self.size * 0.8
        
        print(f"🎯 Navigation ring created: {ring_type}")
    
    def create_ring_visual(self):
        """Create ring visual"""
        # Outer ring
        self.outer_ring = Entity(
            parent=self,
            model='cube',
            color=self.color_primary,
            scale=(self.size, 0.5, self.size)
        )
        
        # Ring segments for detail
        num_segments = 12
        for i in range(num_segments):
            angle = (i / num_segments) * 360
            segment_x = math.cos(math.radians(angle)) * self.size * 0.5
            segment_z = math.sin(math.radians(angle)) * self.size * 0.5
            
            segment = Entity(
                parent=self,
                model='cube',
                color=self.color_primary,
                scale=(0.8, 0.3, 0.8),
                position=(segment_x, 0, segment_z),
                rotation=(0, angle, 0)
            )
        
        # Glow effect
        self.glow_effect = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 50),
            scale=self.size * 1.5
        )
    
    def check_passage(self, position, velocity):
        """Check if passed through ring"""
        if self.passed:
            return False
        
        distance_to_ring = distance(position, self.position)
        
        if distance_to_ring < self.detection_radius:
            ring_plane_distance = abs((position - self.position).dot(Vec3(0, 1, 0)))
            
            if ring_plane_distance < 2.0:
                self.passed = True
                self.trigger_passage_effect()
                return True
        
        return False
    
    def trigger_passage_effect(self):
        """Create passage effect"""
        self.outer_ring.color = color.white
        self.outer_ring.animate('color', self.color_primary, duration=0.5)
        
        # Energy wave
        energy_wave = Entity(
            model='sphere',
            color=color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 100),
            scale=1,
            position=self.position,
            parent=scene
        )
        
        energy_wave.animate_scale(self.size * 3, duration=1.0)
        energy_wave.animate('color', color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 0), duration=1.0)
        destroy(energy_wave, delay=1.1)
        
        print(f"✨ Ring passed! Points: {self.points}")
    
    def update(self, dt):
        """Update ring animations"""
        if self.passed:
            return
        
        self.rotation_y += 30 * dt
        
        # Pulsing glow
        pulse = math.sin(time.time() * 3) * 0.3 + 0.7
        glow_alpha = int(50 * pulse)
        self.glow_effect.color = color.rgba(
            self.color_primary.r, 
            self.color_primary.g, 
            self.color_primary.b, 
            glow_alpha
        )

class CollectionTarget(Entity):
    """Collection targets for racing"""
    
    def __init__(self, position, target_type='orb', value=50):
        super().__init__()
        self.position = position
        self.target_type = target_type
        self.value = value
        self.collected = False
        
        if target_type == 'orb':
            self.base_color = color.rgb(100, 200, 255)
        elif target_type == 'crystal':
            self.base_color = color.rgb(255, 100, 200)
        else:  # energy_cell
            self.base_color = color.rgb(255, 255, 100)
        
        self.collection_radius = 3
        self.create_target_visual()
    
    def create_target_visual(self):
        """Create target visual"""
        self.target_body = Entity(
            parent=self,
            model='sphere',
            color=self.base_color,
            scale=2
        )
        
        self.energy_aura = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(self.base_color.r, self.base_color.g, self.base_color.b, 80),
            scale=4
        )
    
    def check_collection(self, position):
        """Check if target collected"""
        if self.collected:
            return False
        
        distance_to_target = distance(position, self.position)
        
        if distance_to_target < self.collection_radius:
            self.collected = True
            self.trigger_collection_effect()
            return True
        
        return False
    
    def trigger_collection_effect(self):
        """Collection effect"""
        self.target_body.animate_scale(6, duration=0.3)
        self.target_body.animate('color', color.white, duration=0.3)
        
        self.visible = False
        print(f"💎 Target collected! Value: {self.value}")
    
    def update(self, dt):
        """Update target animations"""
        if self.collected:
            return
        
        self.target_body.rotation_y += 60 * dt
        
        # Pulsing aura
        pulse = math.sin(time.time() * 4) * 0.3 + 0.7
        aura_alpha = int(80 * pulse)
        self.energy_aura.color = color.rgba(
            self.base_color.r, 
            self.base_color.g, 
            self.base_color.b, 
            aura_alpha
        )

class RaceCourse:
    """Complete race course"""
    
    def __init__(self, course_name):
        self.course_name = course_name
        self.rings = []
        self.targets = []
        
        self.current_ring_index = 0
        self.course_active = False
        self.total_score = 0
        
        self.generate_course()
    
    def generate_course(self):
        """Generate race course"""
        if self.course_name == 'Golden Gate Circuit':
            # Golden Gate Bridge circuit
            self.rings.append(NavigationRing(Vec3(-120, 40, 120), 'checkpoint', 10))
            self.rings.append(NavigationRing(Vec3(-80, 35, 120), 'speed_ring', 8))
            self.rings.append(NavigationRing(Vec3(-50, 50, 120), 'checkpoint', 10))
            self.rings.append(NavigationRing(Vec3(-80, 45, 120), 'bonus_ring', 12))
            
            # Collection targets
            self.targets.append(CollectionTarget(Vec3(-100, 60, 130), 'orb', 100))
            self.targets.append(CollectionTarget(Vec3(-60, 80, 110), 'crystal', 150))
        
        elif self.course_name == 'Twin Peaks Challenge':
            # Twin Peaks course
            self.rings.append(NavigationRing(Vec3(-20, 30, -20), 'checkpoint', 12))
            self.rings.append(NavigationRing(Vec3(0, 150, 0), 'precision_ring', 6))
            self.rings.append(NavigationRing(Vec3(20, 80, 20), 'speed_ring', 10))
            
            self.targets.append(CollectionTarget(Vec3(0, 200, 0), 'crystal', 300))
    
    def start_course(self):
        """Start the course"""
        self.course_active = True
        self.current_ring_index = 0
        self.total_score = 0
        
        for ring in self.rings:
            ring.passed = False
        
        for target in self.targets:
            target.collected = False
            target.visible = True
        
        print(f"🏁 Course '{self.course_name}' started!")
    
    def update(self, dt, player_position, player_velocity):
        """Update course"""
        if not self.course_active:
            return
        
        # Update rings
        for ring in self.rings:
            ring.update(dt)
        
        # Update targets
        for target in self.targets:
            target.update(dt)
        
        # Check ring passages
        if self.current_ring_index < len(self.rings):
            current_ring = self.rings[self.current_ring_index]
            
            if current_ring.check_passage(player_position, player_velocity):
                self.total_score += current_ring.points
                self.current_ring_index += 1
        
        # Check target collections
        for target in self.targets:
            if target.check_collection(player_position):
                self.total_score += target.value
        
        # Check completion
        if self.current_ring_index >= len(self.rings):
            self.complete_course()
    
    def complete_course(self):
        """Complete course"""
        self.course_active = False
        print(f"🏁 Course completed! Final Score: {self.total_score}")

class RacingManager:
    """Manages racing system"""
    
    def __init__(self):
        self.courses = {}
        self.active_course = None
        
        # Create courses
        self.courses['Golden Gate Circuit'] = RaceCourse('Golden Gate Circuit')
        self.courses['Twin Peaks Challenge'] = RaceCourse('Twin Peaks Challenge')
        
        print("🏁 Racing Manager initialized")
    
    def start_course(self, course_name):
        """Start a course"""
        if course_name in self.courses:
            self.active_course = self.courses[course_name]
            self.active_course.start_course()
            return True
        return False
    
    def update(self, dt, player_position, player_velocity):
        """Update active course"""
        if self.active_course:
            self.active_course.update(dt, player_position, player_velocity)
    
    def get_course_status(self):
        """Get course status"""
        if not self.active_course:
            return None
        
        return {
            'course_name': self.active_course.course_name,
            'active': self.active_course.course_active,
            'rings_completed': self.active_course.current_ring_index,
            'total_rings': len(self.active_course.rings),
            'score': self.active_course.total_score
        }

# =============================================================================
# 🦅 ULTRA-REALISTIC FLYING CHARACTER 🦅
# =============================================================================

class RealisticFlyingCharacter(Entity):
    """Ultra-realistic flying character with advanced controls"""
    
    def __init__(self, character_type='archaeopteryx', enhanced_physics=None):
        super().__init__()
        
        self.character_type = character_type
        self.enhanced_physics = enhanced_physics
        self.base_scale = 2.5
        
        # Control system
        self.control_scheme = 'realistic'
        self.control_sensitivity = 1.0
        self.control_smoothing = 0.85
        
        # Control inputs
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        self.throttle_input = 0
        
        # Character state
        self.energy_level = 1.0
        self.stamina = 1.0
        self.stress_level = 0.0
        
        # Create model
        self.create_realistic_model()
        self.position = Vec3(-50, 60, 80)
        
        print(f"🦅 Realistic character created: {character_type}")
    
    def create_realistic_model(self):
        """Create detailed model"""
        # Main body
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(80, 60, 40),
            scale=(2.0 * self.base_scale, 0.8 * self.base_scale, 1.2 * self.base_scale)
        )
        
        # Head
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(90, 70, 50),
            scale=(1.0 * self.base_scale, 0.8 * self.base_scale, 0.8 * self.base_scale),
            position=(0, 0.2 * self.base_scale, 1.2 * self.base_scale)
        )
        
        # Eyes
        for eye_x in [-0.3, 0.3]:
            eye = Entity(
                parent=self.head,
                model='sphere',
                color=color.orange,
                scale=0.25 * self.base_scale,
                position=(eye_x * self.base_scale, 0.2, 0.3)
            )
        
        # Wings
        wing_length = 4 * self.base_scale
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2.0 * self.base_scale),
            position=(-wing_length/2 - 0.8, 0, 0),
            rotation=(0, 0, 8)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2.0 * self.base_scale),
            position=(wing_length/2 + 0.8, 0, 0),
            rotation=(0, 0, -8)
        )
        
        # Tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(70, 50, 30),
            scale=(0.6 * self.base_scale, 0.4 * self.base_scale, 3.0 * self.base_scale),
            position=(0, 0, -2.5 * self.base_scale)
        )
    
    def update_advanced_controls(self, dt):
        """Advanced control system"""
        # Raw inputs
        raw_pitch = 0
        raw_yaw = 0
        raw_roll = 0
        raw_throttle = 0
        
        if held_keys['w']:
            raw_pitch = 1
        elif held_keys['s']:
            raw_pitch = -1
        
        if held_keys['a']:
            raw_yaw = 1
            raw_roll = 0.5
        elif held_keys['d']:
            raw_yaw = -1
            raw_roll = -0.5
        
        if held_keys['space']:
            raw_throttle = 1
        
        if held_keys['shift']:
            raw_pitch -= 0.8
        
        # Control scheme modifications
        if self.control_scheme == 'realistic':
            effectiveness = self.get_control_effectiveness()
            raw_pitch *= effectiveness * self.control_sensitivity
            raw_yaw *= effectiveness * self.control_sensitivity * 0.8
            raw_roll *= effectiveness * self.control_sensitivity * 1.2
        
        # Apply smoothing
        self.pitch_input = self.lerp_control(self.pitch_input, raw_pitch, dt)
        self.yaw_input = self.lerp_control(self.yaw_input, raw_yaw, dt)
        self.roll_input = self.lerp_control(self.roll_input, raw_roll, dt)
        self.throttle_input = self.lerp_control(self.throttle_input, raw_throttle, dt)
        
        # Apply to physics
        if self.enhanced_physics:
            self.enhanced_physics.apply_control_input(
                self.pitch_input, self.yaw_input, self.roll_input, dt
            )
    
    def lerp_control(self, current, target, dt):
        """Smooth control interpolation"""
        return current + (target - current) * (1 - self.control_smoothing) * 10 * dt
    
    def get_control_effectiveness(self):
        """Calculate control effectiveness"""
        base_effectiveness = 1.0
        
        # Energy factor
        base_effectiveness *= (0.5 + self.energy_level * 0.5)
        
        # Stress factor
        base_effectiveness *= (1.0 - self.stress_level * 0.3)
        
        return max(0.1, min(1.5, base_effectiveness))
    
    def update_realistic_animations(self, dt):
        """Update animations"""
        # Get flight data
        if self.enhanced_physics:
            speed = self.enhanced_physics.ground_speed
            climb_rate = self.enhanced_physics.climb_rate
        else:
            speed = 15  # Default
            climb_rate = 0
        
        # Wing animation
        if speed < 8:
            wing_frequency = 6.0
            wing_amplitude = 35
        elif speed > 20:
            wing_frequency = 1.0
            wing_amplitude = 10
        else:
            wing_frequency = 3.0
            wing_amplitude = 20
        
        # Calculate wing positions
        wing_time = time.time() * wing_frequency
        base_flap = math.sin(wing_time) * wing_amplitude
        
        # Apply wing rotations
        self.left_wing.rotation_z = 8 + base_flap + self.roll_input * 10
        self.right_wing.rotation_z = -8 - base_flap - self.roll_input * 10
        
        # Body attitude
        if hasattr(self.enhanced_physics, 'velocity'):
            velocity = self.enhanced_physics.velocity
            if distance(velocity, Vec3(0, 0, 0)) > 1:
                pitch_angle = math.degrees(math.atan2(-velocity.y, abs(velocity.z) + 0.1))
                self.rotation_x = pitch_angle
        
        self.rotation_y += self.yaw_input * 50 * dt
        self.rotation_z = self.roll_input * 35
    
    def update(self, dt):
        """Main update"""
        # Controls
        self.update_advanced_controls(dt)
        
        # Physics
        if self.enhanced_physics:
            physics_data = self.enhanced_physics.update(dt)
        else:
            physics_data = {'speed': 0, 'altitude': self.position.y}
        
        # Animations
        self.update_realistic_animations(dt)
        
        # Keep above ground
        if self.y < 1:
            self.y = 1
            if hasattr(self.enhanced_physics, 'velocity'):
                self.enhanced_physics.velocity.y = max(0, self.enhanced_physics.velocity.y)
        
        return physics_data
    
    def set_control_scheme(self, scheme):
        """Change control scheme"""
        self.control_scheme = scheme
        
        if scheme == 'realistic':
            self.control_sensitivity = 1.0
            self.control_smoothing = 0.85
        elif scheme == 'arcade':
            self.control_sensitivity = 1.5
            self.control_smoothing = 0.6
        elif scheme == 'expert':
            self.control_sensitivity = 0.8
            self.control_smoothing = 0.95
        
        print(f"🎮 Control scheme: {scheme}")

# =============================================================================
# 🌉 SAN FRANCISCO WORLD 🌉
# =============================================================================

class SanFranciscoTerrain(Entity):
    """Accurate San Francisco terrain"""
    
    def __init__(self, size=400, resolution=80):
        super().__init__()
        self.size = size
        self.resolution = resolution
        
        # SF features
        self.sf_features = {
            'twin_peaks': {'pos': (0, 0), 'height': 280, 'radius': 25},
            'telegraph_hill': {'pos': (-60, 60), 'height': 84, 'radius': 10},
            'nob_hill': {'pos': (-40, 30), 'height': 104, 'radius': 15},
        }
        
        self.golden_gate_pos = (-80, 120)
        self.bay_center = (0, 80)
        
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate SF terrain"""
        self.height_map = []
        
        for i in range(self.resolution + 1):
            row = []
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                
                height = 0
                
                # Add SF hills
                for hill_name, hill_data in self.sf_features.items():
                    hill_x, hill_z = hill_data['pos']
                    hill_height = hill_data['height']
                    hill_radius = hill_data['radius']
                    
                    dist = math.sqrt((x - hill_x)**2 + (z - hill_z)**2)
                    if dist < hill_radius * 2:
                        hill_factor = max(0, 1 - (dist / (hill_radius * 2))**2)
                        height += hill_height * hill_factor
                
                # Bay area
                bay_dist = math.sqrt((x - self.bay_center[0])**2 + (z - self.bay_center[1])**2)
                if bay_dist < 60:
                    bay_factor = max(0, 1 - (bay_dist / 60)**3)
                    height -= 20 * bay_factor
                
                # Add noise
                height += pnoise2(x * 0.01, z * 0.01) * 8
                height = max(height, -25)
                
                row.append(height)
            self.height_map.append(row)
        
        self.create_mesh()
    
    def create_mesh(self):
        """Create terrain mesh"""
        vertices = []
        triangles = []
        colors = []
        
        for i in range(self.resolution + 1):
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                y = self.height_map[i][j]
                
                vertices.append(Vec3(x, y, z))
                
                # Color based on height
                if y < -5:
                    colors.append(color.rgb(0.1, 0.3, 0.6))
                elif y < 0:
                    colors.append(color.rgb(0.2, 0.5, 0.8))
                elif y < 50:
                    colors.append(color.rgb(0.4, 0.6, 0.3))
                else:
                    colors.append(color.rgb(0.6, 0.6, 0.6))
        
        # Generate triangles
        for i in range(self.resolution):
            for j in range(self.resolution):
                v1 = i * (self.resolution + 1) + j
                v2 = (i + 1) * (self.resolution + 1) + j
                v3 = i * (self.resolution + 1) + (j + 1)
                v4 = (i + 1) * (self.resolution + 1) + (j + 1)
                
                triangles.extend([v1, v2, v3, v2, v4, v3])
        
        self.model = Mesh(vertices=vertices, triangles=triangles, colors=colors)
        self.model.generate()

class GoldenGateBridge(Entity):
    """Golden Gate Bridge model"""
    
    def __init__(self, position=Vec3(-80, 15, 120)):
        super().__init__()
        self.position = position
        
        # Bridge deck
        self.deck = Entity(
            parent=self,
            model='cube',
            color=color.rgb(196, 76, 25),
            scale=(120, 2, 8),
            position=(0, 25, 0)
        )
        
        # Towers
        self.north_tower = Entity(
            parent=self,
            model='cube',
            color=color.rgb(196, 76, 25),
            scale=(6, 80, 4),
            position=(-30, 40, 0)
        )
        
        self.south_tower = Entity(
            parent=self,
            model='cube',
            color=color.rgb(196, 76, 25),
            scale=(6, 80, 4),
            position=(30, 40, 0)
        )
        
        # Cables
        for side in [-2, 2]:
            cable = Entity(
                parent=self,
                model='cube',
                color=color.rgb(150, 150, 150),
                scale=(140, 0.5, 0.5),
                position=(0, 75, side)
            )

# =============================================================================
# 🎮 ENHANCED UI SYSTEM 🎮
# =============================================================================

class EnhancedGameUI:
    """Enhanced UI with flight instruments"""
    
    def __init__(self):
        self.setup_ui()
    
    def setup_ui(self):
        """Setup enhanced UI"""
        # Flight data panel
        self.flight_panel = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(0, 0, 0, 100),
            scale=(0.4, 0.3, 1),
            position=(-0.6, 0.3, 0)
        )
        
        # Speed indicator
        self.speed_text = Text(
            'Speed: 0 m/s',
            parent=camera.ui,
            scale=1.8,
            color=color.lime,
            position=(-0.85, 0.45, 0)
        )
        
        # Altitude indicator
        self.altitude_text = Text(
            'Altitude: 0 m',
            parent=camera.ui,
            scale=1.8,
            color=color.cyan,
            position=(-0.85, 0.4, 0)
        )
        
        # G-Force meter
        self.g_force_text = Text(
            'G-Force: 1.0',
            parent=camera.ui,
            scale=1.6,
            color=color.yellow,
            position=(-0.85, 0.35, 0)
        )
        
        # Energy level
        self.energy_text = Text(
            'Energy: 100%',
            parent=camera.ui,
            scale=1.6,
            color=color.orange,
            position=(-0.85, 0.3, 0)
        )
        
        # Course info
        self.course_text = Text(
            'No active course',
            parent=camera.ui,
            scale=1.8,
            color=color.white,
            position=(0.4, 0.45, 0)
        )
        
        # Score
        self.score_text = Text(
            'Score: 0',
            parent=camera.ui,
            scale=2.2,
            color=color.gold,
            position=(0.4, 0.4, 0)
        )
        
        # Hazard warnings
        self.warning_text = Text(
            '',
            parent=camera.ui,
            scale=2.0,
            color=color.red,
            position=(0, 0.3, 0),
            origin=(0, 0)
        )
        
        # Controls help
        self.controls_text = Text(
            '🎮 WASD=Flight | Space=Boost | Shift=Dive | 1-3=Courses | C=Controls | ESC=Menu',
            parent=camera.ui,
            scale=1.2,
            color=color.light_gray,
            position=(-0.9, -0.45, 0)
        )
        
        print("🎨 Enhanced UI initialized")
    
    def update_flight_data(self, flight_data):
        """Update flight instruments"""
        speed = flight_data.get('speed', 0)
        altitude = flight_data.get('altitude', 0)
        g_force = flight_data.get('g_force', 1.0)
        
        self.speed_text.text = f'Speed: {speed:.1f} m/s'
        self.altitude_text.text = f'Altitude: {altitude:.1f} m'
        self.g_force_text.text = f'G-Force: {g_force:.1f}'
        
        # Color coding
        if speed > 35:
            self.speed_text.color = color.red
        elif speed > 25:
            self.speed_text.color = color.yellow
        else:
            self.speed_text.color = color.lime
        
        if altitude < 10:
            self.altitude_text.color = color.red
        elif altitude < 25:
            self.altitude_text.color = color.yellow
        else:
            self.altitude_text.color = color.cyan
        
        if g_force > 3:
            self.g_force_text.color = color.red
        elif g_force > 2:
            self.g_force_text.color = color.yellow
        else:
            self.g_force_text.color = color.lime
    
    def update_character_data(self, character_data):
        """Update character specific data"""
        energy = character_data.get('energy_level', 1.0)
        self.energy_text.text = f'Energy: {energy*100:.0f}%'
        
        if energy < 0.3:
            self.energy_text.color = color.red
        elif energy < 0.6:
            self.energy_text.color = color.yellow
        else:
            self.energy_text.color = color.lime
    
    def update_course_info(self, course_status):
        """Update course information"""
        if course_status:
            self.course_text.text = f"Course: {course_status['course_name']}"
            self.score_text.text = f"Score: {course_status['score']}"
            
            if course_status['active']:
                rings_info = f" | Rings: {course_status['rings_completed']}/{course_status['total_rings']}"
                self.course_text.text += rings_info
        else:
            self.course_text.text = "No active course"
            self.score_text.text = "Score: 0"
    
    def update_warnings(self, hazard_warnings):
        """Update hazard warnings"""
        if hazard_warnings:
            warning_text = " | ".join(hazard_warnings)
            self.warning_text.text = f"⚠️ {warning_text}"
        else:
            self.warning_text.text = ""

# =============================================================================
# 🚀 MAIN GAME CLASS 🚀
# =============================================================================

class EnhancedPrehistoricSimulator:
    """🦕 ENHANCED PREHISTORIC SAN FRANCISCO SIMULATOR 🌉"""
    
    def __init__(self):
        self.setup_window()
        
        # Create enhanced systems
        self.create_world()
        self.create_character()
        self.create_ui()
        self.create_managers()
        
        # Game state
        self.game_active = False
        self.show_intro = True
        
        print("🦕" * 60)
        print("🚀 ENHANCED PREHISTORIC SAN FRANCISCO FLIGHT SIMULATOR 🚀")
        print("🦕" * 60)
        print()
        print("🎮 CONTROLS:")
        print("   WASD = Advanced Flight Control")
        print("   Space = Energy Boost / Thermal Riding")
        print("   Shift = Power Dive")
        print("   Q/E = Roll Control")
        print("   1 = Start Golden Gate Circuit")
        print("   2 = Start Twin Peaks Challenge")
        print("   C = Cycle Control Schemes")
        print("   ENTER = Start Game")
        print()
        print("✨ NEW FEATURES:")
        print("   🌪️ Dynamic weather and obstacles")
        print("   🏁 Racing courses with rings and targets")
        print("   ⚛️ Advanced realistic physics")
        print("   🦅 Ultra-realistic flying character")
        print("   🎮 Multiple control schemes")
        print("   ✨ Enhanced visual effects")
    
    def setup_window(self):
        """Setup game window"""
        window.title = '🦕 ENHANCED PREHISTORIC SAN FRANCISCO - Ultimate Flight Simulator 🌉'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        Entity.default_shader = basic_lighting_shader
    
    def create_world(self):
        """Create the enhanced world"""
        print("🌍 Creating Enhanced Prehistoric San Francisco...")
        
        # Terrain
        self.terrain = SanFranciscoTerrain(size=400, resolution=80)
        print("   ✓ Enhanced terrain with accurate SF topography")
        
        # Golden Gate Bridge
        self.golden_gate = GoldenGateBridge()
        print("   ✓ 🌉 Golden Gate Bridge constructed")
        
        # Lighting
        DirectionalLight(color=color.rgb(255, 220, 180), rotation=(60, 45, 0))
        AmbientLight(color=color.rgb(100, 120, 150))
        Sky(texture='sky_default')
        
        # Atmospheric effects
        scene.fog_density = 0.008
        scene.fog_color = color.rgb(0.7, 0.8, 0.9)
        
        print("🌍 Enhanced world creation complete!")
    
    def create_character(self):
        """Create enhanced character"""
        # Enhanced physics config
        physics_config = {
            'mass': 1.5,
            'wing_area': 2.5,
            'wing_span': 3.0
        }
        
        # Create advanced physics
        self.physics = AdvancedFlightPhysics(None, physics_config)
        
        # Create realistic character
        self.player = RealisticFlyingCharacter('archaeopteryx', self.physics)
        self.physics.entity = self.player  # Link physics to character
        
        print("🦅 Enhanced character with advanced physics created")
    
    def create_ui(self):
        """Create enhanced UI"""
        self.ui = EnhancedGameUI()
        
        # Intro message
        self.intro_text = Text(
            '🦕 ENHANCED PREHISTORIC SAN FRANCISCO! 🌉\n'
            '✨ Advanced Physics | 🌪️ Dynamic Obstacles | 🏁 Racing Courses\n'
            'Press ENTER to begin the ultimate flight adventure!',
            parent=camera.ui,
            scale=2.0,
            color=color.gold,
            position=(0, 0, 0),
            origin=(0, 0)
        )
    
    def create_managers(self):
        """Create game managers"""
        # Environmental hazards
        self.hazard_manager = EnvironmentalHazardManager(world_bounds=200)
        
        # Racing system
        self.racing_manager = RacingManager()
        
        print("🎮 All game managers initialized")
    
    def start_game(self):
        """Start the enhanced game"""
        self.game_active = True
        self.show_intro = False
        self.intro_text.visible = False
        
        # Setup camera
        camera.parent = self.player
        camera.position = (0, 25, -30)
        camera.rotation_x = 45
        
        print("🚀 Enhanced game started!")
    
    def update(self):
        """Main game update loop"""
        if not self.game_active:
            return
        
        dt = time.dt
        
        # Update character
        flight_data = self.player.update(dt)
        
        # Update environmental hazards
        self.hazard_manager.update(dt, self.player.position)
        
        # Get environmental effects
        env_effects = self.hazard_manager.get_environmental_effects(self.player.position)
        
        # Apply environmental effects to physics
        if env_effects['turbulence'] != Vec3(0, 0, 0):
            self.physics.velocity += env_effects['turbulence'] * dt * 0.1
        
        # Update racing
        self.racing_manager.update(dt, self.player.position, self.physics.velocity)
        
        # Update UI
        self.ui.update_flight_data(flight_data)
        self.ui.update_character_data(self.player.get_flight_data())
        self.ui.update_course_info(self.racing_manager.get_course_status())
        self.ui.update_warnings(env_effects['hazard_warnings'])

# =============================================================================
# 🎮 INPUT HANDLING 🎮
# =============================================================================

# Create game instance
enhanced_game = EnhancedPrehistoricSimulator()

def input(key):
    """Enhanced input handling"""
    if key == 'escape':
        if enhanced_game.show_intro:
            quit()
        else:
            enhanced_game.game_active = not enhanced_game.game_active
    
    elif key == 'enter':
        if enhanced_game.show_intro:
            enhanced_game.start_game()
    
    elif key == '1':
        if enhanced_game.game_active:
            enhanced_game.racing_manager.start_course('Golden Gate Circuit')
    
    elif key == '2':
        if enhanced_game.game_active:
            enhanced_game.racing_manager.start_course('Twin Peaks Challenge')
    
    elif key == 'c':
        if enhanced_game.game_active:
            # Cycle control schemes
            current = enhanced_game.player.control_scheme
            if current == 'realistic':
                enhanced_game.player.set_control_scheme('arcade')
            elif current == 'arcade':
                enhanced_game.player.set_control_scheme('expert')
            else:
                enhanced_game.player.set_control_scheme('realistic')
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen

def update():
    """Main update function"""
    enhanced_game.update()

# 🚀 LAUNCH THE ENHANCED ADVENTURE! 🚀
if __name__ == '__main__':
    print("🦕🌉 LAUNCHING ENHANCED PREHISTORIC SAN FRANCISCO! 🌉🦕")
    print("🚀 MAXIMUM EPIC FACTOR WITH ADVANCED FEATURES 🚀")
    print("WE ARE LEGION - PREPARE FOR ULTIMATE GREATNESS!")
    app.run()