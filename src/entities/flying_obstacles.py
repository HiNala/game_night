"""
🌪️ DYNAMIC FLYING OBSTACLES & CHALLENGES 🌪️
Advanced AI-driven obstacles and environmental hazards for epic gameplay.
"""

import math
import random
from ursina import *

class StormCloud(Entity):
    """Dynamic storm cloud with turbulence and lightning"""
    
    def __init__(self, position, intensity='moderate'):
        super().__init__()
        self.position = position
        self.intensity = intensity
        
        # Storm properties
        if intensity == 'light':
            self.size = random.uniform(15, 25)
            self.turbulence_strength = 3.0
            self.lightning_chance = 0.01
        elif intensity == 'moderate':
            self.size = random.uniform(25, 40)
            self.turbulence_strength = 6.0
            self.lightning_chance = 0.03
        else:  # severe
            self.size = random.uniform(40, 60)
            self.turbulence_strength = 10.0
            self.lightning_chance = 0.05
        
        # Movement properties
        self.drift_speed = random.uniform(2, 8)
        self.drift_direction = random.uniform(0, 360)
        self.vertical_movement = random.uniform(0.5, 2.0)
        
        # Visual components
        self.create_storm_visual()
        
        # Internal state
        self.lightning_timer = 0
        self.turbulence_zones = self.create_turbulence_zones()
        self.age = 0
        self.lifetime = random.uniform(300, 600)  # 5-10 minutes
        
        print(f"⛈️ Storm cloud created: {intensity} intensity at {position}")
    
    def create_storm_visual(self):
        """Create visual representation of storm cloud"""
        # Main cloud body
        self.cloud_body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(60, 60, 80),
            scale=(self.size, self.size * 0.6, self.size),
            position=(0, 0, 0)
        )
        
        # Cloud layers for depth
        for i in range(3):
            layer_scale = (1 - i * 0.2)
            layer = Entity(
                parent=self,
                model='cube',
                color=color.rgba(80 - i*10, 80 - i*10, 100 - i*5, 150 - i*30),
                scale=(self.size * layer_scale, self.size * 0.4, self.size * layer_scale),
                position=(0, i * 2, 0)
            )
        
        # Storm indicators
        self.lightning_effect = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(255, 255, 200, 0),
            scale=self.size * 1.2,
            visible=False
        )
        
        # Warning zone indicator
        self.warning_zone = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 200, 0, 30),
            scale=(self.size * 1.5, self.size * 0.8, self.size * 1.5),
            position=(0, -self.size * 0.3, 0)
        )
    
    def create_turbulence_zones(self):
        """Create turbulence zones within storm"""
        zones = []
        num_zones = int(self.size / 8)  # More zones for larger storms
        
        for _ in range(num_zones):
            zone = {
                'position': Vec3(
                    random.uniform(-self.size/2, self.size/2),
                    random.uniform(-self.size/3, self.size/3),
                    random.uniform(-self.size/2, self.size/2)
                ),
                'radius': random.uniform(3, 8),
                'strength': random.uniform(0.5, 1.0) * self.turbulence_strength,
                'rotation_speed': random.uniform(30, 120)
            }
            zones.append(zone)
        
        return zones
    
    def get_turbulence_effect(self, position):
        """Calculate turbulence effect on aircraft at position"""
        storm_relative_pos = position - self.position
        
        # Check if inside storm
        if distance(storm_relative_pos, Vec3(0, 0, 0)) > self.size:
            return Vec3(0, 0, 0)
        
        total_turbulence = Vec3(0, 0, 0)
        
        # Base storm turbulence
        storm_distance = distance(storm_relative_pos, Vec3(0, 0, 0))
        storm_factor = max(0, 1 - (storm_distance / self.size))
        
        base_turbulence = Vec3(
            random.uniform(-1, 1) * self.turbulence_strength * storm_factor,
            random.uniform(-0.5, 0.5) * self.turbulence_strength * storm_factor,
            random.uniform(-1, 1) * self.turbulence_strength * storm_factor
        )
        total_turbulence += base_turbulence
        
        # Turbulence from specific zones
        for zone in self.turbulence_zones:
            zone_pos = self.position + zone['position']
            zone_distance = distance(position, zone_pos)
            
            if zone_distance < zone['radius']:
                zone_factor = max(0, 1 - (zone_distance / zone['radius']))
                
                # Rotational turbulence
                angle = math.atan2(position.z - zone_pos.z, position.x - zone_pos.x)
                rotation_angle = angle + math.radians(zone['rotation_speed'] * time.time())
                
                zone_turbulence = Vec3(
                    math.cos(rotation_angle) * zone['strength'] * zone_factor,
                    random.uniform(-0.3, 0.3) * zone['strength'] * zone_factor,
                    math.sin(rotation_angle) * zone['strength'] * zone_factor
                )
                total_turbulence += zone_turbulence
        
        return total_turbulence
    
    def update(self, dt):
        """Update storm cloud behavior"""
        self.age += dt
        
        # Storm movement
        drift_rad = math.radians(self.drift_direction)
        drift_velocity = Vec3(
            math.cos(drift_rad) * self.drift_speed,
            math.sin(time.time() * 0.1) * self.vertical_movement,
            math.sin(drift_rad) * self.drift_speed
        )
        self.position += drift_velocity * dt
        
        # Lightning effects
        self.lightning_timer -= dt
        if self.lightning_timer <= 0 and random.random() < self.lightning_chance:
            self.trigger_lightning()
            self.lightning_timer = random.uniform(5, 20)
        
        # Storm evolution
        life_factor = self.age / self.lifetime
        if life_factor > 0.8:
            # Storm weakening
            self.turbulence_strength *= 0.999
            alpha = max(0, 1 - (life_factor - 0.8) * 5)
            self.cloud_body.color = color.rgba(60, 60, 80, int(255 * alpha))
        
        # Update visual effects
        self.update_visual_effects()
        
        return self.age < self.lifetime  # Return False when storm should be removed
    
    def trigger_lightning(self):
        """Create lightning effect"""
        self.lightning_effect.visible = True
        self.lightning_effect.color = color.rgba(255, 255, 200, 200)
        
        # Lightning flash animation
        self.lightning_effect.animate('color', color.rgba(255, 255, 200, 0), duration=0.3)
        invoke(setattr, self.lightning_effect, 'visible', False, delay=0.3)
        
        print("⚡ Lightning strike!")
    
    def update_visual_effects(self):
        """Update cloud visual effects"""
        # Pulsing warning zone
        pulse = math.sin(time.time() * 3) * 0.2 + 0.8
        self.warning_zone.scale = (
            self.size * 1.5 * pulse,
            self.size * 0.8,
            self.size * 1.5 * pulse
        )

class WindShear(Entity):
    """Invisible wind shear zone that affects flight"""
    
    def __init__(self, position, direction, strength, width=20, height=10):
        super().__init__()
        self.position = position
        self.direction = math.radians(direction)  # Wind direction in radians
        self.strength = strength  # Wind speed in m/s
        self.width = width
        self.height = height
        self.length = width  # Shear zone is roughly square
        
        # Movement properties
        self.drift_speed = random.uniform(1, 3)
        self.drift_direction = random.uniform(0, 360)
        
        # Create subtle visual indicator
        self.create_visual_indicator()
        
        print(f"💨 Wind shear created: {strength} m/s at {position}")
    
    def create_visual_indicator(self):
        """Create subtle visual indicator for wind shear"""
        # Very faint visual indicator - particles
        self.particles = []
        for _ in range(10):
            particle = Entity(
                parent=self,
                model='cube',
                color=color.rgba(200, 200, 255, 30),
                scale=0.2,
                position=(
                    random.uniform(-self.width/2, self.width/2),
                    random.uniform(-self.height/2, self.height/2),
                    random.uniform(-self.length/2, self.length/2)
                )
            )
            particle.velocity = Vec3(
                math.cos(self.direction) * self.strength * 0.1,
                0,
                math.sin(self.direction) * self.strength * 0.1
            )
            self.particles.append(particle)
    
    def get_wind_effect(self, position):
        """Calculate wind effect on aircraft"""
        relative_pos = position - self.position
        
        # Check if inside wind shear zone
        if (abs(relative_pos.x) > self.width/2 or 
            abs(relative_pos.y) > self.height/2 or
            abs(relative_pos.z) > self.length/2):
            return Vec3(0, 0, 0)
        
        # Calculate wind vector
        wind_x = math.cos(self.direction) * self.strength
        wind_z = math.sin(self.direction) * self.strength
        
        # Add some vertical component for realism
        wind_y = math.sin(time.time() * 2 + relative_pos.x * 0.1) * self.strength * 0.2
        
        return Vec3(wind_x, wind_y, wind_z)
    
    def update(self, dt):
        """Update wind shear"""
        # Gradual movement
        drift_rad = math.radians(self.drift_direction)
        drift_velocity = Vec3(
            math.cos(drift_rad) * self.drift_speed,
            0,
            math.sin(drift_rad) * self.drift_speed
        )
        self.position += drift_velocity * dt
        
        # Update particle positions
        for particle in self.particles:
            particle.position += particle.velocity * dt
            
            # Reset particles that drift too far
            if distance(particle.position, Vec3(0, 0, 0)) > max(self.width, self.length):
                particle.position = Vec3(
                    random.uniform(-self.width/2, self.width/2),
                    random.uniform(-self.height/2, self.height/2),
                    random.uniform(-self.length/2, self.length/2)
                )
        
        return True  # Wind shears persist

class BirdFlock(Entity):
    """Flock of birds that can pose collision hazard"""
    
    def __init__(self, position, flock_size=8, bird_type='seagull'):
        super().__init__()
        self.position = position
        self.flock_size = flock_size
        self.bird_type = bird_type
        
        # Flock properties
        self.leader_position = position.copy()
        self.formation_pattern = 'v_formation'  # or 'cluster', 'line'
        self.flight_speed = random.uniform(8, 15)
        self.flight_direction = random.uniform(0, 360)
        self.altitude_preference = position.y
        
        # Behavior state
        self.behavior_mode = 'patrol'  # patrol, fleeing, feeding
        self.avoidance_distance = 15  # Distance to avoid player
        self.danger_distance = 8     # Distance that triggers evasive action
        
        # Create flock
        self.birds = self.create_flock()
        
        print(f"🐦 Bird flock created: {flock_size} {bird_type}s at {position}")
    
    def create_flock(self):
        """Create individual birds in formation"""
        birds = []
        
        for i in range(self.flock_size):
            # Calculate formation position
            if self.formation_pattern == 'v_formation':
                if i == 0:
                    # Leader
                    offset = Vec3(0, 0, 0)
                else:
                    # V formation
                    side = 1 if i % 2 == 1 else -1
                    row = (i + 1) // 2
                    offset = Vec3(side * row * 3, -row * 0.5, -row * 4)
            else:
                # Random cluster
                offset = Vec3(
                    random.uniform(-5, 5),
                    random.uniform(-2, 2),
                    random.uniform(-5, 5)
                )
            
            bird = Entity(
                parent=self,
                model='cube',
                color=color.rgb(150, 150, 150) if self.bird_type == 'seagull' else color.rgb(80, 60, 40),
                scale=(0.8, 0.3, 1.2),
                position=offset
            )
            
            # Bird wings
            left_wing = Entity(
                parent=bird,
                model='cube',
                color=bird.color,
                scale=(1.5, 0.1, 0.6),
                position=(-0.8, 0, 0),
                rotation=(0, 0, 15)
            )
            
            right_wing = Entity(
                parent=bird,
                model='cube',
                color=bird.color,
                scale=(1.5, 0.1, 0.6),
                position=(0.8, 0, 0),
                rotation=(0, 0, -15)
            )
            
            bird.left_wing = left_wing
            bird.right_wing = right_wing
            bird.wing_beat_time = random.uniform(0, 2 * math.pi)
            bird.formation_offset = offset
            
            birds.append(bird)
        
        return birds
    
    def update_behavior(self, player_position):
        """Update flock behavior based on player proximity"""
        distance_to_player = distance(self.position, player_position)
        
        if distance_to_player < self.danger_distance:
            self.behavior_mode = 'emergency_evasion'
        elif distance_to_player < self.avoidance_distance:
            self.behavior_mode = 'avoidance'
        else:
            self.behavior_mode = 'patrol'
    
    def update(self, dt, player_position=None):
        """Update flock movement and behavior"""
        if player_position:
            self.update_behavior(player_position)
        
        # Update leader position based on behavior
        if self.behavior_mode == 'patrol':
            # Normal patrol flight
            direction_rad = math.radians(self.flight_direction)
            patrol_velocity = Vec3(
                math.cos(direction_rad) * self.flight_speed,
                math.sin(time.time() * 0.2) * 2,  # Gentle altitude changes
                math.sin(direction_rad) * self.flight_speed
            )
            self.leader_position += patrol_velocity * dt
            
            # Occasionally change direction
            if random.random() < 0.01:
                self.flight_direction += random.uniform(-30, 30)
        
        elif self.behavior_mode == 'avoidance':
            # Gentle avoidance maneuver
            if player_position:
                avoidance_vector = (self.position - player_position).normalized()
                avoidance_velocity = avoidance_vector * self.flight_speed * 1.5
                self.leader_position += avoidance_velocity * dt
        
        elif self.behavior_mode == 'emergency_evasion':
            # Rapid evasive action
            if player_position:
                evasion_vector = (self.position - player_position).normalized()
                # Add random component for scatter
                random_component = Vec3(
                    random.uniform(-1, 1),
                    random.uniform(0.5, 1.5),  # Prefer upward evasion
                    random.uniform(-1, 1)
                ).normalized()
                
                evasion_velocity = (evasion_vector + random_component * 0.5) * self.flight_speed * 2.5
                self.leader_position += evasion_velocity * dt
        
        # Update main position
        self.position = self.leader_position
        
        # Update individual bird positions and animations
        for i, bird in enumerate(self.birds):
            # Formation keeping with some lag
            target_position = self.leader_position + bird.formation_offset
            current_pos = self.position + bird.position
            
            # Smooth movement toward formation position
            bird.position = lerp(bird.position, bird.formation_offset, 2 * dt)
            
            # Wing flapping animation
            bird.wing_beat_time += dt * 8  # Wing beat frequency
            wing_flap = math.sin(bird.wing_beat_time) * 20
            
            bird.left_wing.rotation_z = 15 + wing_flap
            bird.right_wing.rotation_z = -15 - wing_flap
            
            # Bank turns
            if self.behavior_mode != 'patrol':
                bank_angle = 20 if self.behavior_mode == 'emergency_evasion' else 10
                bird.rotation_z = bank_angle * (1 if random.random() > 0.5 else -1)
            else:
                bird.rotation_z = lerp(bird.rotation_z, 0, 3 * dt)
        
        return True  # Flocks persist

class EnvironmentalHazardManager:
    """Manages all environmental hazards and obstacles"""
    
    def __init__(self, world_bounds):
        self.world_bounds = world_bounds
        self.storm_clouds = []
        self.wind_shears = []
        self.bird_flocks = []
        
        # Hazard spawning parameters
        self.max_storms = 3
        self.max_wind_shears = 5
        self.max_bird_flocks = 4
        
        # Spawn timers
        self.storm_spawn_timer = 0
        self.wind_spawn_timer = 0
        self.bird_spawn_timer = 0
        
        self.initialize_hazards()
        print("🌪️ Environmental Hazard Manager initialized")
    
    def initialize_hazards(self):
        """Create initial set of hazards"""
        # Initial storm clouds
        for _ in range(2):
            self.spawn_storm_cloud()
        
        # Initial wind shears
        for _ in range(3):
            self.spawn_wind_shear()
        
        # Initial bird flocks
        for _ in range(2):
            self.spawn_bird_flock()
    
    def spawn_storm_cloud(self):
        """Spawn a new storm cloud"""
        if len(self.storm_clouds) >= self.max_storms:
            return
        
        position = Vec3(
            random.uniform(-self.world_bounds, self.world_bounds),
            random.uniform(40, 120),
            random.uniform(-self.world_bounds, self.world_bounds)
        )
        
        intensity = random.choice(['light', 'moderate', 'severe'])
        storm = StormCloud(position, intensity)
        self.storm_clouds.append(storm)
    
    def spawn_wind_shear(self):
        """Spawn a new wind shear zone"""
        if len(self.wind_shears) >= self.max_wind_shears:
            return
        
        position = Vec3(
            random.uniform(-self.world_bounds, self.world_bounds),
            random.uniform(20, 80),
            random.uniform(-self.world_bounds, self.world_bounds)
        )
        
        direction = random.uniform(0, 360)
        strength = random.uniform(5, 20)
        wind_shear = WindShear(position, direction, strength)
        self.wind_shears.append(wind_shear)
    
    def spawn_bird_flock(self):
        """Spawn a new bird flock"""
        if len(self.bird_flocks) >= self.max_bird_flocks:
            return
        
        position = Vec3(
            random.uniform(-self.world_bounds, self.world_bounds),
            random.uniform(10, 60),
            random.uniform(-self.world_bounds, self.world_bounds)
        )
        
        flock_size = random.randint(4, 12)
        bird_type = random.choice(['seagull', 'crow', 'hawk'])
        flock = BirdFlock(position, flock_size, bird_type)
        self.bird_flocks.append(flock)
    
    def get_environmental_effects(self, position):
        """Get all environmental effects at a position"""
        effects = {
            'turbulence': Vec3(0, 0, 0),
            'wind': Vec3(0, 0, 0),
            'visibility': 1.0,
            'hazard_warnings': []
        }
        
        # Storm effects
        for storm in self.storm_clouds:
            storm_distance = distance(position, storm.position)
            
            if storm_distance < storm.size * 1.5:
                # Inside or near storm
                turbulence = storm.get_turbulence_effect(position)
                effects['turbulence'] += turbulence
                
                if storm_distance < storm.size:
                    effects['visibility'] *= 0.3  # Poor visibility in storm
                    effects['hazard_warnings'].append('STORM_TURBULENCE')
                elif storm_distance < storm.size * 1.2:
                    effects['hazard_warnings'].append('STORM_WARNING')
        
        # Wind shear effects
        for wind_shear in self.wind_shears:
            wind_effect = wind_shear.get_wind_effect(position)
            effects['wind'] += wind_effect
            
            if distance(wind_effect, Vec3(0, 0, 0)) > 0:
                effects['hazard_warnings'].append('WIND_SHEAR')
        
        # Bird collision warnings
        for flock in self.bird_flocks:
            flock_distance = distance(position, flock.position)
            if flock_distance < 15:
                effects['hazard_warnings'].append('BIRD_STRIKE_RISK')
        
        return effects
    
    def update(self, dt, player_position=None):
        """Update all environmental hazards"""
        # Update spawn timers
        self.storm_spawn_timer -= dt
        self.wind_spawn_timer -= dt
        self.bird_spawn_timer -= dt
        
        # Spawn new hazards periodically
        if self.storm_spawn_timer <= 0:
            if random.random() < 0.3:  # 30% chance
                self.spawn_storm_cloud()
            self.storm_spawn_timer = random.uniform(120, 300)  # 2-5 minutes
        
        if self.wind_spawn_timer <= 0:
            if random.random() < 0.5:  # 50% chance
                self.spawn_wind_shear()
            self.wind_spawn_timer = random.uniform(60, 180)  # 1-3 minutes
        
        if self.bird_spawn_timer <= 0:
            if random.random() < 0.4:  # 40% chance
                self.spawn_bird_flock()
            self.bird_spawn_timer = random.uniform(90, 240)  # 1.5-4 minutes
        
        # Update storm clouds
        self.storm_clouds = [storm for storm in self.storm_clouds if storm.update(dt)]
        
        # Update wind shears
        for wind_shear in self.wind_shears:
            wind_shear.update(dt)
        
        # Update bird flocks
        for flock in self.bird_flocks:
            flock.update(dt, player_position)
        
        # Remove old hazards that have drifted too far
        self.cleanup_distant_hazards(player_position)
    
    def cleanup_distant_hazards(self, player_position):
        """Remove hazards that are too far from player"""
        if not player_position:
            return
        
        cleanup_distance = self.world_bounds * 1.5
        
        # Clean up wind shears
        self.wind_shears = [ws for ws in self.wind_shears 
                           if distance(player_position, ws.position) < cleanup_distance]
        
        # Clean up bird flocks
        self.bird_flocks = [bf for bf in self.bird_flocks 
                           if distance(player_position, bf.position) < cleanup_distance] 