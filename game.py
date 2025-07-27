#!/usr/bin/env python3
"""
Flying Squirrel Flight Simulator - Enhanced Version with Overhead Camera
Professional 3D flight simulator with Diablo 3-style overhead view and sparse environment.
"""

from ursina import *
import sys
import os
import math
import random

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.flying_squirrel import FlyingSquirrel
from graphics.environment import EnhancedTerrain, SparseForest, OverheadSkySystem, EnvironmentalLandmarks, ParticleSystem
from graphics.camera_system import OverheadCameraSystem, CinematicCamera, EnvironmentViewCamera
from ui.game_ui import FlightHUD, MainMenu, PauseMenu
import game_config as config

app = Ursina()

class Collectible(Entity):
    """Collectible items scattered throughout the world - enhanced for overhead view"""
    
    def __init__(self, position, collectible_type='acorn'):
        super().__init__()
        self.position = position
        self.collectible_type = collectible_type
        self.collected = False
        self.rotation_speed = 50
        
        # Larger collectibles for better overhead visibility
        base_scale = 0.5  # Increased from 0.3
        
        # Create collectible model
        if collectible_type == 'acorn':
            self.model = 'cube'
            self.color = color.brown
            self.scale = base_scale
        elif collectible_type == 'berry':
            self.model = 'sphere'
            self.color = color.red
            self.scale = base_scale * 0.8
        elif collectible_type == 'nut':
            self.model = 'cube'
            self.color = color.orange
            self.scale = base_scale * 0.9
        
        # Enhanced glow effect for overhead view
        self.glow = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(255, 255, 0, 80),
            scale=2.5  # Larger glow
        )
        
        # Add pulsing beacon effect
        self.beacon = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 255, 255, 200),
            scale=0.1,
            position=(0, 2, 0)  # Above the collectible
        )
    
    def update(self):
        """Animate collectible with enhanced effects for overhead view"""
        if not self.collected:
            self.rotation_y += self.rotation_speed * time.dt
            
            # Bob up and down
            self.y += math.sin(time.time() * 3 + self.x) * 0.8 * time.dt
            
            # Pulsing glow effect
            pulse = math.sin(time.time() * 4) * 0.3 + 0.7
            glow_alpha = int(80 * pulse)
            self.glow.color = color.rgba(255, 255, 0, glow_alpha)
            
            # Beacon effect
            beacon_alpha = int(200 * pulse)
            self.beacon.color = color.rgba(255, 255, 255, beacon_alpha)
    
    def collect(self):
        """Collect this item"""
        if not self.collected:
            self.collected = True
            self.visible = False
            if self.beacon:
                self.beacon.visible = False
            return True
        return False

class GameManager:
    """Enhanced game manager with objectives suited for overhead view"""
    
    def __init__(self):
        self.score = 0
        self.collectibles_found = 0
        self.total_collectibles = 0
        self.flight_time = 0
        self.max_altitude = 0
        self.max_speed = 0
        self.distance_traveled = 0
        self.last_position = Vec3(0, 0, 0)
        
        # Game state
        self.game_started = False
        self.game_paused = False
        self.hud_visible = True
        
        # Enhanced objectives for overhead gameplay
        self.objectives = [
            "Collect 10 acorns scattered throughout the forest",
            "Reach an altitude of 60 meters",
            "Find and use thermal updrafts to soar",
            "Fly for 3 minutes continuously",
            "Visit all 4 corners of the map",
            "Achieve a top speed of 25 m/s"
        ]
        self.completed_objectives = []
        
        # Map exploration tracking
        self.visited_quadrants = set()
        self.quadrant_size = 75  # Size of each map quadrant
    
    def update(self, squirrel):
        """Update game state with enhanced tracking"""
        if not self.game_started or self.game_paused:
            return
        
        # Update flight time
        self.flight_time += time.dt
        
        # Update max altitude
        current_altitude = squirrel.position.y
        if current_altitude > self.max_altitude:
            self.max_altitude = current_altitude
        
        # Update max speed
        current_speed = distance(squirrel.physics.velocity, Vec3(0, 0, 0))
        if current_speed > self.max_speed:
            self.max_speed = current_speed
        
        # Update distance traveled
        distance_this_frame = distance(squirrel.position, self.last_position)
        self.distance_traveled += distance_this_frame
        self.last_position = squirrel.position
        
        # Track map exploration
        self.track_exploration(squirrel.position)
        
        # Check objectives
        self.check_objectives()
    
    def track_exploration(self, position):
        """Track which areas of the map have been visited"""
        quad_x = int(position.x // self.quadrant_size)
        quad_z = int(position.z // self.quadrant_size)
        quadrant = (quad_x, quad_z)
        self.visited_quadrants.add(quadrant)
    
    def check_objectives(self):
        """Check if objectives are completed"""
        # Altitude objective (increased for overhead view)
        if self.max_altitude >= 60 and "Reach an altitude of 60 meters" not in self.completed_objectives:
            self.completed_objectives.append("Reach an altitude of 60 meters")
            self.score += 800
        
        # Flight time objective (increased)
        if self.flight_time >= 180 and "Fly for 3 minutes continuously" not in self.completed_objectives:
            self.completed_objectives.append("Fly for 3 minutes continuously")
            self.score += 500
        
        # Speed objective
        if self.max_speed >= 25 and "Achieve a top speed of 25 m/s" not in self.completed_objectives:
            self.completed_objectives.append("Achieve a top speed of 25 m/s")
            self.score += 600
        
        # Collectible objective
        if self.collectibles_found >= 10 and "Collect 10 acorns scattered throughout the forest" not in self.completed_objectives:
            self.completed_objectives.append("Collect 10 acorns scattered throughout the forest")
            self.score += 1000
        
        # Map exploration objective
        corner_quadrants = {(-1, -1), (-1, 1), (1, -1), (1, 1)}
        if corner_quadrants.issubset(self.visited_quadrants) and "Visit all 4 corners of the map" not in self.completed_objectives:
            self.completed_objectives.append("Visit all 4 corners of the map")
            self.score += 1200
    
    def collect_item(self, item_type):
        """Handle item collection"""
        self.collectibles_found += 1
        
        if item_type == 'acorn':
            self.score += 75
        elif item_type == 'berry':
            self.score += 50
        elif item_type == 'nut':
            self.score += 60

class FlightSimulator:
    """Enhanced main game class with overhead camera system"""
    
    def __init__(self):
        self.setup_window()
        self.game_manager = GameManager()
        
        # Initialize all systems
        self.create_world()
        self.create_camera_system()
        self.create_ui()
        self.create_collectibles()
        
        # Game state
        self.show_menu = True
        self.camera_mode = 'overhead'  # 'overhead', 'cinematic', 'scenic'
        
        print("Flying Squirrel Flight Simulator - Enhanced with Overhead View")
        print("Controls: WASD = Pitch/Yaw, Space = Boost, Shift = Dive")
        print("Camera: Mouse Wheel = Zoom, Q/E = Zoom, R/F = Height, Right Click + Drag = Rotate")
        print("Find thermal updrafts to gain altitude!")
        print("Collect items and complete objectives for points!")
    
    def setup_window(self):
        """Configure game window"""
        window.title = 'Flying Squirrel Flight Simulator - Overhead View'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = config.DEBUG['show_fps']
        
        # Performance settings optimized for overhead view
        Entity.default_shader = basic_lighting_shader  # Simplified for better performance
    
    def create_world(self):
        """Create the enhanced sparse game world"""
        print("Generating enhanced sparse world...")
        
        # Enhanced terrain with better 3D depth
        self.terrain = EnhancedTerrain(
            size=config.WORLD_SIZE,
            resolution=50  # Good balance for overhead view
        )
        
        # Sparse forest with strategic placement
        self.forest = SparseForest(self.terrain, tree_count=100)  # Much more sparse
        
        # Environmental landmarks for navigation
        self.landmarks = EnvironmentalLandmarks(self.terrain)
        
        # Sky system optimized for overhead view
        self.sky_system = OverheadSkySystem()
        
        # Particle system
        self.particle_system = ParticleSystem()
        
        # Flying squirrel optimized for overhead view
        self.squirrel = FlyingSquirrel(config.SQUIRREL_PHYSICS)
        
        print(f"Enhanced world created:")
        print(f"  - {len(self.forest.trees)} trees in {len(self.forest.tree_groups)} clusters")
        print(f"  - {len(self.landmarks.landmarks)} environmental landmarks")
        print(f"  - Terrain size: {config.WORLD_SIZE}x{config.WORLD_SIZE}")
    
    def create_camera_system(self):
        """Create the overhead camera system"""
        # Main overhead camera
        camera_config = {
            'distance': 30,      # Farther back for better overview
            'height': 25,        # Higher up
            'angle': 45,         # Good viewing angle
            'smoothing': 0.08,   # Smooth following
            'rotation_speed': 2.0,
            'zoom_speed': 2.5,
            'min_distance': 18,
            'max_distance': 60,
            'min_height': 12,
            'max_height': 50
        }
        
        self.overhead_camera = OverheadCameraSystem(self.squirrel, camera_config)
        
        # Cinematic camera for special sequences
        self.cinematic_camera = CinematicCamera()
        
        # Environment showcase camera
        self.environment_camera = EnvironmentViewCamera(self.terrain)
        
        print("Overhead camera system initialized")
        print("Camera controls: Mouse Wheel/Q/E = Zoom, R/F = Height, Right Click + Drag = Rotate")
    
    def create_ui(self):
        """Create enhanced user interface for overhead view"""
        # Main menu
        self.main_menu = MainMenu()
        self.main_menu.start_button.on_click = self.start_game
        
        # HUD optimized for overhead view
        self.hud = FlightHUD(self.squirrel)
        self.hud.visible = False
        
        # Pause menu
        self.pause_menu = PauseMenu()
        
        # Enhanced score display
        self.score_text = Text(
            'Score: 0',
            parent=camera.ui,
            scale=2.2,
            color=color.white,
            position=(0.65, 0.45, 0),
            visible=False
        )
        
        # Map exploration indicator
        self.exploration_text = Text(
            'Map: 0% Explored',
            parent=camera.ui,
            scale=1.8,
            color=color.cyan,
            position=(0.65, 0.4, 0),
            visible=False
        )
        
        # Enhanced objectives display
        self.objectives_text = Text(
            'Objectives:\n- Explore the vast world\n- Collect items\n- Master the thermals',
            parent=camera.ui,
            scale=1.3,
            color=color.yellow,
            position=(-0.9, 0.35, 0),
            visible=False
        )
        
        # Camera mode indicator
        self.camera_mode_text = Text(
            'Camera: Overhead',
            parent=camera.ui,
            scale=1.5,
            color=color.light_gray,
            position=(-0.9, -0.4, 0),
            visible=False
        )
    
    def create_collectibles(self):
        """Spawn collectibles strategically across the enhanced world"""
        self.collectibles = []
        
        # Acorns placed strategically for overhead gameplay
        for _ in range(15):  # Reduced count but better placement
            x = random.uniform(-config.WORLD_SIZE//2 + 30, config.WORLD_SIZE//2 - 30)
            z = random.uniform(-config.WORLD_SIZE//2 + 30, config.WORLD_SIZE//2 - 30)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(3, 12)
            
            acorn = Collectible(Vec3(x, y, z), 'acorn')
            self.collectibles.append(acorn)
        
        # Berries at higher altitudes
        for _ in range(10):
            x = random.uniform(-config.WORLD_SIZE//3, config.WORLD_SIZE//3)
            z = random.uniform(-config.WORLD_SIZE//3, config.WORLD_SIZE//3)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(8, 20)
            
            berry = Collectible(Vec3(x, y, z), 'berry')
            self.collectibles.append(berry)
        
        self.game_manager.total_collectibles = len(self.collectibles)
        print(f"Spawned {len(self.collectibles)} collectibles strategically across the world")
    
    def start_game(self):
        """Start the actual gameplay"""
        self.show_menu = False
        self.main_menu.visible = False
        self.main_menu.enabled = False
        
        self.hud.visible = True
        self.score_text.visible = True
        self.exploration_text.visible = True
        self.objectives_text.visible = True
        self.camera_mode_text.visible = True
        
        self.game_manager.game_started = True
        
        # Start with a cinematic intro
        self.start_intro_cinematic()
        
        print("Game started with overhead view! Enjoy the enhanced perspective!")
    
    def start_intro_cinematic(self):
        """Start an intro cinematic showing the world"""
        intro_pos = Vec3(0, 80, -100)  # High overview position
        intro_rot = Vec3(30, 0, 0)     # Looking down at the world
        
        self.cinematic_camera.start_cinematic(
            intro_pos, intro_rot, duration=4.0,
            callback=self.end_intro_cinematic
        )
        self.camera_mode = 'cinematic'
    
    def end_intro_cinematic(self):
        """End intro and switch to overhead camera"""
        self.camera_mode = 'overhead'
        self.overhead_camera.setup_camera()
    
    def toggle_pause(self):
        """Toggle game pause"""
        if not self.game_manager.game_started:
            return
            
        self.game_manager.game_paused = not self.game_manager.game_paused
        
        if self.game_manager.game_paused:
            self.pause_menu.show()
        else:
            self.pause_menu.hide()
    
    def toggle_hud(self):
        """Toggle HUD visibility"""
        if self.game_manager.game_started:
            self.game_manager.hud_visible = not self.game_manager.hud_visible
            self.hud.visible = self.game_manager.hud_visible
            self.score_text.visible = self.game_manager.hud_visible
            self.exploration_text.visible = self.game_manager.hud_visible
            self.objectives_text.visible = self.game_manager.hud_visible
            self.camera_mode_text.visible = self.game_manager.hud_visible
    
    def cycle_camera_mode(self):
        """Cycle through different camera modes"""
        if self.camera_mode == 'overhead':
            self.camera_mode = 'scenic'
            self.environment_camera.activate_scenic_view()
            self.camera_mode_text.text = 'Camera: Scenic View'
        elif self.camera_mode == 'scenic':
            self.camera_mode = 'overhead'
            self.overhead_camera.setup_camera()
            self.camera_mode_text.text = 'Camera: Overhead'
    
    def check_collectibles(self):
        """Check for collectible collection with larger radius for overhead play"""
        squirrel_pos = self.squirrel.position
        
        for collectible in self.collectibles:
            if not collectible.collected:
                distance_to_collectible = distance(squirrel_pos, collectible.position)
                
                if distance_to_collectible < 3:  # Larger collection radius
                    if collectible.collect():
                        self.game_manager.collect_item(collectible.collectible_type)
                        print(f"Collected {collectible.collectible_type}! Score: {self.game_manager.score}")
    
    def update(self):
        """Main game update loop with camera system"""
        if self.show_menu:
            return
        
        if not self.game_manager.game_paused:
            # Update camera system
            if self.camera_mode == 'overhead':
                self.overhead_camera.update()
            elif self.camera_mode == 'cinematic':
                if self.cinematic_camera.update():  # Returns True when complete
                    self.camera_mode = 'overhead'
                    self.overhead_camera.setup_camera()
            elif self.camera_mode == 'scenic':
                pass  # Static scenic view
            
            # Update particle system
            self.particle_system.update()
            
            # Update game manager
            self.game_manager.update(self.squirrel)
            
            # Check collectibles
            self.check_collectibles()
            
            # Create wind particles occasionally
            if random.random() < 0.05:  # Reduced frequency for overhead view
                self.particle_system.create_wind_particles(
                    self.squirrel.position + Vec3(random.uniform(-15, 15), 0, random.uniform(-15, 15))
                )
        
        # Update UI
        if self.game_manager.game_started:
            self.score_text.text = f'Score: {self.game_manager.score}'
            
            # Calculate map exploration percentage
            exploration_percent = min(100, len(self.game_manager.visited_quadrants) * 10)
            self.exploration_text.text = f'Map: {exploration_percent}% Explored'
            
            # Update objectives display
            completed_text = "Completed:\n"
            for obj in self.game_manager.completed_objectives:
                completed_text += f"✓ {obj}\n"
            
            remaining_text = "\nRemaining:\n"
            for obj in self.game_manager.objectives:
                if obj not in self.game_manager.completed_objectives:
                    remaining_text += f"• {obj}\n"
            
            self.objectives_text.text = completed_text + remaining_text

# Create global game instance
game = FlightSimulator()

def input(key):
    """Handle input events with camera controls"""
    if key == 'escape':
        if game.show_menu:
            quit()
        else:
            game.toggle_pause()
    
    elif key == 'f1':
        game.toggle_hud()
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen
    
    elif key == 'c':
        game.cycle_camera_mode()
    
    elif key == 'v':
        if game.camera_mode == 'scenic':
            game.environment_camera.next_viewpoint()

def update():
    """Main update function called by Ursina"""
    game.update()

# Main execution
if __name__ == '__main__':
    # Start the game loop
    app.run() 