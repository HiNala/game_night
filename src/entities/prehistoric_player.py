"""
Prehistoric Player Entity - Epic Flying Creature for San Francisco
The player's flying creature in the prehistoric San Francisco world.
Senior developer quality with maximum epic factor.
"""

from ursina import *
import math
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from physics.flight_physics import FlightPhysics

class PrehistoricPlayer(Entity):
    """Player's flying creature - enhanced for prehistoric San Francisco"""
    
    def __init__(self, creature_type='archaeopteryx', config=None):
        super().__init__()
        
        self.creature_type = creature_type
        self.config = config or self.get_default_config()
        
        # Enhanced scale for epic visibility
        self.base_scale = 2.0
        
        # Create the player creature model
        self.create_player_model()
        
        # Initialize enhanced physics
        self.physics = FlightPhysics(self, self.config)
        
        # Flight state
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        # Animation and visual state
        self.wing_beat_time = 0
        self.energy = 1.0
        self.stamina = 1.0
        
        # Prehistoric abilities
        self.has_fire_breath = (creature_type == 'dragon')
        self.echolocation = (creature_type == 'bat')
        self.thermal_vision = True  # All prehistoric flyers are expert thermal hunters
        
        # Start position
        self.position = Vec3(-50, 60, 80)  # Start near Golden Gate Bridge
        
        # Enhanced visual effects for epic gameplay
        self.create_epic_effects()
        
        # Interaction state
        self.nearby_pterodactyls = []
        self.reputation = 0  # How pterodactyls view the player (-1 to 1)
    
    def get_default_config(self):
        """Default configuration for player creature"""
        return {
            'max_speed': 35,
            'glide_ratio': 5.0,
            'lift_coefficient': 1.0,
            'drag_coefficient': 0.015,
            'mass': 8,  # Lighter than pterodactyls for agility
            'wing_area': 4.0,
            'max_pitch_rate': 3.0,
            'max_yaw_rate': 3.0,
            'max_roll_angle': 0.8,
            'start_altitude': 60,
        }
    
    def create_player_model(self):
        """Create epic player creature model"""
        
        if self.creature_type == 'archaeopteryx':
            self.create_archaeopteryx_model()
        elif self.creature_type == 'dragon':
            self.create_dragon_model()
        elif self.creature_type == 'pterodactyl':
            self.create_player_pterodactyl_model()
        else:
            self.create_archaeopteryx_model()  # Default
    
    def create_archaeopteryx_model(self):
        """Create Archaeopteryx - the first bird, perfect for SF flying"""
        
        # Body with feathers
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(80, 60, 40),  # Dark brown with iridescent sheen
            scale=(2.5 * self.base_scale, 1.0 * self.base_scale, 1.5 * self.base_scale),
            position=(0, 0, 0)
        )
        
        # Feathered head
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(90, 70, 50),
            scale=(1.2 * self.base_scale, 1.0 * self.base_scale, 1.0 * self.base_scale),
            position=(0, 0.3 * self.base_scale, 1.2 * self.base_scale)
        )
        
        # Sharp predator eyes
        for eye_x in [-0.4, 0.4]:
            eye = Entity(
                parent=self.head,
                model='sphere',
                color=color.orange,  # Predator eyes
                scale=0.25 * self.base_scale,
                position=(eye_x * self.base_scale, 0.2, 0.3)
            )
        
        # Toothed beak (archaeopteryx had teeth!)
        self.beak = Entity(
            parent=self.head,
            model='cube',
            color=color.rgb(40, 40, 30),
            scale=(0.3, 0.3, 0.8 * self.base_scale),
            position=(0, 0, 0.8 * self.base_scale)
        )
        
        # Feathered wings with claw tips
        wing_length = 4 * self.base_scale
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2 * self.base_scale),
            position=(-wing_length/2 - 0.8, 0, 0),
            rotation=(0, 0, 12)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(80, 60, 40, 240),
            scale=(wing_length, 0.15 * self.base_scale, 2 * self.base_scale),
            position=(wing_length/2 + 0.8, 0, 0),
            rotation=(0, 0, -12)
        )
        
        # Wing claws (archaeopteryx could climb!)
        for wing in [self.left_wing, self.right_wing]:
            claw = Entity(
                parent=wing,
                model='cube',
                color=color.rgb(30, 30, 20),
                scale=(0.2, 0.1, 0.3),
                position=(wing_length * 0.4, 0, 0.8)
            )
        
        # Long feathered tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(70, 50, 30),
            scale=(0.6 * self.base_scale, 0.4 * self.base_scale, 3 * self.base_scale),
            position=(0, 0, -2.5 * self.base_scale)
        )
        
        # Tail feathers
        for i in range(5):
            tail_feather = Entity(
                parent=self.tail,
                model='cube',
                color=color.rgba(60, 40, 20, 200),
                scale=(0.8, 0.05, 0.4),
                position=(0, 0.3, -1.2 + i * 0.3),
                rotation=(0, 0, random.uniform(-10, 10))
            )
        
        # Legs with sharp talons
        for leg_x in [-0.6, 0.6]:
            leg = Entity(
                parent=self,
                model='cube',
                color=color.rgb(40, 30, 20),
                scale=(0.3 * self.base_scale, 1.2 * self.base_scale, 0.3 * self.base_scale),
                position=(leg_x * self.base_scale, -0.8 * self.base_scale, 0)
            )
            
            # Talons
            talon = Entity(
                parent=leg,
                model='cube',
                color=color.rgb(20, 20, 15),
                scale=(0.8, 0.2, 0.4),
                position=(0, -0.7, 0.2)
            )
    
    def create_dragon_model(self):
        """Create small dragon model - because why not in prehistoric SF!"""
        
        # Dragon body
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(120, 20, 20),  # Dragon red
            scale=(3 * self.base_scale, 1.2 * self.base_scale, 1.8 * self.base_scale),
            position=(0, 0, 0)
        )
        
        # Dragon head with horns
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(140, 30, 30),
            scale=(1.5 * self.base_scale, 1.2 * self.base_scale, 1.2 * self.base_scale),
            position=(0, 0.4 * self.base_scale, 1.5 * self.base_scale)
        )
        
        # Dragon horns
        for horn_x in [-0.3, 0.3]:
            horn = Entity(
                parent=self.head,
                model='cube',
                color=color.rgb(80, 80, 70),
                scale=(0.2, 1, 0.2),
                position=(horn_x * self.base_scale, 0.8, 0)
            )
        
        # Fire-breathing mouth
        self.mouth = Entity(
            parent=self.head,
            model='cube',
            color=color.rgb(200, 100, 50),  # Glowing mouth
            scale=(0.8, 0.4, 0.6),
            position=(0, 0, 0.8)
        )
        
        # Dragon eyes
        for eye_x in [-0.4, 0.4]:
            eye = Entity(
                parent=self.head,
                model='sphere',
                color=color.yellow,
                scale=0.3 * self.base_scale,
                position=(eye_x * self.base_scale, 0.3, 0.4)
            )
        
        # Bat-like dragon wings
        wing_length = 5 * self.base_scale
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(100, 15, 15, 220),
            scale=(wing_length, 0.1 * self.base_scale, 3 * self.base_scale),
            position=(-wing_length/2 - 1, 0, 0),
            rotation=(0, 0, 15)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(100, 15, 15, 220),
            scale=(wing_length, 0.1 * self.base_scale, 3 * self.base_scale),
            position=(wing_length/2 + 1, 0, 0),
            rotation=(0, 0, -15)
        )
        
        # Dragon tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=color.rgb(110, 25, 25),
            scale=(0.8 * self.base_scale, 0.6 * self.base_scale, 4 * self.base_scale),
            position=(0, 0, -3 * self.base_scale)
        )
    
    def create_player_pterodactyl_model(self):
        """Create player pterodactyl - smaller and more agile than NPCs"""
        
        # Similar to NPC pterodactyls but with unique player features
        self.body = Entity(
            parent=self,
            model='cube',
            color=color.rgb(100, 80, 120),  # Unique purple tint
            scale=(2.5 * self.base_scale, 1.2 * self.base_scale, 1.2 * self.base_scale),
            position=(0, 0, 0)
        )
        
        # Head with smaller crest
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(110, 90, 130),
            scale=(1.2 * self.base_scale, 0.8 * self.base_scale, 1.5 * self.base_scale),
            position=(0, 0.4 * self.base_scale, 1.3 * self.base_scale)
        )
        
        # Player pterodactyl wings
        wing_length = 6 * self.base_scale
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(100, 80, 120, 230),
            scale=(wing_length, 0.12 * self.base_scale, 2.5 * self.base_scale),
            position=(-wing_length/2 - 0.8, 0, 0),
            rotation=(0, 0, 8)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(100, 80, 120, 230),
            scale=(wing_length, 0.12 * self.base_scale, 2.5 * self.base_scale),
            position=(wing_length/2 + 0.8, 0, 0),
            rotation=(0, 0, -8)
        )
    
    def create_epic_effects(self):
        """Create enhanced visual effects for the player"""
        
        # Enhanced particle trail
        self.trail_entities = []
        for i in range(10):
            trail_particle = Entity(
                parent=scene,
                model='cube',
                color=color.rgba(255, 200, 100, 140 - i*14),
                scale=0.4 - i*0.03,
                visible=False
            )
            self.trail_entities.append(trail_particle)
        
        # Thermal vision indicators
        self.thermal_indicators = []
        
        # Energy aura when at high energy
        self.energy_aura = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(100, 200, 255, 50),
            scale=4,
            visible=False
        )
        
        # Speed boost effect
        self.speed_boost_effect = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(255, 150, 50, 80),
            scale=3,
            visible=False
        )
    
    def update(self, nearby_pterodactyls=[]):
        """Update player creature with enhanced interactions"""
        dt = time.dt
        
        # Store nearby pterodactyls for interaction
        self.nearby_pterodactyls = nearby_pterodactyls
        
        # Handle input
        self.handle_enhanced_input()
        
        # Update physics
        physics_data = self.physics.update(dt)
        
        # Update animations and effects
        self.update_epic_animations(physics_data)
        self.update_epic_effects(physics_data)
        
        # Update abilities
        self.update_abilities(dt)
        
        # Pterodactyl interactions
        self.update_pterodactyl_interactions()
        
        # Keep above ground/water
        if self.y < 1:
            self.y = 1
            self.physics.velocity.y = max(0, self.physics.velocity.y)
        
        return physics_data
    
    def handle_enhanced_input(self):
        """Enhanced input handling with special abilities"""
        
        # Basic flight controls
        self.pitch_input = 0
        self.yaw_input = 0
        self.roll_input = 0
        
        if held_keys['w']:
            self.pitch_input = 1
        elif held_keys['s']:
            self.pitch_input = -1
        
        if held_keys['a']:
            self.yaw_input = 1
            self.roll_input = 1
        elif held_keys['d']:
            self.yaw_input = -1
            self.roll_input = -1
        
        # Enhanced abilities
        if held_keys['space']:
            self.pitch_input += 0.6
            self.use_stamina(dt * 0.5)
        
        if held_keys['shift']:
            self.pitch_input -= 1.0
            
        # Special abilities
        if held_keys['f'] and self.has_fire_breath:
            self.breathe_fire()
        
        if held_keys['e']:
            self.thermal_boost()
        
        # Apply enhanced control inputs
        self.physics.apply_control_input(
            self.pitch_input * 1.2,  # Enhanced responsiveness
            self.yaw_input * 1.2,
            self.roll_input
        )
    
    def update_epic_animations(self, physics_data):
        """Enhanced animations for epic gameplay"""
        speed = physics_data['speed']
        
        # Enhanced wing animation
        self.wing_beat_time += time.dt * speed * 1.2
        
        if speed > 5:
            wing_flap = math.sin(self.wing_beat_time) * (18 - speed * 0.4)
            energy_boost = self.energy * 5  # More dramatic when high energy
            
            base_angle = 8
            self.left_wing.rotation_z = base_angle + wing_flap + energy_boost
            self.right_wing.rotation_z = -base_angle - wing_flap - energy_boost
        else:
            # Gliding animation
            glide_adjust = math.sin(time.time() * 0.7) * 4
            self.left_wing.rotation_z = 5 + glide_adjust
            self.right_wing.rotation_z = -5 - glide_adjust
        
        # Body orientation with enhanced responsiveness
        self.rotation_x = math.degrees(math.atan2(-self.physics.velocity.y, 
                                                abs(self.physics.velocity.z) + 0.1))
        self.rotation_y += self.yaw_input * 50 * time.dt
        self.rotation_z = self.roll_input * 35
        
        # Scale effects based on energy and speed
        energy_scale = 1.0 + (self.energy * 0.1)
        speed_scale = 1.0 + (speed * 0.01)
        total_scale = energy_scale * speed_scale
        
        self.body.scale = (2.5 * self.base_scale * total_scale,
                          1.0 * self.base_scale,
                          1.5 * self.base_scale)
    
    def update_epic_effects(self, physics_data):
        """Update enhanced visual effects"""
        speed = physics_data['speed']
        
        # Enhanced particle trail
        if speed > 3:
            for i, particle in enumerate(self.trail_entities):
                particle.visible = True
                trail_pos = self.position - self.forward * (i + 1) * 1.2
                particle.position = trail_pos
                alpha = max(0, 140 - i*14 - int(speed*2))
                particle.color = color.rgba(255, 200, 100, alpha)
        else:
            for particle in self.trail_entities:
                particle.visible = False
        
        # Energy aura when high energy
        if self.energy > 0.8:
            self.energy_aura.visible = True
            pulse = math.sin(time.time() * 4) * 0.3 + 0.7
            self.energy_aura.scale = 4 * pulse
            aura_alpha = int(50 * self.energy * pulse)
            self.energy_aura.color = color.rgba(100, 200, 255, aura_alpha)
        else:
            self.energy_aura.visible = False
        
        # Speed boost effect
        if speed > 25:
            self.speed_boost_effect.visible = True
            boost_alpha = int((speed - 25) * 8)
            self.speed_boost_effect.color = color.rgba(255, 150, 50, min(120, boost_alpha))
        else:
            self.speed_boost_effect.visible = False
    
    def update_abilities(self, dt):
        """Update special abilities"""
        
        # Regenerate energy slowly
        if self.energy < 1.0:
            self.energy = min(1.0, self.energy + 0.1 * dt)
        
        # Regenerate stamina
        if self.stamina < 1.0:
            self.stamina = min(1.0, self.stamina + 0.2 * dt)
    
    def use_stamina(self, amount):
        """Use stamina for special maneuvers"""
        self.stamina = max(0, self.stamina - amount)
    
    def thermal_boost(self):
        """Use thermal vision to find updrafts"""
        if self.energy > 0.2:
            # Temporarily boost lift for thermal riding
            self.physics.velocity.y += 3 * time.dt
            self.energy -= 0.5 * time.dt
    
    def breathe_fire(self):
        """Dragon fire breath ability"""
        if self.has_fire_breath and self.energy > 0.3:
            # Create fire effect
            fire_effect = Entity(
                model='cube',
                color=color.rgba(255, 100, 0, 200),
                scale=(1, 1, 8),
                position=self.position + self.forward * 4,
                rotation=self.rotation,
                parent=scene
            )
            
            # Animate fire
            fire_effect.animate_scale((3, 3, 12), duration=1)
            fire_effect.animate('color', color.rgba(255, 0, 0, 0), duration=1)
            
            destroy(fire_effect, delay=1.1)
            self.energy -= 0.2
    
    def update_pterodactyl_interactions(self):
        """Handle interactions with nearby pterodactyls"""
        
        for pterodactyl in self.nearby_pterodactyls:
            distance_to_ptero = distance(self.position, pterodactyl.position)
            
            # Close encounter
            if distance_to_ptero < 15:
                # Pterodactyl reaction based on species and player behavior
                if hasattr(pterodactyl, 'species_type'):
                    if pterodactyl.species_type == 'dimorphodon':
                        # Pack hunters might attack
                        if self.reputation < -0.3:
                            # They're hostile - boost player speed for escape
                            self.physics.velocity += (self.position - pterodactyl.position).normalized() * 2 * time.dt
                    
                    elif pterodactyl.species_type == 'quetzalcoatlus':
                        # Giants are mostly indifferent but impressive
                        if distance_to_ptero < 8:
                            # Awe effect - slight slowdown from being impressed
                            self.physics.velocity *= 0.98
                    
                    elif pterodactyl.species_type == 'pteranodon':
                        # Curious but cautious
                        if self.reputation > 0.2:
                            # They might follow the player briefly
                            pass
    
    def get_flight_data(self):
        """Get enhanced flight data for UI"""
        return {
            'speed': distance(self.physics.velocity, Vec3(0, 0, 0)),
            'altitude': self.position.y,
            'heading': self.rotation_y,
            'pitch': self.rotation_x,
            'roll': self.rotation_z,
            'velocity': self.physics.velocity,
            'g_force': getattr(self.physics, 'g_force', 1.0),
            'energy': self.energy,
            'stamina': self.stamina,
            'reputation': self.reputation,
            'creature_type': self.creature_type
        } 