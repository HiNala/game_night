"""
🦅 REALISTIC FLYING CHARACTER SYSTEM 🦅
Ultra-realistic flying character with advanced controls, animations, and physics integration.
"""

import math
import random
from ursina import *

class RealisticFlyingCharacter(Entity):
    """Ultra-realistic flying character with detailed physics and animations"""
    
    def __init__(self, character_type='archaeopteryx', enhanced_physics=None):
        super().__init__()
        
        self.character_type = character_type
        self.enhanced_physics = enhanced_physics
        
        # Character scaling for visibility
        self.base_scale = 2.5
        
        # Physical properties
        self.wing_span = 4.0 * self.base_scale
        self.body_length = 2.0 * self.base_scale
        self.mass = 1.5  # kg
        
        # Control system
        self.control_scheme = 'realistic'  # realistic, arcade, expert
        self.control_sensitivity = 1.0
        self.control_smoothing = 0.85
        
        # Control inputs (smoothed)
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        self.throttle_input = 0
        
        # Flight state
        self.energy_level = 1.0
        self.stamina = 1.0
        self.stress_level = 0.0  # G-force and maneuver stress
        
        # Animation system
        self.wing_beat_frequency = 0
        self.wing_beat_amplitude = 0
        self.body_attitude = Vec3(0, 0, 0)
        self.head_tracking = Vec3(0, 0, 0)
        
        # Advanced features
        self.thermal_sensitivity = 0.8
        self.wind_awareness = 0.9
        self.predator_alertness = 0.7
        
        # Create character model
        self.create_realistic_model()
        
        # Set initial position
        self.position = Vec3(-50, 60, 80)
        
        print(f"🦅 Realistic flying character created: {character_type}")
    
    def create_realistic_model(self):
        """Create highly detailed character model"""
        if self.character_type == 'archaeopteryx':
            self.create_archaeopteryx_model()
        elif self.character_type == 'pteranodon':
            self.create_pteranodon_model()
        elif self.character_type == 'dragon':
            self.create_dragon_model()
        elif self.character_type == 'eagle':
            self.create_eagle_model()
        else:
            self.create_archaeopteryx_model()  # Default
        
        # Add universal enhancements
        self.add_advanced_details()
    
    def create_archaeopteryx_model(self):
        """Create detailed Archaeopteryx model"""
        # Main body (torpedo-shaped for aerodynamics)
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(80, 60, 40),
            scale=(self.body_length, 0.8 * self.base_scale, 1.2 * self.base_scale),
            position=(0, 0, 0)
        )
        
        # Head with intelligent features
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(90, 70, 50),
            scale=(1.0 * self.base_scale, 0.8 * self.base_scale, 0.8 * self.base_scale),
            position=(0, 0.2 * self.base_scale, 1.2 * self.base_scale)
        )
        
        # Intelligent eyes that track movement
        for eye_x in [-0.3, 0.3]:
            eye = Entity(
                parent=self.head,
                model='sphere',
                color=color.orange,
                scale=0.25 * self.base_scale,
                position=(eye_x * self.base_scale, 0.2, 0.3)
            )
            
            # Eye pupil for detail
            pupil = Entity(
                parent=eye,
                model='sphere',
                color=color.black,
                scale=0.6,
                position=(0, 0, 0.5)
            )
        
        # Detailed beak with realistic proportions
        self.beak = Entity(
            parent=self.head,
            model='cube',
            color=color.rgb(40, 40, 30),
            scale=(0.25, 0.25, 0.8 * self.base_scale),
            position=(0, 0, 0.8 * self.base_scale)
        )
        
        # Advanced wing structure
        self.create_detailed_wings()
        
        # Feathered tail with individual control surfaces
        self.create_detailed_tail()
        
        # Legs and feet for perching
        self.create_realistic_legs()
    
    def create_detailed_wings(self):
        """Create anatomically correct wing structure"""
        wing_length = self.wing_span / 2
        
        # Wing bones (humerus, radius, ulna simulation)
        for side, sign in [('left', -1), ('right', 1)]:
            # Main wing structure
            wing = Entity(
                parent=self,
                model='cube',
                color=color.rgba(80, 60, 40, 240),
                scale=(wing_length, 0.15 * self.base_scale, 2.0 * self.base_scale),
                position=(sign * (wing_length/2 + 0.8), 0, 0),
                rotation=(0, 0, sign * 8)
            )
            
            # Wing segments for realistic bending
            segments = []
            for i in range(3):
                segment_length = wing_length / 3
                segment = Entity(
                    parent=wing,
                    model='cube',
                    color=color.rgba(75, 55, 35, 220),
                    scale=(segment_length, 0.8, 1.5 - i * 0.2),
                    position=(sign * segment_length * (i - 1), 0, 0),
                    rotation=(0, 0, i * sign * 3)
                )
                segments.append(segment)
            
            # Wing feathers (primary, secondary)
            for i in range(5):
                feather_pos = wing_length * 0.3 + i * wing_length * 0.15
                feather = Entity(
                    parent=wing,
                    model='cube',
                    color=color.rgba(70, 50, 30, 200),
                    scale=(wing_length * 0.15, 0.05, 1.8 - i * 0.2),
                    position=(sign * feather_pos, 0, 0.8),
                    rotation=(0, 0, i * sign * 5)
                )
            
            # Wing tip for aerodynamic efficiency
            wing_tip = Entity(
                parent=wing,
                model='cube',
                color=color.rgba(60, 40, 20, 180),
                scale=(wing_length * 0.2, 0.08, 0.8),
                position=(sign * wing_length * 0.8, 0, 0.6),
                rotation=(0, 0, sign * 15)
            )
            
            # Store wing references
            if side == 'left':
                self.left_wing = wing
                self.left_wing_segments = segments
                self.left_wing_tip = wing_tip
            else:
                self.right_wing = wing
                self.right_wing_segments = segments
                self.right_wing_tip = wing_tip
    
    def create_detailed_tail(self):
        """Create detailed tail with control surfaces"""
        # Main tail structure
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(70, 50, 30),
            scale=(0.6 * self.base_scale, 0.4 * self.base_scale, 3.0 * self.base_scale),
            position=(0, 0, -2.5 * self.base_scale)
        )
        
        # Tail feathers (individual control)
        self.tail_feathers = []
        for i in range(7):
            angle = (i - 3) * 15  # Spread feathers
            feather = Entity(
                parent=self.tail,
                model='cube',
                color=color.rgba(60, 40, 20, 200),
                scale=(0.8, 0.05, 0.6),
                position=(0, 0.3, -1.2),
                rotation=(0, 0, angle)
            )
            self.tail_feathers.append(feather)
    
    def create_realistic_legs(self):
        """Create detailed legs and feet"""
        for leg_x in [-0.6, 0.6]:
            # Upper leg
            upper_leg = Entity(
                parent=self,
                model='cube',
                color=color.rgb(40, 30, 20),
                scale=(0.3 * self.base_scale, 0.8 * self.base_scale, 0.3 * self.base_scale),
                position=(leg_x * self.base_scale, -0.6 * self.base_scale, 0.2)
            )
            
            # Lower leg
            lower_leg = Entity(
                parent=upper_leg,
                model='cube',
                color=color.rgb(35, 25, 15),
                scale=(0.8, 1.2, 0.8),
                position=(0, -0.8, 0)
            )
            
            # Foot with talons
            foot = Entity(
                parent=lower_leg,
                model='cube',
                color=color.rgb(30, 20, 10),
                scale=(1.2, 0.4, 1.5),
                position=(0, -0.8, 0.3)
            )
            
            # Individual talons
            for talon_i in range(3):
                talon = Entity(
                    parent=foot,
                    model='cube',
                    color=color.rgb(20, 15, 10),
                    scale=(0.3, 0.2, 0.8),
                    position=((talon_i - 1) * 0.4, -0.3, 0.8),
                    rotation=(15, 0, 0)
                )
    
    def add_advanced_details(self):
        """Add advanced visual details"""
        # Breathing animation reference
        self.breathing_time = 0
        
        # Eye tracking system
        self.eye_target = Vec3(0, 0, 1)
        
        # Muscle tension visualization
        self.muscle_tension = 0
        
        # Feather ruffling
        self.feather_ruffle = 0
    
    def update_advanced_controls(self, dt):
        """Handle advanced control input with realistic response"""
        # Raw control inputs
        raw_pitch = 0
        raw_yaw = 0
        raw_roll = 0
        raw_throttle = 0
        
        # Basic flight controls
        if held_keys['w']:
            raw_pitch = 1
        elif held_keys['s']:
            raw_pitch = -1
        
        if held_keys['a']:
            raw_yaw = 1
            raw_roll = 0.5  # Coordinated turn
        elif held_keys['d']:
            raw_yaw = -1
            raw_roll = -0.5
        
        # Advanced controls
        if held_keys['space']:
            raw_throttle = 1  # Energy input (flapping)
        
        if held_keys['shift']:
            raw_pitch -= 0.8  # Dive input
        
        if held_keys['q']:
            raw_roll += 0.8  # Additional roll control
        elif held_keys['e']:
            raw_roll -= 0.8
        
        # Control scheme modifications
        if self.control_scheme == 'realistic':
            # Realistic response with delays and limitations
            control_effectiveness = self.get_control_effectiveness()
            
            raw_pitch *= control_effectiveness * self.control_sensitivity
            raw_yaw *= control_effectiveness * self.control_sensitivity * 0.8
            raw_roll *= control_effectiveness * self.control_sensitivity * 1.2
            
        elif self.control_scheme == 'arcade':
            # More responsive, less realistic
            raw_pitch *= 1.5 * self.control_sensitivity
            raw_yaw *= 1.5 * self.control_sensitivity
            raw_roll *= 1.5 * self.control_sensitivity
        
        # Apply control smoothing
        self.pitch_input = lerp(self.pitch_input, raw_pitch, 1 - self.control_smoothing)
        self.yaw_input = lerp(self.yaw_input, raw_yaw, 1 - self.control_smoothing)
        self.roll_input = lerp(self.roll_input, raw_roll, 1 - self.control_smoothing)
        self.throttle_input = lerp(self.throttle_input, raw_throttle, 1 - self.control_smoothing)
        
        # Apply to physics system
        if self.enhanced_physics:
            self.enhanced_physics.apply_control_input(
                self.pitch_input,
                self.yaw_input,
                self.roll_input,
                dt
            )
    
    def get_control_effectiveness(self):
        """Calculate control effectiveness based on flight conditions"""
        base_effectiveness = 1.0
        
        # Airspeed factor
        if hasattr(self.enhanced_physics, 'airspeed'):
            airspeed = self.enhanced_physics.airspeed
            if airspeed < 5:
                base_effectiveness *= 0.3  # Poor control at low speed
            elif airspeed > 30:
                base_effectiveness *= 1.2  # Better control at high speed
        
        # Energy factor
        base_effectiveness *= (0.5 + self.energy_level * 0.5)
        
        # Stress factor
        base_effectiveness *= (1.0 - self.stress_level * 0.3)
        
        return max(0.1, min(1.5, base_effectiveness))
    
    def update_realistic_animations(self, dt):
        """Update detailed character animations"""
        
        # Get flight data
        if self.enhanced_physics:
            speed = self.enhanced_physics.ground_speed
            climb_rate = self.enhanced_physics.climb_rate
            g_force = self.enhanced_physics.g_force
        else:
            speed = distance(getattr(self, 'velocity', Vec3(0, 0, 0)), Vec3(0, 0, 0))
            climb_rate = 0
            g_force = 1.0
        
        # Wing animation based on flight mode
        self.update_wing_animation(speed, climb_rate, dt)
        
        # Body attitude based on flight forces
        self.update_body_attitude(g_force, dt)
        
        # Head tracking and awareness
        self.update_head_tracking(dt)
        
        # Breathing animation
        self.update_breathing_animation(dt)
        
        # Tail control surface animation
        self.update_tail_animation(dt)
        
        # Stress and fatigue effects
        self.update_stress_effects(g_force, dt)
    
    def update_wing_animation(self, speed, climb_rate, dt):
        """Realistic wing flapping based on flight conditions"""
        
        # Determine flight mode
        if speed < 8:
            # Slow flight - high frequency flapping
            self.wing_beat_frequency = 6.0
            self.wing_beat_amplitude = 35
        elif speed > 20:
            # Fast flight - soaring with minimal flapping
            self.wing_beat_frequency = 1.0
            self.wing_beat_amplitude = 10
        else:
            # Cruise flight
            self.wing_beat_frequency = 3.0
            self.wing_beat_amplitude = 20
        
        # Climbing requires more power
        if climb_rate > 2:
            self.wing_beat_frequency *= 1.5
            self.wing_beat_amplitude *= 1.3
        
        # Energy affects wing beat
        energy_factor = (0.5 + self.energy_level * 0.5)
        self.wing_beat_frequency *= energy_factor
        
        # Calculate wing positions
        wing_time = time.time() * self.wing_beat_frequency
        base_flap = math.sin(wing_time) * self.wing_beat_amplitude
        
        # Asymmetric flapping for turns
        left_flap = base_flap + self.roll_input * 10
        right_flap = base_flap - self.roll_input * 10
        
        # Apply wing rotations
        self.left_wing.rotation_z = 8 + left_flap
        self.right_wing.rotation_z = -8 - right_flap
        
        # Wing segment bending for realism
        for i, segment in enumerate(self.left_wing_segments):
            bend_factor = (i + 1) * 0.3
            segment.rotation_z = left_flap * bend_factor * 0.2
        
        for i, segment in enumerate(self.right_wing_segments):
            bend_factor = (i + 1) * 0.3
            segment.rotation_z = -right_flap * bend_factor * 0.2
    
    def update_body_attitude(self, g_force, dt):
        """Update body attitude based on flight forces"""
        
        # Pitch attitude from velocity
        if hasattr(self.enhanced_physics, 'velocity'):
            velocity = self.enhanced_physics.velocity
            if distance(velocity, Vec3(0, 0, 0)) > 1:
                pitch_angle = math.degrees(math.atan2(-velocity.y, abs(velocity.z) + 0.1))
                self.body_attitude.x = lerp(self.body_attitude.x, pitch_angle, 2 * dt)
        
        # Roll from control input
        target_roll = self.roll_input * 45
        self.body_attitude.z = lerp(self.body_attitude.z, target_roll, 3 * dt)
        
        # Yaw from turn coordination
        target_yaw = self.yaw_input * 20
        self.body_attitude.y = lerp(self.body_attitude.y, target_yaw, 2 * dt)
        
        # Apply attitudes
        self.rotation_x = self.body_attitude.x
        self.rotation_y = self.body_attitude.y
        self.rotation_z = self.body_attitude.z
        
        # G-force effects on posture
        if g_force > 2:
            # Tension under high G
            self.muscle_tension = min(1.0, (g_force - 1) * 0.5)
        else:
            self.muscle_tension = max(0, self.muscle_tension - dt)
    
    def update_head_tracking(self, dt):
        """Intelligent head tracking and awareness"""
        
        # Look in direction of turn
        head_yaw_target = self.yaw_input * 30
        
        # Look ahead when diving or climbing
        head_pitch_target = -self.pitch_input * 20
        
        # Random scanning behavior (predator awareness)
        if random.random() < 0.01:  # 1% chance per frame
            self.eye_target = Vec3(
                random.uniform(-1, 1),
                random.uniform(-0.5, 0.5),
                random.uniform(0.5, 1)
            ).normalized()
        
        # Apply head movements
        self.head.rotation_y = lerp(self.head.rotation_y, head_yaw_target, 4 * dt)
        self.head.rotation_x = lerp(self.head.rotation_x, head_pitch_target, 3 * dt)
    
    def update_breathing_animation(self, dt):
        """Subtle breathing animation for realism"""
        self.breathing_time += dt * 2  # Breathing rate
        
        breathing_factor = math.sin(self.breathing_time) * 0.05 + 1
        
        # Apply to body scale
        self.body.scale = (
            self.body_length,
            0.8 * self.base_scale * breathing_factor,
            1.2 * self.base_scale
        )
    
    def update_tail_animation(self, dt):
        """Tail feather control for flight stability"""
        
        # Tail acts as rudder
        tail_deflection = self.yaw_input * 15
        
        # Individual feather control
        for i, feather in enumerate(self.tail_feathers):
            feather_angle = (i - 3) * 15 + tail_deflection
            
            # Add some flutter in turbulence
            if hasattr(self.enhanced_physics, 'turbulence_intensity'):
                turbulence = self.enhanced_physics.turbulence_intensity
                flutter = math.sin(time.time() * 8 + i) * turbulence * 5
                feather_angle += flutter
            
            feather.rotation_z = feather_angle
    
    def update_stress_effects(self, g_force, dt):
        """Update stress and fatigue effects"""
        
        # Calculate stress from G-force and maneuvers
        stress_input = 0
        
        if g_force > 2:
            stress_input += (g_force - 2) * 0.5
        
        if abs(self.roll_input) > 0.7:
            stress_input += 0.2
        
        if abs(self.pitch_input) > 0.8:
            stress_input += 0.3
        
        # Update stress level
        self.stress_level = max(0, min(1, self.stress_level + stress_input * dt - 0.1 * dt))
        
        # Energy consumption
        energy_consumption = 0.05 * dt  # Base consumption
        
        if self.throttle_input > 0:
            energy_consumption += self.throttle_input * 0.2 * dt
        
        if speed > 25:
            energy_consumption += 0.1 * dt
        
        self.energy_level = max(0, self.energy_level - energy_consumption)
        
        # Energy regeneration (rest and thermals)
        if hasattr(self.enhanced_physics, 'thermal_strength'):
            thermal_regen = self.enhanced_physics.thermal_strength * 0.05 * dt
            self.energy_level = min(1, self.energy_level + thermal_regen)
        
        # Gradual energy recovery when not under stress
        if self.stress_level < 0.3 and self.throttle_input < 0.2:
            self.energy_level = min(1, self.energy_level + 0.02 * dt)
    
    def update(self, dt):
        """Main update function"""
        
        # Handle advanced controls
        self.update_advanced_controls(dt)
        
        # Update physics if available
        if self.enhanced_physics:
            physics_data = self.enhanced_physics.update(dt)
        else:
            physics_data = {'speed': 0, 'altitude': self.position.y}
        
        # Update animations
        self.update_realistic_animations(dt)
        
        # Keep above ground
        if self.y < 1:
            self.y = 1
            if hasattr(self.enhanced_physics, 'velocity'):
                self.enhanced_physics.velocity.y = max(0, self.enhanced_physics.velocity.y)
        
        return physics_data
    
    def set_control_scheme(self, scheme):
        """Change control scheme (realistic, arcade, expert)"""
        self.control_scheme = scheme
        
        if scheme == 'realistic':
            self.control_sensitivity = 1.0
            self.control_smoothing = 0.85
        elif scheme == 'arcade':
            self.control_sensitivity = 1.5
            self.control_smoothing = 0.6
        elif scheme == 'expert':
            self.control_sensitivity = 0.8
            self.control_smoothing = 0.95
        
        print(f"🎮 Control scheme changed to: {scheme}")
    
    def get_flight_data(self):
        """Get comprehensive flight data for UI"""
        data = {
            'energy_level': self.energy_level,
            'stamina': self.stamina,
            'stress_level': self.stress_level,
            'control_scheme': self.control_scheme,
            'wing_beat_frequency': self.wing_beat_frequency,
            'muscle_tension': self.muscle_tension
        }
        
        if self.enhanced_physics:
            data.update({
                'speed': self.enhanced_physics.ground_speed,
                'airspeed': self.enhanced_physics.airspeed,
                'altitude': self.position.y,
                'climb_rate': self.enhanced_physics.climb_rate,
                'g_force': self.enhanced_physics.g_force,
                'angle_of_attack': math.degrees(self.enhanced_physics.angle_of_attack),
                'thermal_strength': self.enhanced_physics.thermal_strength,
                'energy_altitude': self.enhanced_physics.energy_altitude,
                'glide_ratio': self.enhanced_physics.glide_performance
            })
        
        return data 