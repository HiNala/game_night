"""
Enhanced Environment System - Redesigned for Better 3D Depth and Sparsity
Advanced terrain generation with varied biomes and clear visual landmarks.
"""

from ursina import *
import math
import random
from noise import pnoise2

class EnhancedTerrain(Entity):
    """Redesigned terrain with better 3D depth perception and varied landscapes"""
    
    def __init__(self, size=300, resolution=40):
        super().__init__()
        self.size = size
        self.resolution = resolution
        self.scale = 0.02  # Larger scale for more varied terrain
        self.height_multiplier = 40  # More dramatic height differences
        
        # Generate height map with distinct biomes
        self.height_map = self.generate_varied_height_map()
        
        # Create terrain mesh with better visual variety
        self.create_detailed_terrain_mesh()
        
        # Add visual materials
        self.setup_terrain_materials()
    
    def generate_varied_height_map(self):
        """Generate height map with distinct biomes and features"""
        height_map = []
        
        for i in range(self.resolution + 1):
            row = []
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                
                # Base terrain with multiple octaves
                height = 0
                amplitude = 1
                frequency = self.scale
                
                # Large-scale features (mountains, valleys)
                height += pnoise2(x * frequency * 0.3, z * frequency * 0.3) * amplitude * 2
                
                # Medium-scale features (hills)
                amplitude *= 0.6
                frequency *= 2
                height += pnoise2(x * frequency, z * frequency) * amplitude
                
                # Small-scale details
                amplitude *= 0.4
                frequency *= 3
                height += pnoise2(x * frequency, z * frequency) * amplitude
                
                # Create distinct biomes
                distance_from_center = math.sqrt(x*x + z*z)
                
                # Central valley (good for starting)
                if distance_from_center < 30:
                    height *= 0.3
                    height += 5  # Raised valley floor
                
                # Mountain ranges at edges
                elif distance_from_center > 120:
                    height *= 1.8
                    height += 20
                
                # Rolling hills in between
                else:
                    height *= 1.0
                    height += 10
                
                # Scale final height
                height *= self.height_multiplier
                
                # Ensure reasonable minimum height
                height = max(height, 0)
                
                row.append(height)
            height_map.append(row)
        
        return height_map
    
    def create_detailed_terrain_mesh(self):
        """Create terrain mesh with better color coding for different elevations"""
        vertices = []
        triangles = []
        uvs = []
        colors = []
        
        # Generate vertices, UVs, and colors
        for i in range(self.resolution + 1):
            for j in range(self.resolution + 1):
                x = (i - self.resolution/2) * self.size / self.resolution
                z = (j - self.resolution/2) * self.size / self.resolution
                y = self.height_map[i][j]
                
                vertices.append(Vec3(x, y, z))
                uvs.append((i/self.resolution, j/self.resolution))
                
                # Color based on height and slope
                if y < 5:
                    colors.append(color.rgb(0.3, 0.6, 0.2))  # Dark green for valleys
                elif y < 15:
                    colors.append(color.rgb(0.4, 0.7, 0.3))  # Medium green
                elif y < 30:
                    colors.append(color.rgb(0.6, 0.5, 0.3))  # Brown for hills
                else:
                    colors.append(color.rgb(0.7, 0.7, 0.7))  # Gray for mountains
        
        # Generate triangles
        for i in range(self.resolution):
            for j in range(self.resolution):
                v1 = i * (self.resolution + 1) + j
                v2 = (i + 1) * (self.resolution + 1) + j
                v3 = i * (self.resolution + 1) + (j + 1)
                v4 = (i + 1) * (self.resolution + 1) + (j + 1)
                
                triangles.extend([v1, v2, v3, v2, v4, v3])
        
        # Create mesh with vertex colors
        self.model = Mesh(
            vertices=vertices,
            triangles=triangles,
            uvs=uvs,
            colors=colors
        )
        self.model.generate()
    
    def setup_terrain_materials(self):
        """Set up terrain visual properties"""
        self.color = color.white  # Use vertex colors
        self.texture_scale = 10
    
    def get_height_at_position(self, x, z):
        """Get terrain height at world position with bounds checking"""
        # Convert world position to height map coordinates
        map_x = int((x + self.size/2) * self.resolution / self.size)
        map_z = int((z + self.size/2) * self.resolution / self.size)
        
        # Clamp to valid range
        map_x = max(0, min(self.resolution, map_x))
        map_z = max(0, min(self.resolution, map_z))
        
        return self.height_map[map_x][map_z]

class SparseForest:
    """Much sparser forest with strategic tree placement for visual landmarks"""
    
    def __init__(self, terrain, tree_count=80):  # Reduced from 400
        self.terrain = terrain
        self.tree_count = tree_count
        self.trees = []
        self.tree_groups = []  # Groups of trees for visual clustering
        
        self.generate_sparse_forest()
    
    def generate_sparse_forest(self):
        """Generate strategically placed trees in clusters"""
        
        # Create tree clusters for visual landmarks
        cluster_count = 12
        trees_per_cluster = 4-8
        
        for cluster_id in range(cluster_count):
            # Choose cluster center
            cluster_x = random.uniform(-self.terrain.size/3, self.terrain.size/3)
            cluster_z = random.uniform(-self.terrain.size/3, self.terrain.size/3)
            cluster_radius = random.uniform(8, 15)
            
            cluster_trees = []
            
            for _ in range(random.randint(4, 8)):
                # Place tree within cluster
                angle = random.uniform(0, 2 * math.pi)
                distance = random.uniform(0, cluster_radius)
                
                x = cluster_x + math.cos(angle) * distance
                z = cluster_z + math.sin(angle) * distance
                y = self.terrain.get_height_at_position(x, z)
                
                # Only place trees on suitable terrain
                if 2 < y < 35:  # Not in valleys, not on high peaks
                    tree_type = random.choice(['oak', 'pine', 'birch'])
                    tree = DetailedTree(Vec3(x, y, z), tree_type)
                    self.trees.append(tree)
                    cluster_trees.append(tree)
            
            self.tree_groups.append(cluster_trees)
        
        # Add some isolated landmark trees
        for _ in range(20):
            x = random.uniform(-self.terrain.size/2 + 30, self.terrain.size/2 - 30)
            z = random.uniform(-self.terrain.size/2 + 30, self.terrain.size/2 - 30)
            y = self.terrain.get_height_at_position(x, z)
            
            if 5 < y < 25:  # Mid-elevation trees
                tree_type = random.choice(['oak', 'pine'])
                tree = DetailedTree(Vec3(x, y, z), tree_type, scale_multiplier=1.3)
                self.trees.append(tree)

class DetailedTree(Entity):
    """Enhanced tree model with better scaling for overhead view"""
    
    def __init__(self, position, tree_type='oak', scale_multiplier=1.0):
        super().__init__()
        self.position = position
        self.tree_type = tree_type
        self.scale_multiplier = scale_multiplier
        
        # More varied tree characteristics
        self.height_scale = random.uniform(0.8, 1.6) * scale_multiplier
        self.width_scale = random.uniform(0.6, 1.4) * scale_multiplier
        
        self.create_detailed_tree_model()
    
    def create_detailed_tree_model(self):
        """Create more detailed tree model optimized for overhead view"""
        
        # Trunk - taller and more visible from above
        trunk_height = 6 * self.height_scale
        self.trunk = Entity(
            parent=self,
            model='cube',
            color=color.rgb(82, 51, 23),  # Darker brown
            scale=(0.4 * self.width_scale, trunk_height, 0.4 * self.width_scale),
            position=(0, trunk_height/2, 0)
        )
        
        # Canopy - optimized for overhead viewing
        if self.tree_type == 'oak':
            # Broad, spreading canopy
            self.canopy = Entity(
                parent=self,
                model='cube',
                color=color.rgb(34, 139, 34),
                scale=(4 * self.width_scale, 2.5 * self.height_scale, 4 * self.width_scale),
                position=(0, trunk_height + 1, 0)
            )
        elif self.tree_type == 'pine':
            # Tall, narrow conical shape
            for i in range(3):
                level_width = (3 - i * 0.7) * self.width_scale
                pine_section = Entity(
                    parent=self,
                    model='cube',
                    color=color.rgb(0, 100, 0),
                    scale=(level_width, 1.5, level_width),
                    position=(0, trunk_height + i * 1.2, 0)
                )
        else:  # birch
            # Medium canopy with lighter color
            self.canopy = Entity(
                parent=self,
                model='cube',
                color=color.rgb(50, 205, 50),
                scale=(3 * self.width_scale, 2 * self.height_scale, 3 * self.width_scale),
                position=(0, trunk_height + 0.5, 0)
            )
            
            # White trunk for birch
            self.trunk.color = color.rgb(240, 240, 240)

class OverheadSkySystem(Entity):
    """Simplified sky system optimized for overhead view"""
    
    def __init__(self):
        super().__init__()
        
        # Sky dome with better contrast for overhead view
        self.sky_dome = Sky(texture='sky_default')
        
        # Directional lighting optimized for visibility
        self.main_light = DirectionalLight(
            color=color.white,
            rotation=(60, 45, 0)  # Angled for good shadow definition
        )
        
        # Ambient light for overall visibility
        self.ambient_light = AmbientLight(
            color=color.rgb(120, 120, 140)
        )
        
        # Atmospheric settings
        self.setup_atmosphere()
    
    def setup_atmosphere(self):
        """Set up atmospheric effects for overhead view"""
        # Reduced fog for better long-distance visibility
        scene.fog_density = 0.003
        scene.fog_color = color.rgb(0.8, 0.9, 1.0)

class EnvironmentalLandmarks:
    """Create visual landmarks for navigation"""
    
    def __init__(self, terrain):
        self.terrain = terrain
        self.landmarks = []
        
        self.create_landmarks()
    
    def create_landmarks(self):
        """Create distinctive landmarks for navigation"""
        
        # Large rock formations
        for _ in range(8):
            x = random.uniform(-100, 100)
            z = random.uniform(-100, 100)
            y = self.terrain.get_height_at_position(x, z)
            
            if y > 15:  # Only on elevated terrain
                rock = Entity(
                    model='cube',
                    color=color.rgb(100, 100, 100),
                    scale=(random.uniform(3, 6), random.uniform(4, 8), random.uniform(3, 6)),
                    position=(x, y + 2, z)
                )
                self.landmarks.append(rock)
        
        # Clearings (large open areas)
        for _ in range(5):
            x = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            y = self.terrain.get_height_at_position(x, z)
            
            # Create clearing marker (could be a lake or field)
            clearing = Entity(
                model='cube',
                color=color.rgb(0.2, 0.4, 0.8),  # Blue for water
                scale=(15, 0.2, 15),
                position=(x, y + 0.1, z)
            )
            self.landmarks.append(clearing)

class ParticleSystem:
    """Optimized particle system for overhead view"""
    
    def __init__(self):
        self.particles = []
        self.max_particles = 30  # Reduced for overhead view
    
    def create_wind_particles(self, position, count=3):
        """Create subtle wind effect particles"""
        for _ in range(count):
            particle = Entity(
                model='cube',
                color=color.rgba(255, 255, 255, 80),
                scale=0.15,
                position=position + Vec3(
                    random.uniform(-5, 5),
                    random.uniform(0, 3), 
                    random.uniform(-5, 5)
                )
            )
            
            particle.velocity = Vec3(
                random.uniform(-3, 3),
                random.uniform(-0.5, 0.5),
                random.uniform(-3, 3)
            )
            
            particle.life = 3.0
            self.particles.append(particle)
    
    def update(self):
        """Update particle system"""
        for particle in self.particles[:]:
            particle.life -= time.dt
            
            if particle.life <= 0:
                destroy(particle)
                self.particles.remove(particle)
            else:
                particle.position += particle.velocity * time.dt
                
                # Fade out
                alpha = int(particle.life * 26.7)  # 80/3
                particle.color = color.rgba(255, 255, 255, alpha) 