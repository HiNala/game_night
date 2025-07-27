"""
San Francisco Prehistoric World Generator
Epic 3D recreation of San Francisco with Golden Gate Bridge and pterodactyl ecosystem.
Built by senior developers for maximum epic factor.
"""

from ursina import *
import math
import random
from noise import pnoise2
import numpy as np

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
                    height -= 20 * bay_factor  # Below sea level
                
                # Pacific Ocean (west side)
                if x < -120:
                    ocean_factor = max(0, (x + 120) / -20)
                    height -= 15 * ocean_factor
                
                # Add noise for realistic terrain variation
                height += pnoise2(x * 0.01, z * 0.01) * 8
                height += pnoise2(x * 0.03, z * 0.03) * 3
                
                # Ensure minimum ground level
                height = max(height, -25)  # Allow underwater areas
                
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
                    colors.append(color.rgb(0.1, 0.3, 0.6))  # Bay water - deep blue
                elif y < 0:
                    colors.append(color.rgb(0.2, 0.5, 0.8))  # Shallow water
                elif y < 20:
                    colors.append(color.rgb(0.8, 0.7, 0.5))  # Beach/low areas - sand
                elif y < 50:
                    colors.append(color.rgb(0.4, 0.6, 0.3))  # Low hills - green
                elif y < 100:
                    colors.append(color.rgb(0.5, 0.5, 0.4))  # Mid hills - brown
                else:
                    colors.append(color.rgb(0.6, 0.6, 0.6))  # High peaks - gray
        
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
    """Detailed 3D model of the iconic Golden Gate Bridge"""
    
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
            parent=self,
            model='cube',
            color=color.rgb(196, 76, 25),  # International Orange
            scale=(self.bridge_length, 2, self.bridge_width),
            position=(0, 25, 0)
        )
        
        # North Tower
        self.north_tower = Entity(
            parent=self,
            model='cube',
            color=color.rgb(196, 76, 25),
            scale=(6, self.tower_height, 4),
            position=(-30, self.tower_height/2, 0)
        )
        
        # South Tower  
        self.south_tower = Entity(
            parent=self,
            model='cube',
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
        
        # Main cables (simplified as cylinders)
        for side in [-2, 2]:
            # North to South main cable
            main_cable = Entity(
                parent=self,
                model='cube',
                color=color.rgb(150, 150, 150),
                scale=(self.bridge_length + 20, 0.5, 0.5),
                position=(0, cable_height, side)
            )
            
            # Vertical suspension cables
            for i in range(-50, 51, 10):
                cable_length = cable_height - 25 + abs(i) * 0.1  # Catenary curve approximation
                vertical_cable = Entity(
                    parent=self,
                    model='cube',
                    color=color.rgb(120, 120, 120),
                    scale=(0.2, cable_length, 0.2),
                    position=(i, 25 + cable_length/2, side)
                )
    
    def create_bridge_approaches(self):
        """Create the approach spans and roadways"""
        # Marin approach (north)
        marin_approach = Entity(
            parent=self,
            model='cube',
            color=color.rgb(160, 160, 160),
            scale=(40, 1.5, self.bridge_width),
            position=(-80, 20, 0)
        )
        
        # San Francisco approach (south)
        sf_approach = Entity(
            parent=self,
            model='cube',
            color=color.rgb(160, 160, 160),
            scale=(40, 1.5, self.bridge_width),
            position=(80, 20, 0)
        )
    
    def add_bridge_details(self):
        """Add Art Deco architectural details"""
        # Tower tops with Art Deco styling
        for tower_x in [-30, 30]:
            tower_top = Entity(
                parent=self,
                model='cube',
                color=color.rgb(180, 60, 20),
                scale=(8, 4, 6),
                position=(tower_x, self.tower_height + 2, 0)
            )
            
            # Tower lights
            for light_y in range(10, int(self.tower_height), 15):
                light = Entity(
                    parent=self,
                    model='sphere',
                    color=color.yellow,
                    scale=0.5,
                    position=(tower_x + 3.5, light_y, 0)
                )

class SanFranciscoLandmarks:
    """Iconic San Francisco landmarks and buildings"""
    
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
        
        # Lombard Street (curved road)
        self.create_lombard_street()
        
        # SF-Oakland Bay Bridge
        self.create_bay_bridge()
    
    def create_alcatraz(self, position):
        """The infamous island prison"""
        # Island base
        island = Entity(
            model='cube',
            color=color.rgb(0.5, 0.4, 0.3),
            scale=(15, 3, 12),
            position=position
        )
        
        # Prison building
        prison = Entity(
            model='cube',
            color=color.rgb(0.6, 0.6, 0.5),
            scale=(8, 6, 10),
            position=position + Vec3(0, 4.5, 0)
        )
        
        self.landmarks.extend([island, prison])
    
    def create_transamerica_pyramid(self, position):
        """The iconic pyramid skyscraper"""
        # Base
        base = Entity(
            model='cube',
            color=color.rgb(0.9, 0.9, 0.8),
            scale=(8, 20, 8),
            position=position + Vec3(0, 10, 0)
        )
        
        # Pyramid top (simplified)
        pyramid = Entity(
            model='cube',
            color=color.rgb(0.95, 0.95, 0.85),
            scale=(6, 30, 6),
            position=position + Vec3(0, 35, 0)
        )
        
        self.landmarks.extend([base, pyramid])
    
    def create_coit_tower(self, position):
        """The Art Deco tower on Telegraph Hill"""
        tower = Entity(
            model='cube',
            color=color.rgb(0.8, 0.8, 0.7),
            scale=(3, 25, 3),
            position=position + Vec3(0, 12.5, 0)
        )
        
        # Tower top
        tower_top = Entity(
            model='cube',
            color=color.rgb(0.7, 0.7, 0.6),
            scale=(4, 3, 4),
            position=position + Vec3(0, 26.5, 0)
        )
        
        self.landmarks.extend([tower, tower_top])
    
    def create_lombard_street(self):
        """The world's crookedest street"""
        # Simplified curved road segments
        for i in range(8):
            angle = i * 45
            x = -35 + math.sin(math.radians(angle)) * 3
            z = 45 + i * 2
            y = self.terrain.get_height_at_position(x, z)
            
            road_segment = Entity(
                model='cube',
                color=color.rgb(0.3, 0.3, 0.3),
                scale=(2, 0.5, 3),
                position=Vec3(x, y + 0.25, z),
                rotation_y=angle
            )
            self.landmarks.append(road_segment)
    
    def create_bay_bridge(self):
        """San Francisco-Oakland Bay Bridge"""
        bridge_y = 15
        
        # Western span
        west_span = Entity(
            model='cube',
            color=color.rgb(120, 120, 120),
            scale=(80, 2, 6),
            position=Vec3(40, bridge_y, 80)
        )
        
        # Eastern span
        east_span = Entity(
            model='cube',
            color=color.rgb(120, 120, 120),
            scale=(60, 2, 6),
            position=Vec3(110, bridge_y, 80)
        )
        
        # Support towers
        for tower_x in [0, 80, 140]:
            tower = Entity(
                model='cube',
                color=color.rgb(100, 100, 100),
                scale=(4, 40, 3),
                position=Vec3(tower_x, 35, 80)
            )
            self.landmarks.append(tower)
        
        self.landmarks.extend([west_span, east_span])

class SanFranciscoAtmosphere(Entity):
    """Prehistoric atmospheric effects for San Francisco"""
    
    def __init__(self):
        super().__init__()
        
        self.setup_prehistoric_lighting()
        self.create_fog_system()
        self.add_atmospheric_particles()
    
    def setup_prehistoric_lighting(self):
        """Dramatic prehistoric lighting"""
        # Main sun with warmer, more primitive feel
        self.sun = DirectionalLight(
            color=color.rgb(255, 200, 150),  # Warmer, more orange
            rotation=(50, 45, 0)
        )
        
        # Ambient light with prehistoric tint
        self.ambient = AmbientLight(
            color=color.rgb(120, 100, 80)   # Warmer ambient
        )
        
        # Sky with prehistoric atmosphere
        self.sky = Sky(texture='sky_default')
    
    def create_fog_system(self):
        """San Francisco's famous fog with prehistoric mystery"""
        # Dynamic fog that moves through the Golden Gate
        scene.fog_density = 0.008
        scene.fog_color = color.rgb(0.7, 0.8, 0.9)
        
        # Fog layers for dramatic effect
        self.fog_layers = []
        for i in range(5):
            fog_layer = Entity(
                model='cube',
                color=color.rgba(200, 220, 240, 30),
                scale=(200, 5, 200),
                position=(0, 20 + i*8, 0)
            )
            self.fog_layers.append(fog_layer)
    
    def add_atmospheric_particles(self):
        """Prehistoric atmospheric particles"""
        # Flying ash/dust particles
        self.particles = []
        for _ in range(50):
            particle = Entity(
                model='cube',
                color=color.rgba(255, 240, 200, 100),
                scale=0.1,
                position=(
                    random.uniform(-200, 200),
                    random.uniform(10, 100),
                    random.uniform(-200, 200)
                )
            )
            particle.velocity = Vec3(
                random.uniform(-1, 1),
                random.uniform(-0.5, 0.5),
                random.uniform(-1, 1)
            )
            self.particles.append(particle)
    
    def update(self):
        """Update atmospheric effects"""
        # Move fog layers
        for i, fog_layer in enumerate(self.fog_layers):
            fog_layer.x += math.sin(time.time() * 0.3 + i) * 0.1
            fog_layer.z += math.cos(time.time() * 0.2 + i) * 0.05
        
        # Move particles
        for particle in self.particles:
            particle.position += particle.velocity * time.dt
            
            # Reset particles that drift too far
            if distance(particle.position, Vec3(0, 50, 0)) > 300:
                particle.position = Vec3(
                    random.uniform(-200, 200),
                    random.uniform(10, 100),
                    random.uniform(-200, 200)
                )

class SanFranciscoWaterSystem:
    """Bay water and ocean effects"""
    
    def __init__(self, terrain):
        self.terrain = terrain
        self.create_water_system()
    
    def create_water_system(self):
        """Create dynamic bay and ocean water"""
        
        # San Francisco Bay
        self.bay_water = Entity(
            model='cube',
            color=color.rgba(0.2, 0.4, 0.8, 180),
            scale=(120, 1, 80),
            position=(0, -2, 80)
        )
        
        # Pacific Ocean
        self.ocean_water = Entity(
            model='cube',
            color=color.rgba(0.1, 0.3, 0.7, 200),
            scale=(100, 1, 200),
            position=(-150, -5, 0)
        )
        
        # Animated waves (simplified)
        self.wave_time = 0
    
    def update(self):
        """Update water animations"""
        self.wave_time += time.dt
        
        # Simple wave animation
        wave_height = math.sin(self.wave_time * 2) * 0.5
        self.bay_water.y = -2 + wave_height
        self.ocean_water.y = -5 + wave_height * 0.8 