"""
Enhanced Environment System
Advanced terrain generation, vegetation, and atmospheric effects.
"""

from ursina import *
import math
import random
from noise import pnoise2

class EnhancedTerrain(Entity):
    """Advanced terrain with multiple biomes and detail levels"""
    
    def __init__(self, size=200, resolution=80):
        super().__init__()
        self.size = size
        self.resolution = resolution
        self.scale = 0.05
        self.height_multiplier = 25
        
        # Generate height map
        self.height_map = self.generate_height_map()
        
        # Create terrain mesh
        self.create_terrain_mesh()
        
        # Add texture and materials
        self.setup_materials()
    
    def generate_height_map(self):
        """Generate detailed height map using multiple octaves of noise"""
        height_map = []
        
        for i in range(self.resolution + 1):
            row = []
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                
                # Multiple octaves for realistic terrain
                height = 0
                amplitude = 1
                frequency = self.scale
                
                # Base terrain
                height += pnoise2(x * frequency, z * frequency) * amplitude
                
                # Add hills
                amplitude *= 0.5
                frequency *= 2
                height += pnoise2(x * frequency, z * frequency) * amplitude
                
                # Add fine details
                amplitude *= 0.5
                frequency *= 2
                height += pnoise2(x * frequency, z * frequency) * amplitude
                
                # Scale height
                height *= self.height_multiplier
                
                # Ensure minimum height above water
                height = max(height, 0)
                
                row.append(height)
            height_map.append(row)
        
        return height_map
    
    def create_terrain_mesh(self):
        """Create detailed terrain mesh with proper normals"""
        vertices = []
        triangles = []
        uvs = []
        normals = []
        
        # Generate vertices and UVs
        for i in range(self.resolution + 1):
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                y = self.height_map[i][j]
                
                vertices.append(Vec3(x, y, z))
                uvs.append((i/self.resolution, j/self.resolution))
        
        # Generate triangles and calculate normals
        for i in range(self.resolution):
            for j in range(self.resolution):
                # Vertex indices
                v1 = i * (self.resolution + 1) + j
                v2 = (i + 1) * (self.resolution + 1) + j
                v3 = i * (self.resolution + 1) + (j + 1)
                v4 = (i + 1) * (self.resolution + 1) + (j + 1)
                
                # Two triangles per quad
                triangles.extend([v1, v2, v3, v2, v4, v3])
                
                # Calculate normals for lighting
                if i < self.resolution and j < self.resolution:
                    p1 = vertices[v1]
                    p2 = vertices[v2]
                    p3 = vertices[v3]
                    
                    # Cross product for normal
                    edge1 = p2 - p1
                    edge2 = p3 - p1
                    normal = edge1.cross(edge2).normalized()
                    
                    # Add normal for each vertex (simplified)
                    for _ in range(6):  # 6 vertices in two triangles
                        normals.append(normal)
        
        # Create mesh
        self.model = Mesh(
            vertices=vertices,
            triangles=triangles,
            uvs=uvs,
            normals=normals
        )
        
        # Generate mesh
        self.model.generate()
    
    def setup_materials(self):
        """Set up terrain materials and textures"""
        # Multi-texture based on height and slope
        self.color = color.green
        
        # You could add texture blending here based on height
        # For now, using solid colors for different elevation zones
    
    def get_height_at_position(self, x, z):
        """Get terrain height at world position"""
        # Convert world position to height map coordinates
        map_x = int((x + self.size/2) * self.resolution / self.size)
        map_z = int((z + self.size/2) * self.resolution / self.size)
        
        # Clamp to valid range
        map_x = max(0, min(self.resolution, map_x))
        map_z = max(0, min(self.resolution, map_z))
        
        return self.height_map[map_x][map_z]

class DetailedTree(Entity):
    """Enhanced tree model with multiple parts and variations"""
    
    def __init__(self, position, tree_type='oak'):
        super().__init__()
        self.position = position
        self.tree_type = tree_type
        
        # Randomize tree characteristics
        self.height_scale = random.uniform(0.8, 1.4)
        self.width_scale = random.uniform(0.7, 1.2)
        
        self.create_tree_model()
    
    def create_tree_model(self):
        """Create detailed tree model with trunk and foliage"""
        
        # Trunk
        trunk_height = 4 * self.height_scale
        self.trunk = Entity(
            parent=self,
            model='cube',
            color=color.rgb(101, 67, 33),  # Brown
            scale=(0.5 * self.width_scale, trunk_height, 0.5 * self.width_scale),
            position=(0, trunk_height/2, 0)
        )
        
        # Multiple foliage levels for more realistic look
        foliage_y = trunk_height
        foliage_colors = [
            color.rgb(34, 139, 34),   # Forest green
            color.rgb(50, 205, 50),   # Lime green
            color.rgb(0, 128, 0),     # Green
        ]
        
        # Create layered foliage
        for i, foliage_color in enumerate(foliage_colors):
            foliage_size = (3.5 - i*0.5) * self.width_scale
            foliage_entity = Entity(
                parent=self,
                model='cube',
                color=foliage_color,
                scale=(foliage_size, foliage_size * 0.8, foliage_size),
                position=(0, foliage_y + i * 1.5, 0)
            )
        
        # Add some branch details
        for i in range(random.randint(2, 5)):
            branch_angle = random.uniform(0, 360)
            branch_length = random.uniform(1, 2) * self.width_scale
            branch_y = trunk_height * random.uniform(0.6, 0.9)
            
            branch = Entity(
                parent=self,
                model='cube',
                color=color.rgb(101, 67, 33),
                scale=(0.2, 0.2, branch_length),
                position=(0, branch_y, 0),
                rotation=(0, branch_angle, random.uniform(-20, 20))
            )

class Forest:
    """Manages forest generation and LOD"""
    
    def __init__(self, terrain, tree_count=400):
        self.terrain = terrain
        self.tree_count = tree_count
        self.trees = []
        
        self.generate_forest()
    
    def generate_forest(self):
        """Generate forest with realistic distribution"""
        
        for _ in range(self.tree_count):
            # Random position
            x = random.uniform(-self.terrain.size/2 + 10, self.terrain.size/2 - 10)
            z = random.uniform(-self.terrain.size/2 + 10, self.terrain.size/2 - 10)
            
            # Get terrain height at this position
            y = self.terrain.get_height_at_position(x, z)
            
            # Only place trees on suitable terrain (not too steep, not too low)
            if y > 2 and y < 20:  # Elevation constraints
                tree_type = random.choice(['oak', 'pine', 'birch'])
                tree = DetailedTree(Vec3(x, y, z), tree_type)
                self.trees.append(tree)

class SkySystem(Entity):
    """Advanced sky rendering with dynamic lighting"""
    
    def __init__(self):
        super().__init__()
        
        # Time of day (0-24 hours)
        self.time_of_day = 12.0  # Start at noon
        self.time_speed = 0.1  # How fast time passes
        
        # Sky dome
        self.sky_dome = Sky()
        
        # Sun
        self.sun = Entity(
            model='sphere',
            color=color.yellow,
            scale=3,
            position=(0, 50, 0)
        )
        
        # Directional light (sun)
        self.sun_light = DirectionalLight(
            color=color.white,
            rotation=(45, 45, 0)
        )
        
        # Ambient light
        self.ambient_light = AmbientLight(
            color=color.rgb(70, 70, 100)
        )
        
        # Atmospheric effects
        self.setup_atmosphere()
    
    def setup_atmosphere(self):
        """Set up atmospheric effects like fog"""
        # Fog for depth perception
        scene.fog_density = 0.01
        scene.fog_color = color.rgb(0.7, 0.8, 0.9)
    
    def update(self):
        """Update sky system - day/night cycle"""
        self.time_of_day += self.time_speed * time.dt
        if self.time_of_day >= 24:
            self.time_of_day = 0
        
        # Calculate sun position based on time
        sun_angle = (self.time_of_day - 6) * 15  # Degrees from horizon
        sun_azimuth = (self.time_of_day / 24) * 360  # Around the sky
        
        # Update sun position
        sun_distance = 100
        self.sun.position = (
            math.sin(math.radians(sun_azimuth)) * sun_distance,
            math.sin(math.radians(sun_angle)) * sun_distance,
            math.cos(math.radians(sun_azimuth)) * sun_distance
        )
        
        # Update lighting based on time of day
        sun_intensity = max(0, math.sin(math.radians(sun_angle)))
        
        # Adjust ambient light
        if sun_intensity > 0.1:
            # Day time
            ambient_intensity = 0.3 + sun_intensity * 0.4
            self.ambient_light.color = color.rgb(
                ambient_intensity, 
                ambient_intensity, 
                ambient_intensity * 1.1
            )
        else:
            # Night time
            self.ambient_light.color = color.rgb(0.1, 0.1, 0.15)
        
        # Update directional light
        self.sun_light.rotation = (sun_angle, sun_azimuth, 0)
        self.sun_light.color = color.rgb(
            1.0 * sun_intensity,
            0.9 * sun_intensity, 
            0.7 * sun_intensity
        )

class ParticleSystem:
    """Simple particle system for environmental effects"""
    
    def __init__(self):
        self.particles = []
        self.max_particles = 50
    
    def create_wind_particles(self, position, count=5):
        """Create wind effect particles"""
        for _ in range(count):
            particle = Entity(
                model='cube',
                color=color.rgba(255, 255, 255, 100),
                scale=0.05,
                position=position + Vec3(
                    random.uniform(-2, 2),
                    random.uniform(-1, 1), 
                    random.uniform(-2, 2)
                )
            )
            
            # Add velocity
            particle.velocity = Vec3(
                random.uniform(-5, 5),
                random.uniform(-1, 1),
                random.uniform(-5, 5)
            )
            
            particle.life = 2.0  # 2 seconds
            self.particles.append(particle)
    
    def update(self):
        """Update particle system"""
        for particle in self.particles[:]:  # Copy list to avoid iteration issues
            particle.life -= time.dt
            
            if particle.life <= 0:
                destroy(particle)
                self.particles.remove(particle)
            else:
                # Update particle position
                particle.position += particle.velocity * time.dt
                
                # Fade out over time
                alpha = int(particle.life * 127.5)
                particle.color = color.rgba(255, 255, 255, alpha) 