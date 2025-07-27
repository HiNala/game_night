"""
Enhanced Flying Squirrel Entity - Optimized for Overhead View
Advanced 3D model with realistic flight behavior and better visibility from above.
"""

from ursina import *
import math
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from physics.flight_physics import FlightPhysics

class FlyingSquirrel(Entity):
    """Enhanced flying squirrel optimized for overhead camera view"""
    
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        
        # Scale up for better visibility from overhead
        self.base_scale = 1.5  # Larger than before
        
        # Create detailed squirrel model
        self.create_overhead_optimized_model()
        
        # Initialize physics engine
        self.physics = FlightPhysics(self, config)
        
        # Flight state
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        # Animation state
        self.wing_beat_time = 0
        self.glide_factor = 0
        
        # Visual state for overhead view
        self.altitude_shadow = None
        self.create_altitude_indicators()
        
        # Start position
        self.position = Vec3(0, config.get('start_altitude', 25), 0)
        
        # Visual effects optimized for overhead view
        self.create_overhead_effects()
    
    def create_overhead_optimized_model(self):
        """Create squirrel model optimized for overhead viewing"""
        
        # Main body - more elongated and visible from above
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(139, 69, 19),  # Saddle brown
            scale=(2.0 * self.base_scale, 0.8 * self.base_scale, 1.2 * self.base_scale),
            position=(0, 0, 0)
        )
        
        # Head - larger and more prominent
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(160, 82, 45),  # Lighter brown
            scale=(1.0 * self.base_scale, 0.8 * self.base_scale, 0.8 * self.base_scale),
            position=(0, 0, 0.8 * self.base_scale)
        )
        
        # Eyes - more visible from above
        eye_size = 0.2 * self.base_scale
        self.left_eye = Entity(
            parent=self.head,
            model='sphere',
            color=color.black,
            scale=(eye_size, eye_size, eye_size),
            position=(-0.25 * self.base_scale, 0.2 * self.base_scale, 0.2 * self.base_scale)
        )
        
        self.right_eye = Entity(
            parent=self.head,
            model='sphere',
            color=color.black,
            scale=(eye_size, eye_size, eye_size),
            position=(0.25 * self.base_scale, 0.2 * self.base_scale, 0.2 * self.base_scale)
        )
        
        # Gliding membrane (patagium) - much more prominent for overhead view
        wing_length = 3.5 * self.base_scale
        wing_width = 1.8 * self.base_scale
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 220),  # Semi-transparent brown
            scale=(wing_length, 0.08 * self.base_scale, wing_width),
            position=(-wing_length/2 - 0.5, 0, 0),
            rotation=(0, 0, 10)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 220),
            scale=(wing_length, 0.08 * self.base_scale, wing_width),
            position=(wing_length/2 + 0.5, 0, 0),
            rotation=(0, 0, -10)
        )
        
        # Wing edges for better definition
        self.left_wing_edge = Entity(
            parent=self.left_wing,
            model='cube',
            color=color.rgb(101, 67, 33),  # Darker edge
            scale=(1.0, 1.5, 0.1),
            position=(0.4, 0, 0.45)
        )
        
        self.right_wing_edge = Entity(
            parent=self.right_wing,
            model='cube',
            color=color.rgb(101, 67, 33),
            scale=(1.0, 1.5, 0.1),
            position=(-0.4, 0, 0.45)
        )
        
        # Tail membrane - more visible
        self.tail_membrane = Entity(
            parent=self,
            model='cube',
            color=color.rgba(139, 69, 19, 200),
            scale=(1.4 * self.base_scale, 0.08 * self.base_scale, 1.0 * self.base_scale),
            position=(0, 0, -1.5 * self.base_scale),
            rotation=(5, 0, 0)
        )
        
        # Tail - more prominent
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(139, 69, 19),
            scale=(0.4 * self.base_scale, 0.4 * self.base_scale, 2.0 * self.base_scale),
            position=(0, 0, -2.0 * self.base_scale)
        )
        
        # Legs - more visible from above
        leg_positions = [
            (-0.6 * self.base_scale, 0.3 * self.base_scale), 
            (0.6 * self.base_scale, 0.3 * self.base_scale), 
            (-0.6 * self.base_scale, -0.3 * self.base_scale), 
            (0.6 * self.base_scale, -0.3 * self.base_scale)
        ]
        
        for i, (x, z) in enumerate(leg_positions):
            leg = Entity(
                parent=self,
                model='cube',
                color=color.rgb(101, 67, 33),
                scale=(0.25 * self.base_scale, 1.0 * self.base_scale, 0.25 * self.base_scale),
                position=(x, -0.6 * self.base_scale, z)
            )
    
    def create_altitude_indicators(self):
        """Create visual indicators for altitude awareness in overhead view"""
        
        # Shadow on ground for altitude reference
        self.altitude_shadow = Entity(
            model='cube',
            color=color.rgba(0, 0, 0, 100),  # Semi-transparent black
            scale=(3 * self.base_scale, 0.02, 3 * self.base_scale),
            position=(0, 0.1, 0)  # Will be updated dynamically
        )
        
        # Altitude line (connects squirrel to shadow)
        self.altitude_line = Entity(
            model='cube',
            color=color.rgba(255, 255, 255, 150),
            scale=(0.05, 1, 0.05),
            visible=False  # Only show when useful
        )
    
    def create_overhead_effects(self):
        """Create visual effects optimized for overhead view"""
        self.trail_entities = []
        
        # Larger, more visible trail particles
        for i in range(8):  # More trail particles
            trail_particle = Entity(
                parent=scene,
                model='cube',
                color=color.rgba(255, 255, 255, 120 - i*15),
                scale=0.3 - i*0.03,  # Larger particles
                visible=False
            )
            self.trail_entities.append(trail_particle)
        
        # Wing tip vortices for high-speed flight
        self.left_vortex = Entity(
            parent=scene,
            model='cube',
            color=color.rgba(150, 150, 255, 100),
            scale=0.2,
            visible=False
        )
        
        self.right_vortex = Entity(
            parent=scene,
            model='cube',
            color=color.rgba(150, 150, 255, 100),
            scale=0.2,
            visible=False
        )
    
    def update(self):
        """Update squirrel physics and animations for overhead view"""
        dt = time.dt
        
        # Handle input
        self.handle_input()
        
        # Update physics
        physics_data = self.physics.update(dt)
        
        # Update animations for overhead view
        self.update_overhead_animations(physics_data)
        
        # Update visual effects
        self.update_overhead_effects(physics_data)
        
        # Update altitude indicators
        self.update_altitude_indicators()
        
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
    
    def update_overhead_animations(self, physics_data):
        """Update visual animations optimized for overhead view"""
        speed = physics_data['speed']
        
        # Wing animation - more pronounced for overhead visibility
        self.wing_beat_time += time.dt * speed * 0.8
        wing_flap = math.sin(self.wing_beat_time) * (15 - speed * 0.3)
        
        # Update wing positions with more dramatic movement
        base_wing_angle = 10
        self.left_wing.rotation_z = base_wing_angle + wing_flap
        self.right_wing.rotation_z = -base_wing_angle - wing_flap
        
        # Wing edge animation
        edge_flap = wing_flap * 0.5
        self.left_wing_edge.rotation_z = edge_flap
        self.right_wing_edge.rotation_z = -edge_flap
        
        # Tail animation for steering - more visible
        tail_angle = self.yaw_input * 15
        self.tail.rotation_y = tail_angle
        self.tail_membrane.rotation_y = tail_angle * 0.7
        
        # Body orientation based on flight
        self.rotation_x = math.degrees(math.atan2(-self.physics.velocity.y, 
                                                abs(self.physics.velocity.z) + 0.1))
        self.rotation_y += self.yaw_input * 45 * time.dt
        self.rotation_z = self.roll_input * 25
        
        # Scale effects based on speed for dramatic effect
        speed_scale = 1.0 + (speed * 0.02)  # Slight size increase at high speed
        self.body.scale = (2.0 * self.base_scale * speed_scale, 
                          0.8 * self.base_scale, 
                          1.2 * self.base_scale)
    
    def update_overhead_effects(self, physics_data):
        """Update visual effects for overhead view"""
        speed = physics_data['speed']
        
        # Update particle trail - more dramatic
        if speed > 3:
            for i, particle in enumerate(self.trail_entities):
                particle.visible = True
                trail_pos = self.position - self.forward * (i + 1) * 1.0  # Longer trail
                particle.position = trail_pos
                particle.color = color.rgba(255, 255, 255, max(0, 120 - i*15 - int(speed*3)))
        else:
            for particle in self.trail_entities:
                particle.visible = False
        
        # Wing tip vortices at high speed
        if speed > 15:
            self.left_vortex.visible = True
            self.right_vortex.visible = True
            
            # Position vortices at wing tips
            left_wing_tip = self.position + self.left * 3 * self.base_scale
            right_wing_tip = self.position + self.right * 3 * self.base_scale
            
            self.left_vortex.position = left_wing_tip
            self.right_vortex.position = right_wing_tip
            
            # Animate vortices
            vortex_alpha = int(min(255, (speed - 15) * 10))
            self.left_vortex.color = color.rgba(150, 150, 255, vortex_alpha)
            self.right_vortex.color = color.rgba(150, 150, 255, vortex_alpha)
        else:
            self.left_vortex.visible = False
            self.right_vortex.visible = False
    
    def update_altitude_indicators(self):
        """Update altitude reference indicators"""
        # Update shadow position on ground
        if self.altitude_shadow:
            # Position shadow on ground below squirrel
            shadow_y = 0.1  # Just above ground
            self.altitude_shadow.position = Vec3(self.x, shadow_y, self.z)
            
            # Scale shadow based on altitude (higher = larger shadow)
            altitude_factor = min(2.0, self.y / 20)  # Max 2x size at 20m altitude
            shadow_scale = 3 * self.base_scale * altitude_factor
            self.altitude_shadow.scale = (shadow_scale, 0.02, shadow_scale)
            
            # Shadow opacity based on altitude
            shadow_alpha = max(50, min(150, int(200 - self.y * 3)))
            self.altitude_shadow.color = color.rgba(0, 0, 0, shadow_alpha)
        
        # Show altitude line when helpful (high altitude or fast descent)
        if self.altitude_line:
            if self.y > 15 or self.physics.velocity.y < -5:
                self.altitude_line.visible = True
                line_length = self.y - 0.1
                self.altitude_line.position = Vec3(self.x, self.y - line_length/2, self.z)
                self.altitude_line.scale = (0.05, line_length, 0.05)
            else:
                self.altitude_line.visible = False
    
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