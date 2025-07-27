#!/usr/bin/env python3
"""
Flying Squirrel Flight Simulator
A 3D flight simulator game featuring a flying squirrel with realistic gliding physics.
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
import random
from noise import pnoise2

app = Ursina()

# Game settings
WORLD_SIZE = 200
TERRAIN_SCALE = 0.1
TREE_COUNT = 300
WIND_STRENGTH = 0.5

class FlyingSquirrel(Entity):
    """Flying squirrel character with realistic gliding physics"""
    
    def __init__(self):
        super().__init__()
        
        # Create squirrel model (simplified for MVP)
        self.model = 'cube'
        self.color = color.brown
        self.scale = (1.5, 0.5, 0.8)
        
        # Physics properties
        self.velocity = Vec3(0, 0, 0)
        self.speed = 0
        self.max_speed = 20
        self.glide_ratio = 4.0  # How far squirrel can glide vs altitude lost
        self.lift_coefficient = 0.8
        self.drag_coefficient = 0.02
        
        # Flight state
        self.altitude = 20
        self.pitch = 0
        self.roll = 0
        self.yaw = 0
        
        # Position squirrel above terrain
        self.position = Vec3(0, 20, 0)
        
        # Add wings (visual representation)
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.dark_gray,
            scale=(2, 0.1, 1),
            position=(-1.2, 0, 0),
            rotation=(0, 0, 20)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube', 
            color=color.dark_gray,
            scale=(2, 0.1, 1),
            position=(1.2, 0, 0),
            rotation=(0, 0, -20)
        )
        
        # Tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.brown,
            scale=(0.3, 0.3, 1.5),
            position=(0, 0, -1)
        )
    
    def update(self):
        """Update squirrel physics and movement"""
        dt = time.dt
        
        # Get input for flight control
        self.handle_input()
        
        # Apply physics
        self.apply_physics(dt)
        
        # Update visual rotation based on flight dynamics
        self.rotation_x = math.degrees(self.pitch)
        self.rotation_y = math.degrees(self.yaw) 
        self.rotation_z = math.degrees(self.roll)
        
        # Animate wings based on speed
        wing_flap = math.sin(time.time() * self.speed * 0.5) * 10
        self.left_wing.rotation_z = 20 + wing_flap
        self.right_wing.rotation_z = -20 - wing_flap
        
        # Keep squirrel above ground
        if self.y < 1:
            self.y = 1
            self.velocity.y = max(0, self.velocity.y)
    
    def handle_input(self):
        """Handle player input for flight control"""
        # Pitch control (nose up/down)
        if held_keys['w']:
            self.pitch += 2 * time.dt
        if held_keys['s']:
            self.pitch -= 2 * time.dt
        
        # Yaw control (turn left/right)
        if held_keys['a']:
            self.yaw += 2 * time.dt
        if held_keys['d']:
            self.yaw -= 2 * time.dt
            
        # Roll for turns
        if held_keys['a']:
            self.roll = lerp(self.roll, 0.3, 5 * time.dt)
        elif held_keys['d']:
            self.roll = lerp(self.roll, -0.3, 5 * time.dt)
        else:
            self.roll = lerp(self.roll, 0, 5 * time.dt)
        
        # Glide boost
        if held_keys['space']:
            self.velocity += Vec3(0, 0.5, 0) * time.dt
            
        # Dive for speed
        if held_keys['shift']:
            self.pitch -= 1 * time.dt
    
    def apply_physics(self, dt):
        """Apply realistic gliding physics"""
        # Gravity
        gravity = Vec3(0, -9.8, 0)
        
        # Forward thrust based on pitch (diving = more speed)
        thrust_force = Vec3(0, 0, max(0, -self.pitch * 10))
        
        # Rotate thrust based on yaw
        thrust_force = Vec3(
            thrust_force.z * math.sin(self.yaw),
            thrust_force.y,
            thrust_force.z * math.cos(self.yaw)
        )
        
        # Lift force (perpendicular to velocity)
        if self.speed > 0:
            lift_magnitude = self.lift_coefficient * self.speed * 0.1
            lift_force = Vec3(0, lift_magnitude, 0)
        else:
            lift_force = Vec3(0, 0, 0)
        
        # Drag force (opposite to velocity)
        drag_force = -self.velocity * self.drag_coefficient * self.speed
        
        # Wind effects (simple)
        wind_force = Vec3(
            math.sin(time.time() * 0.5) * WIND_STRENGTH,
            0,
            math.cos(time.time() * 0.3) * WIND_STRENGTH
        )
        
        # Combine all forces
        total_force = gravity + thrust_force + lift_force + drag_force + wind_force
        
        # Update velocity
        self.velocity += total_force * dt
        
        # Limit maximum speed
        self.speed = distance(self.velocity, Vec3(0, 0, 0))
        if self.speed > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
            self.speed = self.max_speed
        
        # Update position
        self.position += self.velocity * dt
        
        # Store altitude for UI
        self.altitude = self.y

class Terrain(Entity):
    """Procedurally generated terrain using noise"""
    
    def __init__(self):
        super().__init__()
        
        # Generate terrain mesh
        vertices = []
        triangles = []
        uvs = []
        
        # Create height map using Perlin noise
        resolution = 50
        for i in range(resolution):
            for j in range(resolution):
                x = (i - resolution//2) * WORLD_SIZE / resolution
                z = (j - resolution//2) * WORLD_SIZE / resolution
                
                # Generate height using noise
                height = pnoise2(x * TERRAIN_SCALE, z * TERRAIN_SCALE) * 20
                
                vertices.append(Vec3(x, height, z))
                uvs.append((i/resolution, j/resolution))
                
                # Create triangles
                if i < resolution-1 and j < resolution-1:
                    # Two triangles per quad
                    v1 = i * resolution + j
                    v2 = (i+1) * resolution + j  
                    v3 = i * resolution + (j+1)
                    v4 = (i+1) * resolution + (j+1)
                    
                    triangles.extend([v1, v2, v3, v2, v4, v3])
        
        # Create the mesh
        self.model = Mesh(vertices=vertices, triangles=triangles, uvs=uvs)
        self.color = color.green
        self.texture = 'grass'

class Tree(Entity):
    """Simple tree model for environment"""
    
    def __init__(self, position):
        super().__init__()
        
        # Tree trunk
        self.trunk = Entity(
            parent=self,
            model='cube',
            color=color.brown,
            scale=(0.5, 4, 0.5),
            position=(0, 2, 0)
        )
        
        # Tree leaves
        self.leaves = Entity(
            parent=self,
            model='cube',
            color=color.green,
            scale=(3, 3, 3),
            position=(0, 5, 0)
        )
        
        self.position = position

class GameUI(Entity):
    """Game user interface showing flight data"""
    
    def __init__(self, squirrel):
        super().__init__(parent=camera.ui)
        self.squirrel = squirrel
        
        # Speed indicator
        self.speed_text = Text(
            'Speed: 0 m/s',
            position=(-0.8, 0.45),
            scale=2,
            color=color.white
        )
        
        # Altitude indicator  
        self.altitude_text = Text(
            'Altitude: 0 m',
            position=(-0.8, 0.4),
            scale=2,
            color=color.white
        )
        
        # Controls help
        self.controls_text = Text(
            'Controls: WASD = Pitch/Yaw | Space = Boost | Shift = Dive | ESC = Exit',
            position=(-0.9, -0.45),
            scale=1.5,
            color=color.light_gray
        )
    
    def update(self):
        """Update UI elements"""
        self.speed_text.text = f'Speed: {self.squirrel.speed:.1f} m/s'
        self.altitude_text.text = f'Altitude: {self.squirrel.altitude:.1f} m'

# Initialize game world
def setup_game():
    """Set up the game world and entities"""
    
    # Create terrain
    terrain = Terrain()
    
    # Create flying squirrel
    squirrel = FlyingSquirrel()
    
    # Create trees randomly across terrain
    for _ in range(TREE_COUNT):
        x = random.uniform(-WORLD_SIZE//2, WORLD_SIZE//2)
        z = random.uniform(-WORLD_SIZE//2, WORLD_SIZE//2)
        y = pnoise2(x * TERRAIN_SCALE, z * TERRAIN_SCALE) * 20
        
        tree = Tree(Vec3(x, y, z))
    
    # Set up camera to follow squirrel
    camera.parent = squirrel
    camera.position = (0, 2, -8)
    camera.rotation_x = 10
    
    # Create UI
    ui = GameUI(squirrel)
    
    # Set up lighting
    DirectionalLight(rotation=(45, 45, 0), color=color.white)
    AmbientLight(color=color.rgb(100, 100, 100))
    
    # Sky
    sky = Sky(texture='sky_default')
    
    return squirrel, ui

# Input handling
def input(key):
    """Handle key inputs"""
    if key == 'escape':
        quit()

# Main game setup
if __name__ == '__main__':
    # Window settings
    window.title = 'Flying Squirrel Flight Simulator'
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = True
    
    # Setup game
    squirrel, ui = setup_game()
    
    # Start game loop
    app.run() 