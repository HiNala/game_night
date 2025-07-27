#!/usr/bin/env python3
"""
Flying Squirrel Flight Simulator - Enhanced Version
Professional 3D flight simulator with realistic physics and engaging gameplay.
"""

from ursina import *
import sys
import os
import math
import random

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.flying_squirrel import FlyingSquirrel
from graphics.environment import EnhancedTerrain, Forest, SkySystem, ParticleSystem
from ui.game_ui import FlightHUD, MainMenu, PauseMenu
import game_config as config

app = Ursina()

class Collectible(Entity):
    """Collectible items scattered throughout the world"""
    
    def __init__(self, position, collectible_type='acorn'):
        super().__init__()
        self.position = position
        self.collectible_type = collectible_type
        self.collected = False
        self.rotation_speed = 50
        
        # Create collectible model
        if collectible_type == 'acorn':
            self.model = 'cube'
            self.color = color.brown
            self.scale = 0.3
        elif collectible_type == 'berry':
            self.model = 'sphere'
            self.color = color.red
            self.scale = 0.2
        elif collectible_type == 'nut':
            self.model = 'cube'
            self.color = color.orange
            self.scale = 0.25
        
        # Add glow effect
        self.glow = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(255, 255, 0, 50),
            scale=1.5
        )
    
    def update(self):
        """Animate collectible"""
        if not self.collected:
            self.rotation_y += self.rotation_speed * time.dt
            
            # Bob up and down
            self.y += math.sin(time.time() * 3 + self.x) * 0.5 * time.dt
    
    def collect(self):
        """Collect this item"""
        if not self.collected:
            self.collected = True
            self.visible = False
            return True
        return False

class GameManager:
    """Manages game state, objectives, and progression"""
    
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
        
        # Objectives
        self.objectives = [
            "Collect 10 acorns scattered throughout the forest",
            "Reach an altitude of 50 meters",
            "Find and use thermal updrafts to soar",
            "Fly for 2 minutes continuously",
            "Explore the entire map area"
        ]
        self.completed_objectives = []
    
    def update(self, squirrel):
        """Update game state"""
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
        
        # Check objectives
        self.check_objectives()
    
    def check_objectives(self):
        """Check if objectives are completed"""
        # Altitude objective
        if self.max_altitude >= 50 and "Reach an altitude of 50 meters" not in self.completed_objectives:
            self.completed_objectives.append("Reach an altitude of 50 meters")
            self.score += 500
        
        # Flight time objective
        if self.flight_time >= 120 and "Fly for 2 minutes continuously" not in self.completed_objectives:
            self.completed_objectives.append("Fly for 2 minutes continuously")
            self.score += 300
        
        # Collectible objective
        if self.collectibles_found >= 10 and "Collect 10 acorns scattered throughout the forest" not in self.completed_objectives:
            self.completed_objectives.append("Collect 10 acorns scattered throughout the forest")
            self.score += 1000
    
    def collect_item(self, item_type):
        """Handle item collection"""
        self.collectibles_found += 1
        
        if item_type == 'acorn':
            self.score += 50
        elif item_type == 'berry':
            self.score += 30
        elif item_type == 'nut':
            self.score += 40

class FlightSimulator:
    """Main game class that orchestrates all systems"""
    
    def __init__(self):
        self.setup_window()
        self.game_manager = GameManager()
        
        # Initialize all systems
        self.create_world()
        self.create_ui()
        self.create_collectibles()
        
        # Game state
        self.show_menu = True
        
        print("Flying Squirrel Flight Simulator - Enhanced Version")
        print("Controls: WASD = Pitch/Yaw, Space = Boost, Shift = Dive")
        print("Find thermal updrafts to gain altitude!")
        print("Collect items and complete objectives for points!")
    
    def setup_window(self):
        """Configure game window"""
        window.title = 'Flying Squirrel Flight Simulator - Enhanced'
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        window.fps_counter.enabled = config.DEBUG['show_fps']
        
        # Performance settings
        Entity.default_shader = lit_with_shadows_shader if config.GRAPHICS['enable_shadows'] else basic_lighting_shader
    
    def create_world(self):
        """Create the game world"""
        print("Generating world...")
        
        # Terrain
        self.terrain = EnhancedTerrain(
            size=config.WORLD_SIZE,
            resolution=60  # Good balance of detail and performance
        )
        
        # Forest
        self.forest = Forest(self.terrain, config.TREE_COUNT)
        
        # Sky system
        self.sky_system = SkySystem()
        
        # Particle system
        self.particle_system = ParticleSystem()
        
        # Flying squirrel
        self.squirrel = FlyingSquirrel(config.SQUIRREL_PHYSICS)
        
        # Camera setup
        self.setup_camera()
        
        print(f"World created with {len(self.forest.trees)} trees")
    
    def create_ui(self):
        """Create user interface"""
        # Main menu
        self.main_menu = MainMenu()
        self.main_menu.start_button.on_click = self.start_game
        
        # HUD
        self.hud = FlightHUD(self.squirrel)
        self.hud.visible = False
        
        # Pause menu
        self.pause_menu = PauseMenu()
        
        # Score display
        self.score_text = Text(
            'Score: 0',
            parent=camera.ui,
            scale=2,
            color=color.white,
            position=(0.7, 0.45, 0),
            visible=False
        )
        
        # Objectives display
        self.objectives_text = Text(
            'Objectives:\n- Find thermal updrafts\n- Collect items\n- Explore the world',
            parent=camera.ui,
            scale=1.2,
            color=color.yellow,
            position=(-0.9, 0.3, 0),
            visible=False
        )
    
    def create_collectibles(self):
        """Spawn collectibles throughout the world"""
        self.collectibles = []
        
        # Acorns (main collectible)
        for _ in range(20):
            x = random.uniform(-config.WORLD_SIZE//2 + 20, config.WORLD_SIZE//2 - 20)
            z = random.uniform(-config.WORLD_SIZE//2 + 20, config.WORLD_SIZE//2 - 20)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(2, 8)
            
            acorn = Collectible(Vec3(x, y, z), 'acorn')
            self.collectibles.append(acorn)
        
        # Berries (bonus items)
        for _ in range(15):
            x = random.uniform(-config.WORLD_SIZE//2 + 20, config.WORLD_SIZE//2 - 20)
            z = random.uniform(-config.WORLD_SIZE//2 + 20, config.WORLD_SIZE//2 - 20)
            y = self.terrain.get_height_at_position(x, z) + random.uniform(5, 15)
            
            berry = Collectible(Vec3(x, y, z), 'berry')
            self.collectibles.append(berry)
        
        self.game_manager.total_collectibles = len(self.collectibles)
        print(f"Spawned {len(self.collectibles)} collectibles")
    
    def setup_camera(self):
        """Setup camera to follow squirrel"""
        camera.parent = self.squirrel
        camera.position = (0, 3, -8)
        camera.rotation_x = 10
    
    def start_game(self):
        """Start the actual gameplay"""
        self.show_menu = False
        self.main_menu.visible = False
        self.main_menu.enabled = False
        
        self.hud.visible = True
        self.score_text.visible = True
        self.objectives_text.visible = True
        
        self.game_manager.game_started = True
        
        print("Game started! Good luck flying!")
    
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
            self.objectives_text.visible = self.game_manager.hud_visible
    
    def check_collectibles(self):
        """Check for collectible collection"""
        squirrel_pos = self.squirrel.position
        
        for collectible in self.collectibles:
            if not collectible.collected:
                distance_to_collectible = distance(squirrel_pos, collectible.position)
                
                if distance_to_collectible < 2:  # Collection radius
                    if collectible.collect():
                        self.game_manager.collect_item(collectible.collectible_type)
                        print(f"Collected {collectible.collectible_type}! Score: {self.game_manager.score}")
    
    def update(self):
        """Main game update loop"""
        if self.show_menu:
            return
        
        if not self.game_manager.game_paused:
            # Update sky system
            self.sky_system.update()
            
            # Update particle system
            self.particle_system.update()
            
            # Update game manager
            self.game_manager.update(self.squirrel)
            
            # Check collectibles
            self.check_collectibles()
            
            # Create wind particles occasionally
            if random.random() < 0.1:  # 10% chance each frame
                self.particle_system.create_wind_particles(
                    self.squirrel.position + Vec3(random.uniform(-10, 10), 0, random.uniform(-10, 10))
                )
        
        # Update UI
        if self.game_manager.game_started:
            self.score_text.text = f'Score: {self.game_manager.score}'
            
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
    """Handle input events"""
    if key == 'escape':
        if game.show_menu:
            quit()
        else:
            game.toggle_pause()
    
    elif key == 'f1':
        game.toggle_hud()
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen

def update():
    """Main update function called by Ursina"""
    game.update()

# Main execution
if __name__ == '__main__':
    # Start the game loop
    app.run() 