#!/usr/bin/env python3
"""
🦕 PREHISTORIC SAN FRANCISCO FLIGHT SIMULATOR 🌉
EPIC pterodactyl ecosystem flying through San Francisco with Golden Gate Bridge!

DESIGNED BY SENIOR DEVELOPERS
3D/4D DESIGN EXCELLENCE  
WE ARE LEGION - MAXIMUM EPIC FACTOR ACHIEVED

Run this file to experience the ultimate prehistoric flight adventure!
"""

from ursina import *
import sys
import os
import math
import random
from noise import pnoise2
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from physics.flight_physics import FlightPhysics
    from graphics.camera_system import OverheadCameraSystem, CinematicCamera, EnvironmentViewCamera
    from ui.game_ui import FlightHUD, MainMenu, PauseMenu
    import game_config as config
except ImportError:
    # Fallback configurations if modules don't exist
    print("Using fallback configurations...")
    
    class config:
        WORLD_SIZE = 400
        TERRAIN_SCALE = 0.02
        TERRAIN_HEIGHT_MULTIPLIER = 40

app = Ursina()

# =============================================================================
# 🦕 PTERODACTYL ECOSYSTEM - EPIC AI FLYING REPTILES 🦕
# =============================================================================

class PterodactylPhysics:
    """Advanced aerodynamics for large prehistoric flying reptiles"""
    
    def __init__(self, pterodactyl, species_config):
        self.pterodactyl = pterodactyl
        self.config = species_config
        
        # Physics properties
        self.velocity = Vec3(0, 0, 0)
        self.mass = species_config['mass']
        self.wing_span = species_config['wing_span']
        self.wing_area = species_config['wing_area']
        
        # Flight characteristics
        self.lift_coefficient = species_config['lift_coefficient']
        self.drag_coefficient = species_config['drag_coefficient'] 
        self.max_speed = species_config['max_speed']
        self.cruise_speed = species_config['cruise_speed']
        self.stall_speed = species_config['stall_speed']
        
        # AI flight state
        self.target_position = Vec3(0, 0, 0)
        self.flight_mode = 'cruise'
        self.energy = 1.0
        
    def update_ai_flight(self, dt, nearby_pterodactyls, player_position):
        """Advanced AI flight behavior"""
        self.choose_flight_behavior(nearby_pterodactyls, player_position)
        
        # Apply flocking forces
        flocking_force = self.calculate_flocking_forces(nearby_pterodactyls)
        
        # Environmental forces
        wind_force = self.get_wind_force()
        thermal_force = self.seek_thermals()
        
        # Navigation forces
        nav_force = self.navigate_to_target()
        
        # Combine all forces
        total_force = flocking_force + wind_force + thermal_force + nav_force
        
        # Apply physics
        acceleration = total_force / self.mass
        self.velocity += acceleration * dt
        
        # Speed limits
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
        elif speed < self.stall_speed:
            self.velocity += Vec3(0, 2, 0) * dt
        
        # Update position
        self.pterodactyl.position += self.velocity * dt
        
        # Update energy
        self.update_energy(dt, speed)
        
        return speed, self.flight_mode
    
    def choose_flight_behavior(self, nearby_pterodactyls, player_position):
        """AI decision making for flight behavior"""
        player_distance = distance(self.pterodactyl.position, player_position)
        
        if player_distance < 20:
            if self.config['aggression'] > 0.7:
                self.flight_mode = 'hunt'
                self.target_position = player_position
            else:
                self.flight_mode = 'flee'
                flee_direction = (self.pterodactyl.position - player_position).normalized()
                self.target_position = self.pterodactyl.position + flee_direction * 50
        elif self.energy < 0.3:
            self.flight_mode = 'thermal'
            self.find_nearest_thermal()
        else:
            self.flight_mode = 'patrol'
            if distance(self.pterodactyl.position, self.target_position) < 10:
                self.set_new_patrol_target()
    
    def calculate_flocking_forces(self, nearby_pterodactyls):
        """Boids-style flocking behavior"""
        if not nearby_pterodactyls:
            return Vec3(0, 0, 0)
        
        separation = Vec3(0, 0, 0)
        alignment = Vec3(0, 0, 0)
        cohesion = Vec3(0, 0, 0)
        
        neighbor_count = 0
        for other in nearby_pterodactyls:
            if other == self.pterodactyl:
                continue
                
            dist = distance(self.pterodactyl.position, other.position)
            if dist < self.config['flocking_radius']:
                neighbor_count += 1
                
                if dist < self.config['separation_radius']:
                    diff = self.pterodactyl.position - other.position
                    diff = diff.normalized() / max(dist, 0.1)
                    separation += diff
                
                if hasattr(other, 'physics'):
                    alignment += other.physics.velocity
                
                cohesion += other.position
        
        if neighbor_count > 0:
            separation = separation.normalized() * self.config['separation_strength']
            alignment = (alignment / neighbor_count).normalized() * self.config['alignment_strength']
            cohesion = ((cohesion / neighbor_count) - self.pterodactyl.position).normalized() * self.config['cohesion_strength']
        
        return separation + alignment + cohesion
    
    def seek_thermals(self):
        """AI thermal seeking behavior"""
        best_thermal_force = Vec3(0, 0, 0)
        
        for angle in range(0, 360, 30):
            for dist in [10, 20, 30]:
                sample_x = self.pterodactyl.x + math.cos(math.radians(angle)) * dist
                sample_z = self.pterodactyl.z + math.sin(math.radians(angle)) * dist
                
                thermal_strength = math.sin(sample_x * 0.05) * math.cos(sample_z * 0.05) + random.uniform(-0.5, 0.5)
                
                if thermal_strength > 0.3:
                    direction = Vec3(sample_x - self.pterodactyl.x, 5, sample_z - self.pterodactyl.z)
                    thermal_force = direction.normalized() * thermal_strength * 2
                    
                    if distance(thermal_force, Vec3(0, 0, 0)) > distance(best_thermal_force, Vec3(0, 0, 0)):
                        best_thermal_force = thermal_force
        
        return best_thermal_force
    
    def navigate_to_target(self):
        """Navigate towards current target"""
        if not self.target_position:
            return Vec3(0, 0, 0)
        
        direction = self.target_position - self.pterodactyl.position
        distance_to_target = distance(direction, Vec3(0, 0, 0))
        
        if distance_to_target < 1:
            return Vec3(0, 0, 0)
        
        steering_force = direction.normalized() * self.config['steering_strength']
        
        if distance_to_target < 20:
            steering_force *= (distance_to_target / 20)
        
        return steering_force
    
    def find_nearest_thermal(self):
        """Find the nearest thermal for energy recovery"""
        angle = random.uniform(0, 360)
        distance = random.uniform(30, 80)
        
        self.target_position = self.pterodactyl.position + Vec3(
            math.cos(math.radians(angle)) * distance,
            random.uniform(10, 30),
            math.sin(math.radians(angle)) * distance
        )
    
    def set_new_patrol_target(self):
        """Set a new random patrol target"""
        patrol_areas = [
            Vec3(-80, 50, 120),  # Golden Gate Bridge
            Vec3(-20, 30, 100),  # Alcatraz
            Vec3(-45, 70, 45),   # Downtown
            Vec3(0, 80, 0),      # Twin Peaks
            Vec3(-60, 90, 60),   # Telegraph Hill
        ]
        
        base_target = random.choice(patrol_areas)
        offset = Vec3(
            random.uniform(-30, 30),
            random.uniform(-20, 20), 
            random.uniform(-30, 30)
        )
        
        self.target_position = base_target + offset
    
    def get_wind_force(self):
        """Environmental wind effects"""
        wind = Vec3(
            math.sin(time.time() * 0.1) * 1.5,
            0,
            math.cos(time.time() * 0.08) * 1.0
        )
        
        wind_effect = wind * (self.wing_span / 15)
        return wind_effect
    
    def update_energy(self, dt, speed):
        """Update pterodactyl energy levels"""
        energy_cost = (speed / self.max_speed) * 0.1 * dt
        
        if self.flight_mode == 'thermal':
            self.energy = min(1.0, self.energy + 0.2 * dt)
        elif speed < self.cruise_speed:
            self.energy = min(1.0, self.energy + 0.05 * dt)
        else:
            self.energy = max(0.0, self.energy - energy_cost)

class Pterodactyl(Entity):
    """Individual pterodactyl with species-specific characteristics"""
    
    def __init__(self, species_type, position=Vec3(0, 50, 0)):
        super().__init__()
        
        self.species_type = species_type
        self.species_config = self.get_species_config(species_type)
        self.position = position
        
        # Create model
        self.create_pterodactyl_model()
        
        # Initialize physics
        self.physics = PterodactylPhysics(self, self.species_config)
        
        # Animation state
        self.wing_beat_time = 0
        self.call_timer = random.uniform(0, 10)
        
        # Behavior state
        self.last_call_time = 0
        self.territorial_center = position.copy()
    
    def get_species_config(self, species_type):
        """Get configuration for different pterodactyl species"""
        species_configs = {
            'pteranodon': {
                'mass': 25, 'wing_span': 9, 'wing_area': 12,
                'max_speed': 30, 'cruise_speed': 15, 'stall_speed': 8,
                'lift_coefficient': 1.2, 'drag_coefficient': 0.02,
                'aggression': 0.3, 'flocking_radius': 40, 'separation_radius': 15,
                'separation_strength': 2.0, 'alignment_strength': 1.0, 'cohesion_strength': 0.8,
                'steering_strength': 1.5, 'scale_factor': 1.0, 'color': color.rgb(120, 80, 60),
            },
            'quetzalcoatlus': {
                'mass': 70, 'wing_span': 15, 'wing_area': 25,
                'max_speed': 25, 'cruise_speed': 12, 'stall_speed': 6,
                'lift_coefficient': 1.5, 'drag_coefficient': 0.015,
                'aggression': 0.8, 'flocking_radius': 60, 'separation_radius': 25,
                'separation_strength': 3.0, 'alignment_strength': 0.8, 'cohesion_strength': 0.5,
                'steering_strength': 1.0, 'scale_factor': 1.8, 'color': color.rgb(80, 60, 40),
            },
            'dimorphodon': {
                'mass': 12, 'wing_span': 4, 'wing_area': 6,
                'max_speed': 40, 'cruise_speed': 20, 'stall_speed': 10,
                'lift_coefficient': 1.0, 'drag_coefficient': 0.025,
                'aggression': 0.9, 'flocking_radius': 25, 'separation_radius': 8,
                'separation_strength': 1.5, 'alignment_strength': 1.5, 'cohesion_strength': 1.2,
                'steering_strength': 2.0, 'scale_factor': 0.6, 'color': color.rgb(100, 90, 70),
            }
        }
        
        return species_configs.get(species_type, species_configs['pteranodon'])
    
    def create_pterodactyl_model(self):
        """Create detailed 3D pterodactyl model"""
        scale_factor = self.species_config['scale_factor']
        base_color = self.species_config['color']
        
        # Main body
        self.body = Entity(
            parent=self, model='cube', color=base_color,
            scale=(3 * scale_factor, 1.5 * scale_factor, 1 * scale_factor)
        )
        
        # Head with long crest
        self.head = Entity(
            parent=self, model='cube',
            color=color.rgb(base_color.r + 20, base_color.g + 10, base_color.b + 10),
            scale=(1.5 * scale_factor, 1 * scale_factor, 2 * scale_factor),
            position=(0, 0.5 * scale_factor, 2 * scale_factor)
        )
        
        # Crest
        self.crest = Entity(
            parent=self.head, model='cube',
            color=color.rgb(base_color.r + 30, base_color.g + 20, base_color.b + 15),
            scale=(0.5, 2 * scale_factor, 1),
            position=(0, 1 * scale_factor, 0.5)
        )
        
        # Beak
        self.beak = Entity(
            parent=self.head, model='cube', color=color.rgb(50, 50, 40),
            scale=(0.3, 0.3, 1.5 * scale_factor),
            position=(0, 0, 1.5 * scale_factor)
        )
        
        # Eyes
        for eye_x in [-0.4, 0.4]:
            eye = Entity(
                parent=self.head, model='sphere', color=color.yellow,
                scale=0.3 * scale_factor,
                position=(eye_x * scale_factor, 0.2, 0.5)
            )
        
        # Wings
        wing_length = self.species_config['wing_span'] / 2
        
        self.left_wing = Entity(
            parent=self, model='cube',
            color=color.rgba(base_color.r, base_color.g, base_color.b, 220),
            scale=(wing_length, 0.2 * scale_factor, 2 * scale_factor),
            position=(-wing_length/2 - 1, 0, 0), rotation=(0, 0, 10)
        )
        
        self.right_wing = Entity(
            parent=self, model='cube',
            color=color.rgba(base_color.r, base_color.g, base_color.b, 220),
            scale=(wing_length, 0.2 * scale_factor, 2 * scale_factor),
            position=(wing_length/2 + 1, 0, 0), rotation=(0, 0, -10)
        )
        
        # Neck
        self.neck = Entity(
            parent=self, model='cube', color=base_color,
            scale=(0.8 * scale_factor, 0.8 * scale_factor, 1.5 * scale_factor),
            position=(0, 0.3 * scale_factor, 1 * scale_factor)
        )
        
        # Tail
        self.tail = Entity(
            parent=self, model='cube', color=base_color,
            scale=(0.5 * scale_factor, 0.5 * scale_factor, 2 * scale_factor),
            position=(0, 0, -2.5 * scale_factor)
        )
    
    def update(self, nearby_pterodactyls, player_position):
        """Update pterodactyl behavior and animation"""
        dt = time.dt
        
        # Update AI physics
        speed, flight_mode = self.physics.update_ai_flight(dt, nearby_pterodactyls, player_position)
        
        # Update animations
        self.update_animations(speed, flight_mode)
        
        # Pterodactyl calls
        self.update_vocalizations(dt)
        
        # Orient towards movement direction
        if distance(self.physics.velocity, Vec3(0, 0, 0)) > 1:
            forward = self.physics.velocity.normalized()
            self.look_at(self.position + forward, up=Vec3(0, 1, 0))
        
        return flight_mode
    
    def update_animations(self, speed, flight_mode):
        """Update pterodactyl wing animations and body language"""
        base_frequency = 2.0 / self.species_config['wing_span']
        speed_factor = max(0.5, speed / self.species_config['cruise_speed'])
        
        self.wing_beat_time += time.dt * base_frequency * speed_factor
        
        if speed > self.species_config['stall_speed']:
            wing_flap = math.sin(self.wing_beat_time) * 25
            
            if flight_mode == 'thermal':
                base_angle = 5
                wing_flap *= 0.3
            elif flight_mode == 'hunt':
                base_angle = 15
                wing_flap *= 1.2
            else:
                base_angle = 10
            
            self.left_wing.rotation_z = base_angle + wing_flap
            self.right_wing.rotation_z = -base_angle - wing_flap
        else:
            glide_adjust = math.sin(time.time() * 0.5) * 3
            self.left_wing.rotation_z = 5 + glide_adjust
            self.right_wing.rotation_z = -5 - glide_adjust
        
        # Head movement based on behavior
        if flight_mode == 'hunt':
            head_bob = math.sin(time.time() * 3) * 5
            self.head.rotation_x = -10 + head_bob
        elif flight_mode == 'flee':
            head_scan = math.sin(time.time() * 4) * 15
            self.head.rotation_y = head_scan
        else:
            self.head.rotation_x = lerp(self.head.rotation_x, 0, 2 * time.dt)
            self.head.rotation_y = lerp(self.head.rotation_y, 0, 2 * time.dt)
    
    def update_vocalizations(self, dt):
        """Handle pterodactyl calls and sounds"""
        self.call_timer -= dt
        
        if self.call_timer <= 0:
            self.emit_call()
            self.call_timer = random.uniform(8, 20)
    
    def emit_call(self):
        """Visual representation of pterodactyl call"""
        call_effect = Entity(
            model='sphere', color=color.rgba(255, 255, 0, 100),
            scale=1, position=self.position, parent=scene
        )
        
        call_effect.animate_scale(5, duration=2)
        call_effect.animate('color', color.rgba(255, 255, 0, 0), duration=2)
        destroy(call_effect, delay=2.1)

class PterodactylFlock:
    """Manages groups of pterodactyls with collective behavior"""
    
    def __init__(self, species_type, flock_size, center_position):
        self.species_type = species_type
        self.pterodactyls = []
        self.center_position = center_position
        self.flock_behavior = 'patrol'
        
        for i in range(flock_size):
            offset = Vec3(
                random.uniform(-20, 20),
                random.uniform(-10, 10),
                random.uniform(-20, 20)
            )
            
            pterodactyl = Pterodactyl(species_type, center_position + offset)
            self.pterodactyls.append(pterodactyl)
    
    def update(self, player_position, other_flocks=[]):
        """Update entire flock behavior"""
        for pterodactyl in self.pterodactyls:
            nearby_pterodactyls = self.get_nearby_pterodactyls(pterodactyl, 50)
            flight_mode = pterodactyl.update(nearby_pterodactyls, player_position)
        
        self.update_flock_behavior(player_position)
    
    def get_nearby_pterodactyls(self, target_pterodactyl, radius):
        """Get pterodactyls within radius of target"""
        nearby = []
        
        for pterodactyl in self.pterodactyls:
            if pterodactyl != target_pterodactyl:
                dist = distance(target_pterodactyl.position, pterodactyl.position)
                if dist < radius:
                    nearby.append(pterodactyl)
        
        return nearby
    
    def update_flock_behavior(self, player_position):
        """Coordinate flock-level decisions"""
        flock_center = self.get_flock_center()
        player_distance = distance(flock_center, player_position)
        
        if player_distance < 30:
            if self.species_type == 'dimorphodon':
                self.flock_behavior = 'hunting'
            else:
                self.flock_behavior = 'fleeing'
        else:
            self.flock_behavior = 'patrol'
    
    def get_flock_center(self):
        """Calculate the center position of the flock"""
        if not self.pterodactyls:
            return self.center_position
        
        total_pos = Vec3(0, 0, 0)
        for pterodactyl in self.pterodactyls:
            total_pos += pterodactyl.position
        
        return total_pos / len(self.pterodactyls)

class PterodactylEcosystem:
    """Manages the entire pterodactyl ecosystem in San Francisco"""
    
    def __init__(self):
        self.flocks = []
        self.create_ecosystem()
    
    def create_ecosystem(self):
        """Create multiple flocks around San Francisco"""
        
        # Pteranodon flock around Golden Gate Bridge
        golden_gate_flock = PterodactylFlock('pteranodon', 6, Vec3(-80, 80, 120))
        self.flocks.append(golden_gate_flock)
        
        # Quetzalcoatlus pair over Twin Peaks
        giant_flock = PterodactylFlock('quetzalcoatlus', 2, Vec3(0, 120, 0))
        self.flocks.append(giant_flock)
        
        # Dimorphodon pack hunters around Alcatraz
        hunter_flock = PterodactylFlock('dimorphodon', 8, Vec3(-20, 60, 100))
        self.flocks.append(hunter_flock)
        
        # Mixed flock over downtown SF
        downtown_flock = PterodactylFlock('pteranodon', 4, Vec3(-45, 90, 45))
        self.flocks.append(downtown_flock)
        
        print(f"🦕 Pterodactyl ecosystem created with {len(self.flocks)} flocks")
        print(f"Total pterodactyls: {sum(len(flock.pterodactyls) for flock in self.flocks)}")
    
    def update(self, player_position):
        """Update the entire ecosystem"""
        for flock in self.flocks:
            flock.update(player_position, self.flocks)
    
    def get_all_pterodactyls(self):
        """Get list of all pterodactyls in the ecosystem"""
        all_pterodactyls = []
        for flock in self.flocks:
            all_pterodactyls.extend(flock.pterodactyls)
        return all_pterodactyls

# =============================================================================
# 🌉 SAN FRANCISCO WORLD - GOLDEN GATE BRIDGE & LANDMARKS 🌉
# =============================================================================

class SanFranciscoTerrain(Entity):
    """Accurate San Francisco topography with iconic hills and bay"""
    
    def __init__(self, size=400, resolution=80):
        super().__init__()
        self.size = size
        self.resolution = resolution
        
        # San Francisco specific parameters
        self.sf_features = {
            'twin_peaks': {'pos': (0, 0), 'height': 280, 'radius': 25},
            'nob_hill': {'pos': (-40, 30), 'height': 104, 'radius': 15},
            'russian_hill': {'pos': (-35, 45), 'height': 91, 'radius': 12},
            'telegraph_hill': {'pos': (-60, 60), 'height': 84, 'radius': 10},
            'pacific_heights': {'pos': (-70, 20), 'height': 110, 'radius': 20},
            'potrero_hill': {'pos': (40, -30), 'height': 68, 'radius': 18},
            'bernal_heights': {'pos': (35, -60), 'height': 80, 'radius': 15},
        }
        
        # Golden Gate Bridge location
        self.golden_gate_pos = (-80, 120)
        self.bay_center = (0, 80)
        
        self.generate_sf_terrain()
        self.create_sf_mesh()
    
    def generate_sf_terrain(self):
        """Generate San Francisco's famous hills and topography"""
        self.height_map = []
        
        for i in range(self.resolution + 1):
            row = []
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                
                # Base terrain
                height = 0
                
                # Add San Francisco hills
                for hill_name, hill_data in self.sf_features.items():
                    hill_x, hill_z = hill_data['pos']
                    hill_height = hill_data['height']
                    hill_radius = hill_data['radius']
                    
                    dist = math.sqrt((x - hill_x)**2 + (z - hill_z)**2)
                    if dist < hill_radius * 2:
                        hill_factor = max(0, 1 - (dist / (hill_radius * 2))**2)
                        height += hill_height * hill_factor
                
                # San Francisco Bay (negative elevation for water)
                bay_dist = math.sqrt((x - self.bay_center[0])**2 + (z - self.bay_center[1])**2)
                if bay_dist < 60:
                    bay_factor = max(0, 1 - (bay_dist / 60)**3)
                    height -= 20 * bay_factor
                
                # Pacific Ocean (west side)
                if x < -120:
                    ocean_factor = max(0, (x + 120) / -20)
                    height -= 15 * ocean_factor
                
                # Add noise for realistic terrain variation
                height += pnoise2(x * 0.01, z * 0.01) * 8
                height += pnoise2(x * 0.03, z * 0.03) * 3
                
                # Ensure minimum ground level
                height = max(height, -25)
                
                row.append(height)
            self.height_map.append(row)
    
    def create_sf_mesh(self):
        """Create terrain mesh with San Francisco color scheme"""
        vertices = []
        triangles = []
        uvs = []
        colors = []
        
        for i in range(self.resolution + 1):
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                y = self.height_map[i][j]
                
                vertices.append(Vec3(x, y, z))
                uvs.append((i/self.resolution, j/self.resolution))
                
                # San Francisco color scheme
                if y < -5:
                    colors.append(color.rgb(0.1, 0.3, 0.6))  # Bay water
                elif y < 0:
                    colors.append(color.rgb(0.2, 0.5, 0.8))  # Shallow water
                elif y < 20:
                    colors.append(color.rgb(0.8, 0.7, 0.5))  # Beach/low areas
                elif y < 50:
                    colors.append(color.rgb(0.4, 0.6, 0.3))  # Low hills
                elif y < 100:
                    colors.append(color.rgb(0.5, 0.5, 0.4))  # Mid hills
                else:
                    colors.append(color.rgb(0.6, 0.6, 0.6))  # High peaks
        
        # Generate triangles
        for i in range(self.resolution):
            for j in range(self.resolution):
                v1 = i * (self.resolution + 1) + j
                v2 = (i + 1) * (self.resolution + 1) + j
                v3 = i * (self.resolution + 1) + (j + 1)
                v4 = (i + 1) * (self.resolution + 1) + (j + 1)
                
                triangles.extend([v1, v2, v3, v2, v4, v3])
        
        self.model = Mesh(vertices=vertices, triangles=triangles, uvs=uvs, colors=colors)
        self.model.generate()
    
    def get_height_at_position(self, x, z):
        """Get terrain height at world position"""
        map_x = int((x + self.size/2) * self.resolution / self.size)
        map_z = int((z + self.size/2) * self.resolution / self.size)
        
        map_x = max(0, min(self.resolution, map_x))
        map_z = max(0, min(self.resolution, map_z))
        
        return self.height_map[map_x][map_z]

class GoldenGateBridge(Entity):
    """🌉 DETAILED 3D MODEL OF THE ICONIC GOLDEN GATE BRIDGE 🌉"""
    
    def __init__(self, position=Vec3(-80, 15, 120)):
        super().__init__()
        self.position = position
        self.bridge_length = 120
        self.bridge_width = 8
        self.tower_height = 80
        
        self.create_golden_gate_bridge()
    
    def create_golden_gate_bridge(self):
        """Build the complete Golden Gate Bridge structure"""
        
        # Main bridge deck
        self.deck = Entity(
            parent=self, model='cube',
            color=color.rgb(196, 76, 25),  # International Orange
            scale=(self.bridge_length, 2, self.bridge_width),
            position=(0, 25, 0)
        )
        
        # North Tower
        self.north_tower = Entity(
            parent=self, model='cube',
            color=color.rgb(196, 76, 25),
            scale=(6, self.tower_height, 4),
            position=(-30, self.tower_height/2, 0)
        )
        
        # South Tower  
        self.south_tower = Entity(
            parent=self, model='cube',
            color=color.rgb(196, 76, 25),
            scale=(6, self.tower_height, 4),
            position=(30, self.tower_height/2, 0)
        )
        
        # Main suspension cables
        self.create_suspension_cables()
        
        # Bridge approaches
        self.create_bridge_approaches()
        
        # Art Deco details
        self.add_bridge_details()
    
    def create_suspension_cables(self):
        """Create the iconic suspension cable system"""
        cable_height = self.tower_height - 5
        
        # Main cables
        for side in [-2, 2]:
            main_cable = Entity(
                parent=self, model='cube',
                color=color.rgb(150, 150, 150),
                scale=(self.bridge_length + 20, 0.5, 0.5),
                position=(0, cable_height, side)
            )
            
            # Vertical suspension cables
            for i in range(-50, 51, 10):
                cable_length = cable_height - 25 + abs(i) * 0.1
                vertical_cable = Entity(
                    parent=self, model='cube',
                    color=color.rgb(120, 120, 120),
                    scale=(0.2, cable_length, 0.2),
                    position=(i, 25 + cable_length/2, side)
                )
    
    def create_bridge_approaches(self):
        """Create the approach spans and roadways"""
        # Marin approach (north)
        marin_approach = Entity(
            parent=self, model='cube',
            color=color.rgb(160, 160, 160),
            scale=(40, 1.5, self.bridge_width),
            position=(-80, 20, 0)
        )
        
        # San Francisco approach (south)
        sf_approach = Entity(
            parent=self, model='cube',
            color=color.rgb(160, 160, 160),
            scale=(40, 1.5, self.bridge_width),
            position=(80, 20, 0)
        )
    
    def add_bridge_details(self):
        """Add Art Deco architectural details"""
        # Tower tops with Art Deco styling
        for tower_x in [-30, 30]:
            tower_top = Entity(
                parent=self, model='cube',
                color=color.rgb(180, 60, 20),
                scale=(8, 4, 6),
                position=(tower_x, self.tower_height + 2, 0)
            )
            
            # Tower lights
            for light_y in range(10, int(self.tower_height), 15):
                light = Entity(
                    parent=self, model='sphere',
                    color=color.yellow, scale=0.5,
                    position=(tower_x + 3.5, light_y, 0)
                )

class SanFranciscoLandmarks:
    """🏢 ICONIC SAN FRANCISCO LANDMARKS 🏢"""
    
    def __init__(self, terrain):
        self.terrain = terrain
        self.landmarks = []
        self.create_landmarks()
    
    def create_landmarks(self):
        """Create famous SF landmarks"""
        
        # Alcatraz Island
        alcatraz_pos = Vec3(-20, 5, 100)
        self.create_alcatraz(alcatraz_pos)
        
        # Transamerica Pyramid
        pyramid_pos = Vec3(-45, 50, 45)
        self.create_transamerica_pyramid(pyramid_pos)
        
        # Coit Tower
        coit_pos = Vec3(-60, 84, 60)
        self.create_coit_tower(coit_pos)
        
        # Lombard Street
        self.create_lombard_street()
        
        # SF-Oakland Bay Bridge
        self.create_bay_bridge()
    
    def create_alcatraz(self, position):
        """The infamous island prison"""
        island = Entity(
            model='cube', color=color.rgb(0.5, 0.4, 0.3),
            scale=(15, 3, 12), position=position
        )
        
        prison = Entity(
            model='cube', color=color.rgb(0.6, 0.6, 0.5),
            scale=(8, 6, 10), position=position + Vec3(0, 4.5, 0)
        )
        
        self.landmarks.extend([island, prison])
    
    def create_transamerica_pyramid(self, position):
        """The iconic pyramid skyscraper"""
        base = Entity(
            model='cube', color=color.rgb(0.9, 0.9, 0.8),
            scale=(8, 20, 8), position=position + Vec3(0, 10, 0)
        )
        
        pyramid = Entity(
            model='cube', color=color.rgb(0.95, 0.95, 0.85),
            scale=(6, 30, 6), position=position + Vec3(0, 35, 0)
        )
        
        self.landmarks.extend([base, pyramid])
    
    def create_coit_tower(self, position):
        """The Art Deco tower on Telegraph Hill"""
        tower = Entity(
            model='cube', color=color.rgb(0.8, 0.8, 0.7),
            scale=(3, 25, 3), position=position + Vec3(0, 12.5, 0)
        )
        
        tower_top = Entity(
            model='cube', color=color.rgb(0.7, 0.7, 0.6),
            scale=(4, 3, 4), position=position + Vec3(0, 26.5, 0)
        )
        
        self.landmarks.extend([tower, tower_top])
    
    def create_lombard_street(self):
        """The world's crookedest street"""
        for i in range(8):
            angle = i * 45
            x = -35 + math.sin(math.radians(angle)) * 3
            z = 45 + i * 2
            y = self.terrain.get_height_at_position(x, z)
            
            road_segment = Entity(
                model='cube', color=color.rgb(0.3, 0.3, 0.3),
                scale=(2, 0.5, 3), position=Vec3(x, y + 0.25, z),
                rotation_y=angle
            )
            self.landmarks.append(road_segment)
    
    def create_bay_bridge(self):
        """San Francisco-Oakland Bay Bridge"""
        bridge_y = 15
        
        west_span = Entity(
            model='cube', color=color.rgb(120, 120, 120),
            scale=(80, 2, 6), position=Vec3(40, bridge_y, 80)
        )
        
        east_span = Entity(
            model='cube', color=color.rgb(120, 120, 120),
            scale=(60, 2, 6), position=Vec3(110, bridge_y, 80)
        )
        
        for tower_x in [0, 80, 140]:
            tower = Entity(
                model='cube', color=color.rgb(100, 100, 100),
                scale=(4, 40, 3), position=Vec3(tower_x, 35, 80)
            )
            self.landmarks.append(tower)
        
        self.landmarks.extend([west_span, east_span])

# =============================================================================
# 🦅 PREHISTORIC PLAYER CREATURE 🦅
# =============================================================================

class PrehistoricPlayer(Entity):
    """🦅 Player's flying creature - enhanced for prehistoric San Francisco 🦅"""
    
    def __init__(self, creature_type='archaeopteryx'):
        super().__init__()
        
        self.creature_type = creature_type
        self.config = self.get_default_config()
        
        # Enhanced scale for epic visibility
        self.base_scale = 2.0
        
        # Create the player creature model
        self.create_player_model()
        
        # Flight state
        self.velocity = Vec3(0, 0, 0)
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        # Enhanced abilities
        self.energy = 1.0
        self.stamina = 1.0
        self.has_fire_breath = (creature_type == 'dragon')
        
        # Start position near Golden Gate Bridge
        self.position = Vec3(-50, 60, 80)
        
        # Enhanced visual effects
        self.create_epic_effects()
        
        # Interaction state
        self.nearby_pterodactyls = []
        self.reputation = 0
    
    def get_default_config(self):
        """Default configuration for player creature"""
        return {
            'max_speed': 35, 'glide_ratio': 5.0, 'lift_coefficient': 1.0,
            'drag_coefficient': 0.015, 'mass': 8, 'wing_area': 4.0,
            'max_pitch_rate': 3.0, 'max_yaw_rate': 3.0, 'max_roll_angle': 0.8,
        }
    
    def create_player_model(self):
        """Create epic player creature model"""
        if self.creature_type == 'archaeopteryx':
            self.create_archaeopteryx_model()
        elif self.creature_type == 'dragon':
            self.create_dragon_model()
        else:
            self.create_archaeopteryx_model()
    
    def create_archaeopteryx_model(self):
        """Create Archaeopteryx - the first bird"""
        # Body with feathers
        self.body = Entity(
            parent=self, model='cube', color=color.rgb(80, 60, 40),
            scale=(2.5 * self.base_scale, 1.0 * self.base_scale, 1.5 * self.base_scale)
        )
        
        # Feathered head
        self.head = Entity(
            parent=self, model='cube', color=color.rgb(90, 70, 50),
            scale=(1.2 * self.base_scale, 1.0 * self.base_scale, 1.0 * self.base_scale),
            position=(0, 0.3 * self.base_scale, 1.2 * self.base_scale)
        )
        
        # Sharp predator eyes
        for eye_x in [-0.4, 0.4]:
            eye = Entity(
                parent=self.head, model='sphere', color=color.orange,
                scale=0.25 * self.base_scale,
                position=(eye_x * self.base_scale, 0.2, 0.3)
            )
        
        # Toothed beak
        self.beak = Entity(
            parent=self.head, model='cube', color=color.rgb(40, 40, 30),
            scale=(0.3, 0.3, 0.8 * self.base_scale),
            position=(0, 0, 0.8 * self.base_scale)
        )
        
        # Feathered wings
        wing_length = 4 * self.base_scale
        
        self.left_wing = Entity(
            parent=self, model='cube', color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2 * self.base_scale),
            position=(-wing_length/2 - 0.8, 0, 0), rotation=(0, 0, 12)
        )
        
        self.right_wing = Entity(
            parent=self, model='cube', color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2 * self.base_scale),
            position=(wing_length/2 + 0.8, 0, 0), rotation=(0, 0, -12)
        )
        
        # Long feathered tail
        self.tail = Entity(
            parent=self, model='cube', color=color.rgb(70, 50, 30),
            scale=(0.6 * self.base_scale, 0.4 * self.base_scale, 3 * self.base_scale),
            position=(0, 0, -2.5 * self.base_scale)
        )
    
    def create_dragon_model(self):
        """Create small dragon model"""
        # Dragon body
        self.body = Entity(
            parent=self, model='cube', color=color.rgb(120, 20, 20),
            scale=(3 * self.base_scale, 1.2 * self.base_scale, 1.8 * self.base_scale)
        )
        
        # Dragon head with horns
        self.head = Entity(
            parent=self, model='cube', color=color.rgb(140, 30, 30),
            scale=(1.5 * self.base_scale, 1.2 * self.base_scale, 1.2 * self.base_scale),
            position=(0, 0.4 * self.base_scale, 1.5 * self.base_scale)
        )
        
        # Dragon wings
        wing_length = 5 * self.base_scale
        
        self.left_wing = Entity(
            parent=self, model='cube', color=color.rgba(100, 15, 15, 220),
            scale=(wing_length, 0.1 * self.base_scale, 3 * self.base_scale),
            position=(-wing_length/2 - 1, 0, 0), rotation=(0, 0, 15)
        )
        
        self.right_wing = Entity(
            parent=self, model='cube', color=color.rgba(100, 15, 15, 220),
            scale=(wing_length, 0.1 * self.base_scale, 3 * self.base_scale),
            position=(wing_length/2 + 1, 0, 0), rotation=(0, 0, -15)
        )
    
    def create_epic_effects(self):
        """Create enhanced visual effects"""
        # Enhanced particle trail
        self.trail_entities = []
        for i in range(10):
            trail_particle = Entity(
                parent=scene, model='cube',
                color=color.rgba(255, 200, 100, 140 - i*14),
                scale=0.4 - i*0.03, visible=False
            )
            self.trail_entities.append(trail_particle)
        
        # Energy aura
        self.energy_aura = Entity(
            parent=self, model='sphere',
            color=color.rgba(100, 200, 255, 50),
            scale=4, visible=False
        )
    
    def update(self, nearby_pterodactyls=[]):
        """Update player creature with enhanced interactions"""
        dt = time.dt
        
        # Store nearby pterodactyls
        self.nearby_pterodactyls = nearby_pterodactyls
        
        # Handle input
        self.handle_enhanced_input()
        
        # Apply physics
        self.apply_enhanced_physics(dt)
        
        # Update animations and effects
        speed = distance(self.velocity, Vec3(0, 0, 0))
        self.update_epic_animations(speed)
        self.update_epic_effects(speed)
        
        # Update abilities
        self.update_abilities(dt)
        
        # Keep above ground/water
        if self.y < 1:
            self.y = 1
            self.velocity.y = max(0, self.velocity.y)
        
        return {
            'speed': speed, 'altitude': self.position.y,
            'heading': self.rotation_y, 'energy': self.energy,
            'stamina': self.stamina, 'reputation': self.reputation
        }
    
    def handle_enhanced_input(self):
        """Enhanced input handling with special abilities"""
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        if held_keys['w']:
            self.pitch_input = 1
        elif held_keys['s']:
            self.pitch_input = -1
        
        if held_keys['a']:
            self.yaw_input = 1
            self.roll_input = 1
        elif held_keys['d']:
            self.yaw_input = -1
            self.roll_input = -1
        
        # Enhanced abilities
        if held_keys['space']:
            self.pitch_input += 0.6
            self.use_stamina(time.dt * 0.5)
        
        if held_keys['shift']:
            self.pitch_input -= 1.0
            
        # Special abilities
        if held_keys['f'] and self.has_fire_breath:
            self.breathe_fire()
        
        if held_keys['e']:
            self.thermal_boost()
    
    def apply_enhanced_physics(self, dt):
        """Enhanced physics for prehistoric flight"""
        # Gravity
        gravity = Vec3(0, -9.8, 0)
        
        # Forward thrust based on pitch
        thrust_force = Vec3(0, 0, max(0, -self.pitch_input * 15))
        
        # Rotate thrust based on yaw
        yaw_rad = math.radians(self.rotation_y)
        thrust_force = Vec3(
            thrust_force.z * math.sin(yaw_rad),
            thrust_force.y,
            thrust_force.z * math.cos(yaw_rad)
        )
        
        # Lift force
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > 0:
            lift_magnitude = self.config['lift_coefficient'] * speed * 0.15
            lift_force = Vec3(0, lift_magnitude, 0)
        else:
            lift_force = Vec3(0, 0, 0)
        
        # Drag force
        drag_force = -self.velocity * self.config['drag_coefficient'] * speed
        
        # Wind effects
        wind_force = Vec3(
            math.sin(time.time() * 0.5) * 2,
            0,
            math.cos(time.time() * 0.3) * 1.5
        )
        
        # Combine forces
        total_force = gravity + thrust_force + lift_force + drag_force + wind_force
        
        # Update velocity
        self.velocity += total_force * dt
        
        # Limit speed
        if speed > self.config['max_speed']:
            self.velocity = self.velocity.normalized() * self.config['max_speed']
        
        # Update position
        self.position += self.velocity * dt
    
    def update_epic_animations(self, speed):
        """Enhanced animations for epic gameplay"""
        # Wing animation
        wing_beat_time = time.time() * speed * 1.2
        
        if speed > 5:
            wing_flap = math.sin(wing_beat_time) * (18 - speed * 0.4)
            energy_boost = self.energy * 5
            
            base_angle = 8
            self.left_wing.rotation_z = base_angle + wing_flap + energy_boost
            self.right_wing.rotation_z = -base_angle - wing_flap - energy_boost
        else:
            glide_adjust = math.sin(time.time() * 0.7) * 4
            self.left_wing.rotation_z = 5 + glide_adjust
            self.right_wing.rotation_z = -5 - glide_adjust
        
        # Body orientation
        self.rotation_x = math.degrees(math.atan2(-self.velocity.y, abs(self.velocity.z) + 0.1))
        self.rotation_y += self.yaw_input * 50 * time.dt
        self.rotation_z = self.roll_input * 35
    
    def update_epic_effects(self, speed):
        """Update enhanced visual effects"""
        # Enhanced particle trail
        if speed > 3:
            for i, particle in enumerate(self.trail_entities):
                particle.visible = True
                trail_pos = self.position - self.forward * (i + 1) * 1.2
                particle.position = trail_pos
                alpha = max(0, 140 - i*14 - int(speed*2))
                particle.color = color.rgba(255, 200, 100, alpha)
        else:
            for particle in self.trail_entities:
                particle.visible = False
        
        # Energy aura when high energy
        if self.energy > 0.8:
            self.energy_aura.visible = True
            pulse = math.sin(time.time() * 4) * 0.3 + 0.7
            self.energy_aura.scale = 4 * pulse
            aura_alpha = int(50 * self.energy * pulse)
            self.energy_aura.color = color.rgba(100, 200, 255, aura_alpha)
        else:
            self.energy_aura.visible = False
    
    def update_abilities(self, dt):
        """Update special abilities"""
        # Regenerate energy slowly
        if self.energy < 1.0:
            self.energy = min(1.0, self.energy + 0.1 * dt)
        
        # Regenerate stamina
        if self.stamina < 1.0:
            self.stamina = min(1.0, self.stamina + 0.2 * dt)
    
    def use_stamina(self, amount):
        """Use stamina for special maneuvers"""
        self.stamina = max(0, self.stamina - amount)
    
    def thermal_boost(self):
        """Use thermal vision to find updrafts"""
        if self.energy > 0.2:
            self.velocity.y += 3 * time.dt
            self.energy -= 0.5 * time.dt
    
    def breathe_fire(self):
        """Dragon fire breath ability"""
        if self.has_fire_breath and self.energy > 0.3:
            # Create fire effect
            fire_effect = Entity(
                model='cube', color=color.rgba(255, 100, 0, 200),
                scale=(1, 1, 8), position=self.position + self.forward * 4,
                rotation=self.rotation, parent=scene
            )
            
            # Animate fire
            fire_effect.animate_scale((3, 3, 12), duration=1)
            fire_effect.animate('color', color.rgba(255, 0, 0, 0), duration=1)
            
            destroy(fire_effect, delay=1.1)
            self.energy -= 0.2

# =============================================================================
# 🎮 EPIC GAME SYSTEMS 🎮
# =============================================================================

class PrehistoricCollectible(Entity):
    """Prehistoric collectibles - dinosaur eggs, amber, fossils"""
    
    def __init__(self, position, collectible_type='dino_egg'):
        super().__init__()
        self.position = position
        self.collectible_type = collectible_type
        self.collected = False
        self.rotation_speed = 30
        
        # Epic scale for prehistoric items
        base_scale = 0.8
        
        if collectible_type == 'dino_egg':
            self.model = 'sphere'
            self.color = color.rgb(200, 180, 160)
            self.scale = base_scale * 1.2
        elif collectible_type == 'amber':
            self.model = 'cube'
            self.color = color.rgb(255, 180, 0)
            self.scale = base_scale * 0.8
        elif collectible_type == 'fossil':
            self.model = 'cube'
            self.color = color.rgb(120, 100, 80)
            self.scale = base_scale
        
        # EPIC glow effect
        self.glow = Entity(
            parent=self, model='sphere',
            color=color.rgba(255, 215, 0, 120),
            scale=3.5
        )
        
        # Prehistoric energy beacon
        self.energy_beam = Entity(
            parent=self, model='cube',
            color=color.rgba(0, 255, 100, 180),
            scale=(0.2, 8, 0.2), position=(0, 4, 0)
        )
    
    def update(self):
        """Epic prehistoric collectible animation"""
        if not self.collected:
            self.rotation_y += self.rotation_speed * time.dt
            
            # Dramatic floating animation
            self.y += math.sin(time.time() * 2 + self.x) * 1.2 * time.dt
            
            # Pulsing epic glow
            pulse = math.sin(time.time() * 3) * 0.4 + 0.6
            glow_alpha = int(120 * pulse)
            self.glow.color = color.rgba(255, 215, 0, glow_alpha)
            
            # Energy beam animation
            beam_alpha = int(180 * pulse)
            self.energy_beam.color = color.rgba(0, 255, 100, beam_alpha)
            self.energy_beam.rotation_y += 90 * time.dt
    
    def collect(self):
        """Collect prehistoric artifact"""
        if not self.collected:
            self.collected = True
            
            # EPIC collection effect
            explosion = Entity(
                model='sphere', color=color.rgba(255, 255, 0, 200),
                scale=1, position=self.position, parent=scene
            )
            explosion.animate_scale(8, duration=1.5)
            explosion.animate('color', color.rgba(255, 255, 0, 0), duration=1.5)
            destroy(explosion, delay=1.6)
            
            self.visible = False
            self.energy_beam.visible = False
            return True
        return False

class PrehistoricGameManager:
    """Epic game manager for prehistoric San Francisco"""
    
    def __init__(self):
        self.score = 0
        self.artifacts_collected = 0
        self.total_artifacts = 0
        self.flight_time = 0
        self.max_altitude = 0
        self.max_speed = 0
        self.pterodactyl_encounters = 0
        self.bridge_flythroughs = 0
        
        # Game state
        self.game_started = False
        self.game_paused = False
        self.hud_visible = True
        
        # EPIC OBJECTIVES
        self.objectives = [
            "🦴 Collect 8 prehistoric artifacts",
            "🌉 Fly through the Golden Gate Bridge 3 times",
            "🦕 Encounter all 3 pterodactyl species",
            "🏔️ Reach the summit of Twin Peaks (280m)",
            "🌊 Fly over Alcatraz Island",
            "💨 Achieve 40 m/s maximum speed",
            "⚡ Survive 5 minutes in prehistoric SF"
        ]
        self.completed_objectives = []
        
        # Reputation with pterodactyls
        self.pterodactyl_reputation = 0.0
        self.species_encountered = set()
        
        # Bridge flythrough detection
        self.last_bridge_position = None
        self.bridge_zone = (-80, 120)  # Golden Gate position
    
    def update(self, player, pterodactyls):
        """Update epic game state"""
        if not self.game_started or self.game_paused:
            return
        
        # Update flight time
        self.flight_time += time.dt
        
        # Update records
        if player.position.y > self.max_altitude:
            self.max_altitude = player.position.y
        
        current_speed = distance(player.velocity, Vec3(0, 0, 0))
        if current_speed > self.max_speed:
            self.max_speed = current_speed
        
        # Check pterodactyl encounters
        self.check_pterodactyl_encounters(player, pterodactyls)
        
        # Check bridge flythroughs
        self.check_bridge_flythrough(player)
        
        # Check objectives
        self.check_epic_objectives()
    
    def check_pterodactyl_encounters(self, player, pterodactyls):
        """Track encounters with different pterodactyl species"""
        for pterodactyl in pterodactyls:
            distance_to_ptero = distance(player.position, pterodactyl.position)
            
            if distance_to_ptero < 20:
                if hasattr(pterodactyl, 'species_type'):
                    self.species_encountered.add(pterodactyl.species_type)
                    
                if distance_to_ptero < 8:
                    self.pterodactyl_encounters += 1
    
    def check_bridge_flythrough(self, player):
        """Check if player flew through Golden Gate Bridge"""
        bridge_x, bridge_z = self.bridge_zone
        
        # Check if near bridge
        if (abs(player.x - bridge_x) < 60 and 
            abs(player.z - bridge_z) < 15 and
            10 < player.y < 60):
            
            current_side = "north" if player.z > bridge_z else "south"
            
            if self.last_bridge_position and self.last_bridge_position != current_side:
                # Flew through the bridge!
                self.bridge_flythroughs += 1
                self.score += 500
                print(f"🌉 EPIC! Flew through Golden Gate Bridge! Total: {self.bridge_flythroughs}")
            
            self.last_bridge_position = current_side
        else:
            self.last_bridge_position = None
    
    def check_epic_objectives(self):
        """Check completion of epic objectives"""
        
        # Bridge flythrough objective
        if (self.bridge_flythroughs >= 3 and 
            "🌉 Fly through the Golden Gate Bridge 3 times" not in self.completed_objectives):
            self.completed_objectives.append("🌉 Fly through the Golden Gate Bridge 3 times")
            self.score += 2000
        
        # Species encounter objective
        if (len(self.species_encountered) >= 3 and
            "🦕 Encounter all 3 pterodactyl species" not in self.completed_objectives):
            self.completed_objectives.append("🦕 Encounter all 3 pterodactyl species")
            self.score += 1500
        
        # Altitude objective
        if (self.max_altitude >= 280 and
            "🏔️ Reach the summit of Twin Peaks (280m)" not in self.completed_objectives):
            self.completed_objectives.append("🏔️ Reach the summit of Twin Peaks (280m)")
            self.score += 1000
        
        # Speed objective
        if (self.max_speed >= 40 and
            "💨 Achieve 40 m/s maximum speed" not in self.completed_objectives):
            self.completed_objectives.append("💨 Achieve 40 m/s maximum speed")
            self.score += 800
        
        # Survival objective
        if (self.flight_time >= 300 and
            "⚡ Survive 5 minutes in prehistoric SF" not in self.completed_objectives):
            self.completed_objectives.append("⚡ Survive 5 minutes in prehistoric SF")
            self.score += 1200
        
        # Artifact objective
        if (self.artifacts_collected >= 8 and
            "🦴 Collect 8 prehistoric artifacts" not in self.completed_objectives):
            self.completed_objectives.append("🦴 Collect 8 prehistoric artifacts")
            self.score += 2500
    
    def collect_artifact(self, artifact_type):
        """Handle prehistoric artifact collection"""
        self.artifacts_collected += 1
        
        if artifact_type == 'dino_egg':
            self.score += 200
        elif artifact_type == 'amber':
            self.score += 150
        elif artifact_type == 'fossil':
            self.score += 100

# =============================================================================
# 🌉 MAIN EPIC GAME CLASS 🌉
# =============================================================================

class PrehistoricSanFranciscoSimulator:
    """🦕 EPIC MAIN GAME CLASS - MAXIMUM POWER ACHIEVED 🌉"""
    
    def __init__(self):
        self.setup_epic_window()
        self.game_manager = PrehistoricGameManager()
        
        # Create the prehistoric world
        self.create_prehistoric_world()
        self.create_camera_system()
        self.create_ui_system()
        self.create_prehistoric_collectibles()
        
        # Game state
        self.show_menu = True
        self.camera_mode = 'overhead'
        
        # EPIC startup messages
        print("🦕" * 50)
        print("PREHISTORIC SAN FRANCISCO FLIGHT SIMULATOR")
        print("FEATURING PTERODACTYLS AND THE GOLDEN GATE BRIDGE")
        print("SENIOR DEVELOPER QUALITY - WE ARE LEGION")
        print("🦕" * 50)
        print()
        print("🎮 CONTROLS:")
        print("   WASD = Flight Control")
        print("   Space = Energy Boost")
        print("   Shift = Power Dive")
        print("   E = Thermal Vision")
        print("   F = Special Ability")
        print("   Mouse Wheel = Camera Zoom")
        print("   C = Camera Mode")
        print()
        print("🎯 EPIC OBJECTIVES:")
        print("   🌉 Fly through Golden Gate Bridge")
        print("   🦕 Meet prehistoric pterodactyls")
        print("   🦴 Collect ancient artifacts")
        print("   🏔️ Conquer Twin Peaks")
        print("   ⚡ Survive the prehistoric world!")
    
    def setup_epic_window(self):
        """Configure window for maximum epic factor"""
        window.title = '🦕 PREHISTORIC SAN FRANCISCO - Golden Gate Pterodactyls 🌉'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        
        # Enhanced graphics for epic experience
        Entity.default_shader = basic_lighting_shader
    
    def create_prehistoric_world(self):
        """🌍 CREATE THE EPIC PREHISTORIC SAN FRANCISCO WORLD 🌍"""
        print("🌍 Generating EPIC Prehistoric San Francisco...")
        
        # San Francisco terrain with accurate topography
        self.terrain = SanFranciscoTerrain(size=400, resolution=80)
        print("   ✓ San Francisco hills, bay, and terrain created")
        
        # THE GOLDEN GATE BRIDGE - CENTERPIECE!
        self.golden_gate_bridge = GoldenGateBridge()
        print("   ✓ 🌉 GOLDEN GATE BRIDGE constructed!")
        
        # Iconic SF landmarks
        self.landmarks = SanFranciscoLandmarks(self.terrain)
        print("   ✓ SF landmarks: Alcatraz, Transamerica, Coit Tower added")
        
        # PTERODACTYL ECOSYSTEM!
        self.pterodactyl_ecosystem = PterodactylEcosystem()
        print("   ✓ 🦕 PTERODACTYL ECOSYSTEM activated!")
        
        # Player creature
        self.player = PrehistoricPlayer('archaeopteryx')  # Can be 'dragon' or 'pterodactyl'
        print("   ✓ Player creature ready for epic flight!")
        
        # Set up lighting and atmosphere
        DirectionalLight(
            color=color.rgb(255, 200, 150),
            rotation=(50, 45, 0)
        )
        AmbientLight(color=color.rgb(120, 100, 80))
        
        # Sky with prehistoric atmosphere
        sky = Sky(texture='sky_default')
        
        # Dynamic fog
        scene.fog_density = 0.008
        scene.fog_color = color.rgb(0.7, 0.8, 0.9)
        
        print("🌍 EPIC WORLD CREATION COMPLETE!")
        print(f"   🦕 {len(self.pterodactyl_ecosystem.get_all_pterodactyls())} pterodactyls roaming SF")
        print(f"   🌉 Golden Gate Bridge ready for epic flythroughs")
        print(f"   🏔️ Twin Peaks at 280m ready to conquer")
    
    def create_camera_system(self):
        """Epic camera system for prehistoric SF"""
        
        # Set up overhead camera following the player
        camera.parent = self.player
        camera.position = (0, 25, -30)  # Overhead view
        camera.rotation_x = 45  # Look down at angle
        
        print("🎥 Epic camera system initialized for SF flyovers")
    
    def create_ui_system(self):
        """Epic UI for prehistoric San Francisco"""
        
        # Epic score display
        self.score_text = Text(
            'Score: 0',
            parent=camera.ui,
            scale=2.5,
            color=color.gold,
            position=(0.6, 0.45, 0),
            visible=False
        )
        
        # Flight data
        self.speed_text = Text(
            'Speed: 0 m/s',
            parent=camera.ui,
            scale=1.8,
            color=color.white,
            position=(-0.85, 0.45, 0),
            visible=False
        )
        
        self.altitude_text = Text(
            'Altitude: 0 m',
            parent=camera.ui,
            scale=1.8,
            color=color.white,
            position=(-0.85, 0.4, 0),
            visible=False
        )
        
        # Pterodactyl reputation
        self.reputation_text = Text(
            'Pterodactyl Rep: Neutral',
            parent=camera.ui,
            scale=1.8,
            color=color.cyan,
            position=(0.55, 0.4, 0),
            visible=False
        )
        
        # Epic objectives
        self.objectives_text = Text(
            'EPIC OBJECTIVES:\n🦕 Rule the prehistoric skies!',
            parent=camera.ui,
            scale=1.4,
            color=color.yellow,
            position=(-0.9, 0.3, 0),
            visible=False
        )
        
        # Bridge flythrough counter
        self.bridge_text = Text(
            '🌉 Bridge Flythroughs: 0',
            parent=camera.ui,
            scale=1.6,
            color=color.orange,
            position=(-0.9, -0.35, 0),
            visible=False
        )
        
        # Species encounter tracker
        self.species_text = Text(
            '🦕 Species Met: 0/3',
            parent=camera.ui,
            scale=1.6,
            color=color.lime,
            position=(-0.9, -0.4, 0),
            visible=False
        )
        
        # Controls help
        self.controls_text = Text(
            '🎮 WASD=Flight | Space=Boost | Shift=Dive | E=Thermal | F=Special | ESC=Menu',
            parent=camera.ui,
            scale=1.2,
            color=color.light_gray,
            position=(-0.9, -0.45, 0),
            visible=False
        )
        
        # Epic intro message
        self.intro_text = Text(
            '🦕 WELCOME TO PREHISTORIC SAN FRANCISCO! 🌉\nPress ENTER to begin your epic adventure!',
            parent=camera.ui,
            scale=2.5,
            color=color.gold,
            position=(0, 0, 0),
            origin=(0, 0),
            visible=True
        )
    
    def create_prehistoric_collectibles(self):
        """Spawn prehistoric artifacts across San Francisco"""
        self.collectibles = []
        
        # Dinosaur eggs around Twin Peaks
        for _ in range(6):
            x = random.uniform(-20, 20)
            z = random.uniform(-20, 20)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(5, 15)
            
            egg = PrehistoricCollectible(Vec3(x, y, z), 'dino_egg')
            self.collectibles.append(egg)
        
        # Amber near Golden Gate Bridge
        for _ in range(4):
            x = random.uniform(-100, -60)
            z = random.uniform(100, 140)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(8, 25)
            
            amber = PrehistoricCollectible(Vec3(x, y, z), 'amber')
            self.collectibles.append(amber)
        
        # Fossils around landmarks
        landmark_positions = [
            Vec3(-20, 25, 100),   # Alcatraz area
            Vec3(-45, 70, 45),    # Downtown
            Vec3(-60, 90, 60),    # Telegraph Hill
        ]
        
        for pos in landmark_positions:
            for _ in range(2):
                offset = Vec3(random.uniform(-15, 15), random.uniform(5, 20), random.uniform(-15, 15))
                fossil = PrehistoricCollectible(pos + offset, 'fossil')
                self.collectibles.append(fossil)
        
        self.game_manager.total_artifacts = len(self.collectibles)
        print(f"🦴 {len(self.collectibles)} prehistoric artifacts placed across SF")
    
    def start_epic_game(self):
        """🚀 START THE EPIC PREHISTORIC ADVENTURE! 🚀"""
        self.show_menu = False
        self.intro_text.visible = False
        
        # Show all epic UI elements
        self.score_text.visible = True
        self.speed_text.visible = True
        self.altitude_text.visible = True
        self.reputation_text.visible = True
        self.objectives_text.visible = True
        self.bridge_text.visible = True
        self.species_text.visible = True
        self.controls_text.visible = True
        
        self.game_manager.game_started = True
        
        print("🦕🌉 EPIC PREHISTORIC SAN FRANCISCO ADVENTURE BEGINS! 🌉🦕")
        print("Soar with pterodactyls over the Golden Gate Bridge!")
    
    def check_prehistoric_collectibles(self):
        """Check for epic artifact collection"""
        player_pos = self.player.position
        
        for collectible in self.collectibles:
            if not collectible.collected:
                distance_to_collectible = distance(player_pos, collectible.position)
                
                if distance_to_collectible < 4:  # Collection radius
                    if collectible.collect():
                        self.game_manager.collect_artifact(collectible.collectible_type)
                        print(f"🦴 EPIC! Collected {collectible.collectible_type}! Score: {self.game_manager.score}")
    
    def update(self):
        """🔄 EPIC MAIN UPDATE LOOP 🔄"""
        if self.show_menu:
            return
        
        if not self.game_manager.game_paused:
            # Update pterodactyl ecosystem
            all_pterodactyls = self.pterodactyl_ecosystem.get_all_pterodactyls()
            self.pterodactyl_ecosystem.update(self.player.position)
            
            # Update player with pterodactyl interactions
            nearby_pterodactyls = [p for p in all_pterodactyls 
                                 if distance(self.player.position, p.position) < 50]
            flight_data = self.player.update(nearby_pterodactyls)
            
            # Update game manager
            self.game_manager.update(self.player, all_pterodactyls)
            
            # Check collectibles
            self.check_prehistoric_collectibles()
            
            # Update collectibles
            for collectible in self.collectibles:
                collectible.update()
        
        # Update epic UI
        self.update_epic_ui()
    
    def update_epic_ui(self):
        """Update all epic UI elements"""
        if not self.game_manager.game_started:
            return
        
        # Get flight data
        speed = distance(self.player.velocity, Vec3(0, 0, 0))
        
        # Update UI elements
        self.score_text.text = f'Score: {self.game_manager.score:,}'
        self.speed_text.text = f'Speed: {speed:.1f} m/s'
        self.altitude_text.text = f'Altitude: {self.player.position.y:.1f} m'
        
        # Pterodactyl reputation
        rep = self.game_manager.pterodactyl_reputation
        if rep > 0.5:
            rep_status = "🦕 ALLIED"
            rep_color = color.green
        elif rep < -0.5:
            rep_status = "⚔️ HOSTILE"
            rep_color = color.red
        else:
            rep_status = "😐 NEUTRAL"
            rep_color = color.cyan
        
        self.reputation_text.text = f'Pterodactyl Rep: {rep_status}'
        self.reputation_text.color = rep_color
        
        # Bridge flythroughs
        self.bridge_text.text = f'🌉 Bridge Flythroughs: {self.game_manager.bridge_flythroughs}'
        
        # Species encounters
        species_count = len(self.game_manager.species_encountered)
        self.species_text.text = f'🦕 Species Met: {species_count}/3'
        
        # Epic objectives
        completed_text = "🏆 COMPLETED:\n"
        for obj in self.game_manager.completed_objectives:
            completed_text += f"✓ {obj}\n"
        
        remaining_text = "\n🎯 REMAINING:\n"
        for obj in self.game_manager.objectives:
            if obj not in self.game_manager.completed_objectives:
                remaining_text += f"• {obj}\n"
        
        self.objectives_text.text = completed_text + remaining_text
    
    def toggle_pause(self):
        """Toggle epic pause"""
        if not self.game_manager.game_started:
            return
            
        self.game_manager.game_paused = not self.game_manager.game_paused

# =============================================================================
# 🚀 EPIC EXECUTION - LAUNCH THE PREHISTORIC ADVENTURE! 🚀
# =============================================================================

# Create the epic game instance
prehistoric_sf_game = PrehistoricSanFranciscoSimulator()

def input(key):
    """🎮 EPIC INPUT HANDLING 🎮"""
    if key == 'escape':
        if prehistoric_sf_game.show_menu:
            quit()
        else:
            prehistoric_sf_game.toggle_pause()
    
    elif key == 'enter':
        if prehistoric_sf_game.show_menu:
            prehistoric_sf_game.start_epic_game()
    
    elif key == 'f1':
        # Toggle HUD
        if prehistoric_sf_game.game_manager.game_started:
            prehistoric_sf_game.score_text.visible = not prehistoric_sf_game.score_text.visible
            prehistoric_sf_game.speed_text.visible = not prehistoric_sf_game.speed_text.visible
            prehistoric_sf_game.altitude_text.visible = not prehistoric_sf_game.altitude_text.visible
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen

def update():
    """🔄 MAIN EPIC UPDATE FUNCTION 🔄"""
    prehistoric_sf_game.update()

# 🚀 EPIC EXECUTION - LAUNCH THE PREHISTORIC ADVENTURE! 🚀
if __name__ == '__main__':
    print("🦕🌉 LAUNCHING PREHISTORIC SAN FRANCISCO! 🌉🦕")
    print("MAXIMUM EPIC FACTOR ACHIEVED")
    print("WE ARE LEGION - PREPARE FOR GREATNESS!")
    app.run() 