"""
Enhanced Flying Squirrel Entity
Advanced 3D model with realistic flight behavior and animations.
"""

from ursina import *
import math
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from physics.flight_physics import FlightPhysics

class FlyingSquirrel(Entity):
    """Enhanced flying squirrel with advanced physics and animations"""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        
        # Create detailed squirrel model
        self.create_model()
        
        # Initialize physics engine
        self.physics = FlightPhysics(self, config)
        
        # Flight state
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        # Animation state
        self.wing_beat_time = 0
        self.glide_factor = 0
        
        # Sound effects (placeholder)
        self.wind_sound_playing = False
        
        # Start position
        self.position = Vec3(0, config.get('start_altitude', 20), 0)
        
        # Visual effects
        self.create_particle_trail()
    
    def create_model(self):
        """Create detailed 3D model of flying squirrel"""
        
        # Main body
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(139, 69, 19),  # Saddle brown
            scale=(1.5, 0.6, 0.8),
            position=(0, 0, 0)
        )
        
        # Head
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(160, 82, 45),  # Lighter brown
            scale=(0.8, 0.6, 0.6),
            position=(0, 0, 0.6)
        )
        
        # Eyes
        self.left_eye = Entity(
            parent=self.head,
            model='sphere',
            color=color.black,
            scale=(0.15, 0.15, 0.15),
            position=(-0.2, 0.15, 0.2)
        )
        
        self.right_eye = Entity(
            parent=self.head,
            model='sphere',
            color=color.black,
            scale=(0.15, 0.15, 0.15),
            position=(0.2, 0.15, 0.2)
        )
        
        # Nose
        self.nose = Entity(
            parent=self.head,
            model='cube',
            color=color.dark_gray,
            scale=(0.1, 0.1, 0.1),
            position=(0, 0, 0.35)
        )
        
        # Gliding membrane (patagium)
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 200),  # Semi-transparent
            scale=(2.5, 0.05, 1.2),
            position=(-1.5, 0, 0),
            rotation=(0, 0, 15)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 200),
            scale=(2.5, 0.05, 1.2),
            position=(1.5, 0, 0),
            rotation=(0, 0, -15)
        )
        
        # Tail membrane
        self.tail_membrane = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 180),
            scale=(1.0, 0.05, 0.8),
            position=(0, 0, -1.2),
            rotation=(10, 0, 0)
        )
        
        # Tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(139, 69, 19),
            scale=(0.3, 0.3, 1.5),
            position=(0, 0, -1.5)
        )
        
        # Legs
        for i, (x, z) in enumerate([(-0.4, 0.2), (0.4, 0.2), (-0.4, -0.2), (0.4, -0.2)]):
            leg = Entity(
                parent=self,
                model='cube',
                color=color.rgb(101, 67, 33),
                scale=(0.2, 0.8, 0.2),
                position=(x, -0.5, z)
            )
    
    def create_particle_trail(self):
        """Create particle effects for enhanced visuals"""
        # This would be enhanced with actual particle systems
        self.trail_entities = []
        
        for i in range(5):
            trail_particle = Entity(
                parent=scene,
                model='cube',
                color=color.rgba(255, 255, 255, 100 - i*20),
                scale=0.1 - i*0.01,
                visible=False
            )
            self.trail_entities.append(trail_particle)
    
    def update(self):
        """Update squirrel physics and animations"""
        dt = time.dt
        
        # Handle input
        self.handle_input()
        
        # Update physics
        physics_data = self.physics.update(dt)
        
        # Update animations
        self.update_animations(physics_data)
        
        # Update visual effects
        self.update_effects(physics_data)
        
        # Keep above ground
        if self.y < 1:
            self.y = 1
            self.physics.velocity.y = max(0, self.physics.velocity.y)
        
        return physics_data
    
    def handle_input(self):
        """Process player input for flight control"""
        # Reset inputs
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        # Pitch control (elevator)
        if held_keys['w']:
            self.pitch_input = 1
        elif held_keys['s']:
            self.pitch_input = -1
        
        # Yaw control (rudder)
        if held_keys['a']:
            self.yaw_input = 1
            self.roll_input = 1  # Coordinated turn
        elif held_keys['d']:
            self.yaw_input = -1
            self.roll_input = -1
        
        # Additional controls
        if held_keys['space']:
            # Flare maneuver (increase lift temporarily)
            self.pitch_input += 0.5
        
        if held_keys['shift']:
            # Dive for speed
            self.pitch_input -= 0.8
        
        # Apply control inputs to physics
        self.physics.apply_control_input(
            self.pitch_input, 
            self.yaw_input, 
            self.roll_input
        )
    
    def update_animations(self, physics_data):
        """Update visual animations based on flight state"""
        speed = physics_data['speed']
        
        # Wing animation based on speed and glide state
        self.wing_beat_time += time.dt * speed * 0.5
        wing_flap = math.sin(self.wing_beat_time) * (20 - speed * 0.5)  # Less flap at higher speeds
        
        # Update wing positions
        base_wing_angle = 15
        self.left_wing.rotation_z = base_wing_angle + wing_flap
        self.right_wing.rotation_z = -base_wing_angle - wing_flap
        
        # Tail animation for steering
        tail_angle = self.yaw_input * 10
        self.tail.rotation_y = tail_angle
        self.tail_membrane.rotation_y = tail_angle * 0.5
        
        # Body orientation
        self.rotation_x = math.degrees(math.atan2(-self.physics.velocity.y, 
                                                abs(self.physics.velocity.z) + 0.1))
        self.rotation_y += self.yaw_input * 60 * time.dt
        self.rotation_z = self.roll_input * 30
    
    def update_effects(self, physics_data):
        """Update visual effects"""
        speed = physics_data['speed']
        
        # Update particle trail
        if speed > 5:  # Only show trail at higher speeds
            for i, particle in enumerate(self.trail_entities):
                particle.visible = True
                trail_pos = self.position - self.forward * (i + 1) * 0.5
                particle.position = trail_pos
                particle.color = color.rgba(255, 255, 255, max(0, 150 - i*30 - int(speed*5)))
        else:
            for particle in self.trail_entities:
                particle.visible = False
    
    def get_flight_data(self):
        """Get current flight data for UI display"""
        return {
            'speed': distance(self.physics.velocity, Vec3(0, 0, 0)),
            'altitude': self.position.y,
            'heading': self.rotation_y,
            'pitch': self.rotation_x,
            'roll': self.rotation_z,
            'velocity': self.physics.velocity,
            'g_force': getattr(self.physics, 'g_force', 1.0)
        } 