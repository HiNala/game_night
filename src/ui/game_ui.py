"""
Enhanced Game UI System
Professional flight simulator interface with instruments and HUD.
"""

from ursina import *
import math

class FlightHUD(Entity):
    """Head-Up Display with flight instruments"""
    
    def __init__(self, squirrel):
        super().__init__(parent=camera.ui)
        self.squirrel = squirrel
        
        # HUD Elements
        self.create_speed_indicator()
        self.create_altitude_indicator()
        self.create_attitude_indicator()
        self.create_compass()
        self.create_g_force_meter()
        self.create_thermal_indicator()
        self.create_crosshair()
        self.create_controls_help()
    
    def create_speed_indicator(self):
        """Airspeed indicator"""
        self.speed_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.25, 0.4, 1),
            position=(-0.75, 0.25, 0)
        )
        
        self.speed_text = Text(
            'SPEED\n0 m/s',
            parent=self.speed_bg,
            scale=1.5,
            color=color.white,
            position=(0, 0, -0.1),
            origin=(0, 0)
        )
        
        # Speed tape
        self.speed_tape = Entity(parent=self.speed_bg)
        for i in range(0, 51, 5):
            mark = Entity(
                parent=self.speed_tape,
                model='cube',
                color=color.white,
                scale=(0.8, 0.05, 1),
                position=(0, (i-25) * 0.01, -0.05)
            )
            
            if i % 10 == 0:
                mark.scale_x = 1.0
                speed_label = Text(
                    str(i),
                    parent=mark,
                    scale=0.8,
                    color=color.white,
                    position=(0.6, 0, 0)
                )
    
    def create_altitude_indicator(self):
        """Altitude indicator"""
        self.alt_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.25, 0.4, 1),
            position=(0.75, 0.25, 0)
        )
        
        self.alt_text = Text(
            'ALT\n0 m',
            parent=self.alt_bg,
            scale=1.5,
            color=color.white,
            position=(0, 0, -0.1),
            origin=(0, 0)
        )
    
    def create_attitude_indicator(self):
        """Artificial horizon"""
        self.attitude_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 200),
            scale=(0.3, 0.3, 1),
            position=(0, 0.25, 0)
        )
        
        # Horizon line
        self.horizon = Entity(
            parent=self.attitude_bg,
            model='cube',
            color=color.white,
            scale=(1, 0.02, 1),
            position=(0, 0, -0.05)
        )
        
        # Sky and ground
        self.sky_part = Entity(
            parent=self.attitude_bg,
            model='cube',
            color=color.rgb(0.3, 0.6, 1.0),
            scale=(1, 0.5, 1),
            position=(0, 0.25, -0.1)
        )
        
        self.ground_part = Entity(
            parent=self.attitude_bg,
            model='cube',
            color=color.rgb(0.4, 0.2, 0.1),
            scale=(1, 0.5, 1),
            position=(0, -0.25, -0.1)
        )
        
        # Aircraft symbol
        self.aircraft_symbol = Entity(
            parent=self.attitude_bg,
            model='cube',
            color=color.yellow,
            scale=(0.1, 0.02, 1),
            position=(0, 0, -0.02)
        )
    
    def create_compass(self):
        """Heading compass"""
        self.compass_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.4, 0.1, 1),
            position=(0, -0.35, 0)
        )
        
        self.compass_text = Text(
            'HDG: 000°',
            parent=self.compass_bg,
            scale=1.5,
            color=color.white,
            position=(0, 0, -0.1),
            origin=(0, 0)
        )
    
    def create_g_force_meter(self):
        """G-force indicator"""
        self.g_force_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.2, 0.3, 1),
            position=(-0.4, -0.15, 0)
        )
        
        self.g_force_text = Text(
            'G\n1.0',
            parent=self.g_force_bg,
            scale=1.2,
            color=color.white,
            position=(0, 0, -0.1),
            origin=(0, 0)
        )
    
    def create_thermal_indicator(self):
        """Thermal activity indicator"""
        self.thermal_bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.2, 0.3, 1),
            position=(0.4, -0.15, 0)
        )
        
        self.thermal_text = Text(
            'LIFT\n0.0',
            parent=self.thermal_bg,
            scale=1.2,
            color=color.white,
            position=(0, 0, -0.1),
            origin=(0, 0)
        )
    
    def create_crosshair(self):
        """Center crosshair"""
        self.crosshair_h = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 255, 255, 200),
            scale=(0.1, 0.005, 1),
            position=(0, 0, 0)
        )
        
        self.crosshair_v = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 255, 255, 200),
            scale=(0.005, 0.1, 1),
            position=(0, 0, 0)
        )
    
    def create_controls_help(self):
        """Control instructions"""
        self.controls_text = Text(
            'WASD: Pitch/Yaw | Space: Boost | Shift: Dive | ESC: Exit | F1: Hide HUD',
            parent=self,
            scale=1.2,
            color=color.rgba(255, 255, 255, 180),
            position=(-0.9, -0.47, 0)
        )
        
        self.objective_text = Text(
            'Find thermals (rising air) to gain altitude - Look for the LIFT indicator!',
            parent=self,
            scale=1.3,
            color=color.rgba(100, 255, 100, 200),
            position=(-0.9, 0.45, 0)
        )
    
    def update(self):
        """Update HUD elements"""
        if not self.squirrel:
            return
            
        flight_data = self.squirrel.get_flight_data()
        
        # Update speed
        speed = flight_data['speed']
        self.speed_text.text = f'SPEED\n{speed:.1f} m/s'
        
        # Color code speed (green = good, red = slow/fast)
        if 8 <= speed <= 20:
            self.speed_text.color = color.green
        elif speed < 5:
            self.speed_text.color = color.red
        else:
            self.speed_text.color = color.white
        
        # Update altitude
        altitude = flight_data['altitude']
        self.alt_text.text = f'ALT\n{altitude:.1f} m'
        
        # Color code altitude
        if altitude < 5:
            self.alt_text.color = color.red
        elif altitude < 10:
            self.alt_text.color = color.yellow
        else:
            self.alt_text.color = color.white
        
        # Update attitude indicator
        pitch = flight_data['pitch']
        roll = flight_data['roll']
        
        self.horizon.rotation_z = roll
        self.horizon.position = (0, -pitch * 0.01, -0.05)
        self.sky_part.rotation_z = roll
        self.ground_part.rotation_z = roll
        
        # Update compass
        heading = flight_data['heading'] % 360
        self.compass_text.text = f'HDG: {heading:03.0f}°'
        
        # Update G-force
        g_force = flight_data.get('g_force', 1.0)
        self.g_force_text.text = f'G\n{g_force:.1f}'
        
        # Color code G-force
        if g_force > 3.0:
            self.g_force_text.color = color.red
        elif g_force > 2.0:
            self.g_force_text.color = color.yellow
        else:
            self.g_force_text.color = color.white
        
        # Update thermal indicator
        thermal_strength = getattr(self.squirrel.physics, 'thermal_strength', 0)
        self.thermal_text.text = f'LIFT\n{thermal_strength:.1f}'
        
        # Color code thermal activity
        if thermal_strength > 2:
            self.thermal_text.color = color.green
        elif thermal_strength > 0.5:
            self.thermal_text.color = color.yellow
        else:
            self.thermal_text.color = color.white

class MainMenu(Entity):
    """Main menu system"""
    
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.visible = True
        
        # Background
        self.bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 2, 1),
            position=(0, 0, 0.1)
        )
        
        # Title
        self.title = Text(
            'FLYING SQUIRREL\nFLIGHT SIMULATOR',
            parent=self,
            scale=3,
            color=color.white,
            position=(0, 0.3, 0),
            origin=(0, 0)
        )
        
        # Start button
        self.start_button = Button(
            text='START FLIGHT',
            parent=self,
            scale=(0.3, 0.1),
            position=(0, 0, 0),
            color=color.green
        )
        self.start_button.on_click = self.start_game
        
        # Instructions
        self.instructions = Text(
            'Welcome to the Flying Squirrel Flight Simulator!\n\n'
            'Use WASD to control pitch and yaw\n'
            'Find thermal updrafts to gain altitude\n'
            'Explore the beautiful 3D environment\n\n'
            'Click START FLIGHT to begin!',
            parent=self,
            scale=1.5,
            color=color.light_gray,
            position=(0, -0.25, 0),
            origin=(0, 0)
        )
    
    def start_game(self):
        """Start the game"""
        self.visible = False
        self.enabled = False

class PauseMenu(Entity):
    """Pause menu overlay"""
    
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.visible = False
        self.enabled = False
        
        # Background
        self.bg = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(2, 2, 1),
            position=(0, 0, 0.1)
        )
        
        # Pause text
        self.pause_text = Text(
            'PAUSED',
            parent=self,
            scale=4,
            color=color.white,
            position=(0, 0.2, 0),
            origin=(0, 0)
        )
        
        # Resume button
        self.resume_button = Button(
            text='RESUME',
            parent=self,
            scale=(0.2, 0.08),
            position=(0, 0, 0),
            color=color.green
        )
        self.resume_button.on_click = self.resume_game
        
        # Instructions
        self.instructions = Text(
            'Press ESC to resume\nPress F1 to toggle HUD',
            parent=self,
            scale=1.5,
            color=color.light_gray,
            position=(0, -0.15, 0),
            origin=(0, 0)
        )
    
    def show(self):
        """Show pause menu"""
        self.visible = True
        self.enabled = True
    
    def hide(self):
        """Hide pause menu"""
        self.visible = False
        self.enabled = False
    
    def resume_game(self):
        """Resume the game"""
        self.hide() 