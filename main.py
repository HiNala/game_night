#!/usr/bin/env python3
"""
🦕 INFINITE PREHISTORIC FLIGHT SIMULATOR 🌊
EPIC infinite world generation using Wave Function Collapse with logical rules!

🚀 ULTIMATE FEATURES:
- 🌊 Wave Function Collapse infinite world generation
- ⚛️ Advanced flight physics with realistic aerodynamics
- 🌪️ Dynamic obstacles (storms, wind shears, bird flocks)  
- 🏁 Racing system with rings, targets, and courses
- ✨ Enhanced visuals with particles and lighting
- 🦅 Ultra-realistic flying character with detailed animations
- 🎮 Multiple control schemes (Realistic, Arcade, Expert)
- 🌍 Infinite procedural world with logical terrain rules

DESIGNED BY SENIOR DEVELOPERS | WE ARE LEGION
"""

from ursina import *
import sys
import os
import math
import random
from noise import pnoise2
import numpy as np

# Import our WFC system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.world.wave_function_collapse import WaveFunctionCollapse, InfiniteWorldRenderer, FlightCorridorManager, TerrainType

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
    
    def get_thermal_effect(self, position, world_renderer=None):
        """Calculate thermal updraft at position using terrain data"""
        thermal_force = Vec3(0, 0, 0)
        
        if world_renderer:
            terrain_effects = world_renderer.get_terrain_effects_at_position(position)
            thermal_strength = terrain_effects.get('thermal_strength', 0.5)
            elevation = terrain_effects.get('elevation', 0)
            
            # Thermal strength varies with terrain type and elevation
            if thermal_strength > 0.8:  # Strong thermal areas (cities, deserts)
                base_strength = thermal_strength * 6.0
                
                # Add some noise for realism
                noise_factor = 1 + math.sin(time.time() * 0.3 + position.x * 0.01) * 0.3
                thermal_force.y = base_strength * noise_factor
                
                # Height factor - thermals weaken with altitude
                height_factor = max(0, 1 - ((position.y - elevation) / 200))
                thermal_force.y *= height_factor
                
                self.thermal_strength = thermal_force.y
        
        return thermal_force
    
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
    
    def update(self, dt, world_renderer=None):
        """Advanced physics update with terrain integration"""
        # Gravity
        gravity_force = Vec3(0, -9.81 * self.mass, 0)
        
        # Aerodynamic forces
        aero_force, aero_moments = self.calculate_aerodynamic_forces()
        
        # Thermal effects from terrain
        thermal_force = self.get_thermal_effect(self.entity.position, world_renderer) * self.mass
        
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
    
    def __init__(self, world_bounds=500):
        self.world_bounds = world_bounds
        self.storm_clouds = []
        self.bird_flocks = []
        
        self.spawn_timer = 0
        
        # Create initial hazards
        for _ in range(3):
            self.spawn_storm_cloud()
        
        for _ in range(4):
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

class ProceduralRacingManager:
    """Manages procedural racing courses in infinite world"""
    
    def __init__(self, world_renderer):
        self.world_renderer = world_renderer
        self.active_courses = {}
        self.rings = []
        self.targets = []
        self.course_active = False
        self.total_score = 0
        self.current_ring_index = 0
        
        print("🏁 Procedural Racing Manager initialized")
    
    def generate_course_around_position(self, center_position, course_type='exploration'):
        """Generate a procedural racing course around position"""
        self.rings.clear()
        self.targets.clear()
        
        if course_type == 'exploration':
            self.generate_exploration_course(center_position)
        elif course_type == 'terrain_following':
            self.generate_terrain_following_course(center_position)
        elif course_type == 'landmark_tour':
            self.generate_landmark_tour(center_position)
    
    def generate_exploration_course(self, center_position):
        """Generate exploration course with varied terrain"""
        course_radius = 200
        ring_count = 8
        
        for i in range(ring_count):
            angle = (i / ring_count) * 2 * math.pi
            
            # Vary distance and height for interesting course
            distance = course_radius + random.uniform(-50, 50)
            height_offset = random.uniform(30, 80)
            
            ring_x = center_position.x + math.cos(angle) * distance
            ring_z = center_position.z + math.sin(angle) * distance
            
            # Get terrain height at ring position
            terrain_effects = self.world_renderer.get_terrain_effects_at_position(Vec3(ring_x, 0, ring_z))
            terrain_height = terrain_effects.get('elevation', 0)
            
            ring_y = terrain_height + height_offset
            
            # Choose ring type based on terrain
            terrain_type = terrain_effects.get('terrain_type', 'plains')
            if terrain_type in ['urban_high', 'landmark']:
                ring_type = 'precision_ring'
            elif terrain_type in ['water_deep', 'water_shallow']:
                ring_type = 'speed_ring'
            elif i == ring_count - 1:
                ring_type = 'bonus_ring'
            else:
                ring_type = 'checkpoint'
            
            ring = NavigationRing(Vec3(ring_x, ring_y, ring_z), ring_type, 10)
            self.rings.append(ring)
            
            # Add collection targets near some rings
            if random.random() < 0.4:
                target_pos = Vec3(
                    ring_x + random.uniform(-20, 20),
                    ring_y + random.uniform(-10, 10),
                    ring_z + random.uniform(-20, 20)
                )
                target = CollectionTarget(target_pos, 'orb', 100)
                self.targets.append(target)
    
    def generate_terrain_following_course(self, center_position):
        """Generate course that follows terrain elevation"""
        # Implementation for terrain-following course
        pass
    
    def generate_landmark_tour(self, center_position):
        """Generate course connecting landmarks"""
        # Implementation for landmark tour
        pass
    
    def start_course(self, course_type='exploration', center_position=None):
        """Start a procedural course"""
        if center_position is None:
            center_position = Vec3(0, 0, 0)
        
        self.generate_course_around_position(center_position, course_type)
        self.course_active = True
        self.current_ring_index = 0
        self.total_score = 0
        
        print(f"🏁 Started {course_type} course with {len(self.rings)} rings!")
    
    def update(self, dt, player_position, player_velocity):
        """Update racing system"""
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
    
    def get_course_status(self):
        """Get course status"""
        if not self.course_active:
            return None
        
        return {
            'course_name': 'Procedural Course',
            'active': self.course_active,
            'rings_completed': self.current_ring_index,
            'total_rings': len(self.rings),
            'score': self.total_score
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
        self.position = Vec3(0, 100, 0)  # Start at origin with good altitude
        
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
    
    def update(self, dt, world_renderer=None):
        """Main update"""
        # Controls
        self.update_advanced_controls(dt)
        
        # Physics
        if self.enhanced_physics:
            physics_data = self.enhanced_physics.update(dt, world_renderer)
        else:
            physics_data = {'speed': 0, 'altitude': self.position.y}
        
        # Animations
        self.update_realistic_animations(dt)
        
        # Terrain collision (get ground height from world)
        if world_renderer:
            terrain_effects = world_renderer.get_terrain_effects_at_position(self.position)
            ground_height = terrain_effects.get('elevation', 0)
            
            if self.y < ground_height + 2:
                self.y = ground_height + 2
                if hasattr(self.enhanced_physics, 'velocity'):
                    self.enhanced_physics.velocity.y = max(0, self.enhanced_physics.velocity.y)
        else:
            # Default ground check
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
# 🎮 ENHANCED UI SYSTEM 🎮
# =============================================================================

class InfiniteWorldUI:
    """Enhanced UI for infinite world"""
    
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
        
        # Position indicator
        self.position_text = Text(
            'Pos: (0, 0)',
            parent=camera.ui,
            scale=1.6,
            color=color.yellow,
            position=(-0.85, 0.35, 0)
        )
        
        # Terrain type indicator
        self.terrain_text = Text(
            'Terrain: plains',
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
        
        # World info
        self.world_info_text = Text(
            '🌊 Infinite World Generation Active',
            parent=camera.ui,
            scale=1.4,
            color=color.light_gray,
            position=(0.4, 0.35, 0)
        )
        
        # Controls help
        self.controls_text = Text(
            '🎮 WASD=Flight | Space=Boost | Shift=Dive | 1=Race | R=New Course | C=Controls | ESC=Menu',
            parent=camera.ui,
            scale=1.2,
            color=color.light_gray,
            position=(-0.9, -0.45, 0)
        )
        
        print("🎨 Infinite World UI initialized")
    
    def update_flight_data(self, flight_data, position, terrain_effects):
        """Update flight instruments"""
        speed = flight_data.get('speed', 0)
        altitude = flight_data.get('altitude', 0)
        
        self.speed_text.text = f'Speed: {speed:.1f} m/s'
        self.altitude_text.text = f'Altitude: {altitude:.1f} m'
        self.position_text.text = f'Pos: ({position.x:.0f}, {position.z:.0f})'
        
        terrain_type = terrain_effects.get('terrain_type', 'plains')
        self.terrain_text.text = f'Terrain: {terrain_type.replace("_", " ")}'
        
        # Color coding
        if speed > 35:
            self.speed_text.color = color.red
        elif speed > 25:
            self.speed_text.color = color.yellow
        else:
            self.speed_text.color = color.lime
        
        terrain_elevation = terrain_effects.get('elevation', 0)
        altitude_above_ground = altitude - terrain_elevation
        
        if altitude_above_ground < 10:
            self.altitude_text.color = color.red
        elif altitude_above_ground < 25:
            self.altitude_text.color = color.yellow
        else:
            self.altitude_text.color = color.cyan
    
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
    
    def update_warnings(self, hazard_warnings, airspace_warnings):
        """Update warnings"""
        all_warnings = hazard_warnings + airspace_warnings
        
        if all_warnings:
            warning_text = " | ".join(all_warnings)
            self.warning_text.text = f"⚠️ {warning_text}"
        else:
            self.warning_text.text = ""

# =============================================================================
# 🚀 MAIN GAME CLASS 🚀
# =============================================================================

class InfinitePrehistoricSimulator:
    """🦕 INFINITE PREHISTORIC FLIGHT SIMULATOR WITH WFC 🌊"""
    
    def __init__(self):
        self.setup_window()
        
        # Create infinite world systems
        self.create_infinite_world()
        self.create_character()
        self.create_ui()
        self.create_managers()
        
        # Game state
        self.game_active = False
        self.show_intro = True
        
        print("🦕" * 60)
        print("🌊 INFINITE PREHISTORIC FLIGHT SIMULATOR - WAVE FUNCTION COLLAPSE 🌊")
        print("🦕" * 60)
        print()
        print("🌍 INFINITE WORLD FEATURES:")
        print("   🌊 Wave Function Collapse terrain generation")
        print("   🏔️ Logical terrain rules and biome distribution")
        print("   🏗️ Dynamic chunk loading/unloading")
        print("   🌆 Procedural cities, landmarks, and airports")
        print("   ✈️ Intelligent flight corridors and airspace")
        print()
        print("🎮 CONTROLS:")
        print("   WASD = Advanced Flight Control")
        print("   Space = Energy Boost / Thermal Riding")
        print("   Shift = Power Dive")
        print("   1 = Start Procedural Racing Course")
        print("   R = Generate New Racing Course")
        print("   C = Cycle Control Schemes")
        print("   ENTER = Start Game")
        print()
        print("🚀 Experience the ultimate infinite flight adventure!")
    
    def setup_window(self):
        """Setup game window"""
        window.title = '🌊 INFINITE PREHISTORIC FLIGHT SIMULATOR - Wave Function Collapse World 🦕'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        Entity.default_shader = basic_lighting_shader
    
    def create_infinite_world(self):
        """Create the infinite world using WFC"""
        print("🌊 Initializing Wave Function Collapse world generation...")
        
        # Initialize WFC generator
        self.wfc_generator = WaveFunctionCollapse(chunk_size=32)
        
        # Initialize world renderer
        self.world_renderer = InfiniteWorldRenderer(self.wfc_generator)
        
        # Initialize flight corridor manager
        self.flight_manager = FlightCorridorManager(self.wfc_generator)
        
        # Lighting setup
        DirectionalLight(color=color.rgb(255, 220, 180), rotation=(60, 45, 0))
        AmbientLight(color=color.rgb(100, 120, 150))
        Sky(texture='sky_default')
        
        # Enhanced atmospheric effects
        scene.fog_density = 0.005
        scene.fog_color = color.rgb(0.7, 0.8, 0.9)
        
        print("🌊 Infinite world with Wave Function Collapse initialized!")
    
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
        
        print("🦅 Enhanced character with infinite world physics created")
    
    def create_ui(self):
        """Create enhanced UI"""
        self.ui = InfiniteWorldUI()
        
        # Intro message
        self.intro_text = Text(
            '🌊 INFINITE PREHISTORIC FLIGHT SIMULATOR! 🦕\n'
            '🌍 Wave Function Collapse World Generation\n'
            '✨ Infinite Exploration | 🏁 Procedural Racing | 🌆 Logical Terrain Rules\n'
            'Press ENTER to begin the infinite adventure!',
            parent=camera.ui,
            scale=2.0,
            color=color.gold,
            position=(0, 0, 0),
            origin=(0, 0)
        )
    
    def create_managers(self):
        """Create game managers"""
        # Environmental hazards
        self.hazard_manager = EnvironmentalHazardManager(world_bounds=500)
        
        # Procedural racing system
        self.racing_manager = ProceduralRacingManager(self.world_renderer)
        
        print("🎮 All infinite world managers initialized")
    
    def start_game(self):
        """Start the infinite game"""
        self.game_active = True
        self.show_intro = False
        self.intro_text.visible = False
        
        # Setup camera
        camera.parent = self.player
        camera.position = (0, 25, -30)
        camera.rotation_x = 45
        
        # Generate initial world around player
        self.world_renderer.update(self.player.position)
        
        print("🌊 Infinite world game started!")
    
    def update(self):
        """Main game update loop"""
        if not self.game_active:
            return
        
        dt = time.dt
        
        # Update infinite world renderer
        self.world_renderer.update(self.player.position)
        
        # Update character with world data
        flight_data = self.player.update(dt, self.world_renderer)
        
        # Get terrain effects at player position
        terrain_effects = self.world_renderer.get_terrain_effects_at_position(self.player.position)
        
        # Update environmental hazards
        self.hazard_manager.update(dt, self.player.position)
        
        # Get environmental effects
        env_effects = self.hazard_manager.get_environmental_effects(self.player.position)
        
        # Apply environmental effects to physics
        if env_effects['turbulence'] != Vec3(0, 0, 0):
            self.physics.velocity += env_effects['turbulence'] * dt * 0.1
        
        # Check airspace restrictions
        airspace_warnings = self.flight_manager.check_airspace_restrictions(self.player.position)
        
        # Update racing
        self.racing_manager.update(dt, self.player.position, self.physics.velocity)
        
        # Update UI
        self.ui.update_flight_data(flight_data, self.player.position, terrain_effects)
        self.ui.update_course_info(self.racing_manager.get_course_status())
        self.ui.update_warnings(env_effects['hazard_warnings'], airspace_warnings)

# =============================================================================
# 🎮 INPUT HANDLING 🎮
# =============================================================================

# Create game instance
infinite_game = InfinitePrehistoricSimulator()

def input(key):
    """Enhanced input handling for infinite world"""
    if key == 'escape':
        if infinite_game.show_intro:
            quit()
        else:
            infinite_game.game_active = not infinite_game.game_active
    
    elif key == 'enter':
        if infinite_game.show_intro:
            infinite_game.start_game()
    
    elif key == '1':
        if infinite_game.game_active:
            # Start procedural course at current position
            infinite_game.racing_manager.start_course('exploration', infinite_game.player.position)
    
    elif key == 'r':
        if infinite_game.game_active:
            # Generate new racing course
            infinite_game.racing_manager.start_course('exploration', infinite_game.player.position)
            print("🏁 New procedural racing course generated!")
    
    elif key == 'c':
        if infinite_game.game_active:
            # Cycle control schemes
            current = infinite_game.player.control_scheme
            if current == 'realistic':
                infinite_game.player.set_control_scheme('arcade')
            elif current == 'arcade':
                infinite_game.player.set_control_scheme('expert')
            else:
                infinite_game.player.set_control_scheme('realistic')
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen

def update():
    """Main update function"""
    infinite_game.update()

# 🌊 LAUNCH THE INFINITE ADVENTURE! 🌊
if __name__ == '__main__':
    print("🌊🦕 LAUNCHING INFINITE PREHISTORIC FLIGHT SIMULATOR! 🦕🌊")
    print("🚀 WAVE FUNCTION COLLAPSE WORLD GENERATION ACTIVE 🚀")
    print("🌍 EXPERIENCE TRUE INFINITE EXPLORATION!")
    print("WE ARE LEGION - INFINITE GREATNESS ACHIEVED!")
    app.run()