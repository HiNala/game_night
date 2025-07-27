#!/usr/bin/env python3
"""
🦕 PREHISTORIC SAN FRANCISCO FLIGHT SIMULATOR 🌉
EPIC pterodactyl ecosystem flying through San Francisco with Golden Gate Bridge!

DESIGNED BY SENIOR DEVELOPERS
3D/4D DESIGN EXCELLENCE  
WE ARE LEGION - MAXIMUM EPIC FACTOR ACHIEVED
"""

from ursina import *
import sys
import os
import math
import random

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from entities.prehistoric_player import PrehistoricPlayer
from entities.pterodactyl_ecosystem import PterodactylEcosystem
from graphics.san_francisco_world import (
    SanFranciscoTerrain, 
    GoldenGateBridge, 
    SanFranciscoLandmarks,
    SanFranciscoAtmosphere,
    SanFranciscoWaterSystem
)
from graphics.camera_system import OverheadCameraSystem, CinematicCamera, EnvironmentViewCamera
from ui.game_ui import FlightHUD, MainMenu, PauseMenu
import game_config as config

app = Ursina()

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
            parent=self,
            model='sphere',
            color=color.rgba(255, 215, 0, 120),  # Golden glow
            scale=3.5
        )
        
        # Prehistoric energy beacon
        self.energy_beam = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 255, 100, 180),
            scale=(0.2, 8, 0.2),
            position=(0, 4, 0)
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
                model='sphere',
                color=color.rgba(255, 255, 0, 200),
                scale=1,
                position=self.position,
                parent=scene
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
        
        # EPIC OBJECTIVES for prehistoric SF
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
        
        current_speed = distance(player.physics.velocity, Vec3(0, 0, 0))
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
            
            if distance_to_ptero < 20:  # Close encounter
                if hasattr(pterodactyl, 'species_type'):
                    self.species_encountered.add(pterodactyl.species_type)
                    
                if distance_to_ptero < 8:  # Very close encounter
                    self.pterodactyl_encounters += 1
    
    def check_bridge_flythrough(self, player):
        """Check if player flew through Golden Gate Bridge"""
        bridge_x, bridge_z = self.bridge_zone
        
        # Check if near bridge
        if (abs(player.x - bridge_x) < 60 and 
            abs(player.z - bridge_z) < 15 and
            10 < player.y < 60):  # At bridge height
            
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
        
        # Prehistoric atmosphere
        self.atmosphere = SanFranciscoAtmosphere()
        print("   ✓ Prehistoric atmosphere and lighting created")
        
        # Water systems
        self.water_system = SanFranciscoWaterSystem(self.terrain)
        print("   ✓ San Francisco Bay and Pacific Ocean created")
        
        # PTERODACTYL ECOSYSTEM!
        self.pterodactyl_ecosystem = PterodactylEcosystem()
        print("   ✓ 🦕 PTERODACTYL ECOSYSTEM activated!")
        
        # Player creature
        self.player = PrehistoricPlayer('archaeopteryx')  # Can be changed to 'dragon' or 'pterodactyl'
        print("   ✓ Player creature ready for epic flight!")
        
        print("🌍 EPIC WORLD CREATION COMPLETE!")
        print(f"   🦕 {len(self.pterodactyl_ecosystem.get_all_pterodactyls())} pterodactyls roaming SF")
        print(f"   🌉 Golden Gate Bridge ready for epic flythroughs")
        print(f"   🏔️ Twin Peaks at {max([hill['height'] for hill in self.terrain.sf_features.values()])}m")
    
    def create_camera_system(self):
        """Epic camera system for prehistoric SF"""
        
        # Enhanced camera config for epic SF viewing
        camera_config = {
            'distance': 35,      # Farther for epic vistas
            'height': 30,        # Higher for SF overview
            'angle': 50,         # Perfect for Golden Gate views
            'smoothing': 0.06,   # Smooth epic following
            'rotation_speed': 1.8,
            'zoom_speed': 3.0,
            'min_distance': 20,
            'max_distance': 80,  # Zoom out for epic scale
            'min_height': 15,
            'max_height': 60,
        }
        
        self.overhead_camera = OverheadCameraSystem(self.player, camera_config)
        self.cinematic_camera = CinematicCamera()
        self.environment_camera = EnvironmentViewCamera(self.terrain)
        
        print("🎥 Epic camera system initialized for SF flyovers")
    
    def create_ui_system(self):
        """Epic UI for prehistoric San Francisco"""
        
        # Main menu
        self.main_menu = MainMenu()
        self.main_menu.start_button.on_click = self.start_epic_game
        
        # Enhanced HUD
        self.hud = FlightHUD(self.player)
        self.hud.visible = False
        
        # Pause menu
        self.pause_menu = PauseMenu()
        
        # Epic score display
        self.score_text = Text(
            'Score: 0',
            parent=camera.ui,
            scale=2.5,
            color=color.gold,
            position=(0.6, 0.45, 0),
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
            position=(-0.9, 0.4, 0),
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
        self.main_menu.visible = False
        self.main_menu.enabled = False
        
        # Show all epic UI elements
        self.hud.visible = True
        self.score_text.visible = True
        self.reputation_text.visible = True
        self.objectives_text.visible = True
        self.bridge_text.visible = True
        self.species_text.visible = True
        
        self.game_manager.game_started = True
        
        # Epic cinematic intro over Golden Gate Bridge
        self.start_golden_gate_cinematic()
        
        print("🦕🌉 EPIC PREHISTORIC SAN FRANCISCO ADVENTURE BEGINS! 🌉🦕")
        print("Soar with pterodactyls over the Golden Gate Bridge!")
    
    def start_golden_gate_cinematic(self):
        """Epic cinematic intro showcasing Golden Gate Bridge"""
        # Start high above Golden Gate Bridge
        intro_pos = Vec3(-80, 150, 80)  # High above the bridge
        intro_rot = Vec3(45, 180, 0)    # Looking down at bridge
        
        self.cinematic_camera.start_cinematic(
            intro_pos, intro_rot, duration=5.0,
            callback=self.end_cinematic_intro
        )
        self.camera_mode = 'cinematic'
    
    def end_cinematic_intro(self):
        """End cinematic and begin epic gameplay"""
        self.camera_mode = 'overhead'
        self.overhead_camera.setup_camera()
    
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
            # Update camera system
            if self.camera_mode == 'overhead':
                self.overhead_camera.update()
            elif self.camera_mode == 'cinematic':
                if self.cinematic_camera.update():
                    self.camera_mode = 'overhead'
                    self.overhead_camera.setup_camera()
            
            # Update prehistoric atmosphere
            self.atmosphere.update()
            
            # Update water system
            self.water_system.update()
            
            # Update pterodactyl ecosystem
            all_pterodactyls = self.pterodactyl_ecosystem.get_all_pterodactyls()
            self.pterodactyl_ecosystem.update(self.player.position)
            
            # Update player with pterodactyl interactions
            nearby_pterodactyls = [p for p in all_pterodactyls 
                                 if distance(self.player.position, p.position) < 50]
            self.player.update(nearby_pterodactyls)
            
            # Update game manager
            self.game_manager.update(self.player, all_pterodactyls)
            
            # Check collectibles
            self.check_prehistoric_collectibles()
        
        # Update epic UI
        self.update_epic_ui()
    
    def update_epic_ui(self):
        """Update all epic UI elements"""
        if not self.game_manager.game_started:
            return
        
        # Score
        self.score_text.text = f'Score: {self.game_manager.score:,}'
        
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
        
        if self.game_manager.game_paused:
            self.pause_menu.show()
        else:
            self.pause_menu.hide()
    
    def cycle_camera_mode(self):
        """Cycle through epic camera modes"""
        if self.camera_mode == 'overhead':
            self.camera_mode = 'scenic'
            self.environment_camera.activate_scenic_view()
        elif self.camera_mode == 'scenic':
            self.camera_mode = 'overhead'
            self.overhead_camera.setup_camera()

# 🦕 CREATE THE EPIC GAME INSTANCE 🦕
prehistoric_sf_game = PrehistoricSanFranciscoSimulator()

def input(key):
    """🎮 EPIC INPUT HANDLING 🎮"""
    if key == 'escape':
        if prehistoric_sf_game.show_menu:
            quit()
        else:
            prehistoric_sf_game.toggle_pause()
    
    elif key == 'f1':
        # Toggle HUD
        prehistoric_sf_game.hud.visible = not prehistoric_sf_game.hud.visible
    
    elif key == 'f11':
        window.fullscreen = not window.fullscreen
    
    elif key == 'c':
        prehistoric_sf_game.cycle_camera_mode()
    
    elif key == 'v':
        if prehistoric_sf_game.camera_mode == 'scenic':
            prehistoric_sf_game.environment_camera.next_viewpoint()

def update():
    """🔄 MAIN EPIC UPDATE FUNCTION 🔄"""
    prehistoric_sf_game.update()

# 🚀 EPIC EXECUTION - LAUNCH THE PREHISTORIC ADVENTURE! 🚀
if __name__ == '__main__':
    print("🦕🌉 LAUNCHING PREHISTORIC SAN FRANCISCO! 🌉🦕")
    app.run() 