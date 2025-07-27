"""
Pterodactyl Ecosystem - Epic Flying Reptile AI System
Multiple pterodactyl species with advanced flight patterns, flocking behavior, and player interaction.
DESIGNED BY SENIOR DEVELOPERS FOR MAXIMUM EPIC FACTOR.
"""

from ursina import *
import math
import random
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from physics.flight_physics import FlightPhysics

class PterodactylPhysics:
    """Advanced aerodynamics for large prehistoric flying reptiles"""
    
    def __init__(self, pterodactyl, species_config):
        self.pterodactyl = pterodactyl
        self.config = species_config
        
        # Physics properties
        self.velocity = Vec3(0, 0, 0)
        self.mass = species_config['mass']
        self.wing_span = species_config['wing_span']
        self.wing_area = species_config['wing_area']
        
        # Flight characteristics
        self.lift_coefficient = species_config['lift_coefficient']
        self.drag_coefficient = species_config['drag_coefficient'] 
        self.max_speed = species_config['max_speed']
        self.cruise_speed = species_config['cruise_speed']
        self.stall_speed = species_config['stall_speed']
        
        # AI flight state
        self.target_position = Vec3(0, 0, 0)
        self.flight_mode = 'cruise'  # cruise, hunt, flee, thermal, patrol
        self.energy = 1.0  # 0-1, affects flight performance
        
    def update_ai_flight(self, dt, nearby_pterodactyls, player_position):
        """Advanced AI flight behavior"""
        
        # Choose flight behavior based on conditions
        self.choose_flight_behavior(nearby_pterodactyls, player_position)
        
        # Apply flocking forces
        flocking_force = self.calculate_flocking_forces(nearby_pterodactyls)
        
        # Environmental forces
        wind_force = self.get_wind_force()
        thermal_force = self.seek_thermals()
        
        # Navigation forces
        nav_force = self.navigate_to_target()
        
        # Combine all forces
        total_force = flocking_force + wind_force + thermal_force + nav_force
        
        # Apply physics
        acceleration = total_force / self.mass
        self.velocity += acceleration * dt
        
        # Speed limits
        speed = distance(self.velocity, Vec3(0, 0, 0))
        if speed > self.max_speed:
            self.velocity = self.velocity.normalized() * self.max_speed
        elif speed < self.stall_speed:
            # Emergency flap to avoid stall
            self.velocity += Vec3(0, 2, 0) * dt
        
        # Update position
        self.pterodactyl.position += self.velocity * dt
        
        # Update energy
        self.update_energy(dt, speed)
        
        return speed, self.flight_mode
    
    def choose_flight_behavior(self, nearby_pterodactyls, player_position):
        """AI decision making for flight behavior"""
        player_distance = distance(self.pterodactyl.position, player_position)
        
        # Player interaction
        if player_distance < 20:
            if self.config['aggression'] > 0.7:
                self.flight_mode = 'hunt'
                self.target_position = player_position
            else:
                self.flight_mode = 'flee'
                flee_direction = (self.pterodactyl.position - player_position).normalized()
                self.target_position = self.pterodactyl.position + flee_direction * 50
        
        # Low energy - seek thermals
        elif self.energy < 0.3:
            self.flight_mode = 'thermal'
            self.find_nearest_thermal()
        
        # Normal patrol behavior
        else:
            self.flight_mode = 'patrol'
            if distance(self.pterodactyl.position, self.target_position) < 10:
                self.set_new_patrol_target()
    
    def calculate_flocking_forces(self, nearby_pterodactyls):
        """Boids-style flocking behavior"""
        if not nearby_pterodactyls:
            return Vec3(0, 0, 0)
        
        # Separation - avoid crowding neighbors
        separation = Vec3(0, 0, 0)
        # Alignment - steer towards average heading of neighbors  
        alignment = Vec3(0, 0, 0)
        # Cohesion - steer towards average position of neighbors
        cohesion = Vec3(0, 0, 0)
        
        neighbor_count = 0
        for other in nearby_pterodactyls:
            if other == self.pterodactyl:
                continue
                
            dist = distance(self.pterodactyl.position, other.position)
            if dist < self.config['flocking_radius']:
                neighbor_count += 1
                
                # Separation
                if dist < self.config['separation_radius']:
                    diff = self.pterodactyl.position - other.position
                    diff = diff.normalized() / max(dist, 0.1)  # Closer = stronger force
                    separation += diff
                
                # Alignment
                if hasattr(other, 'physics'):
                    alignment += other.physics.velocity
                
                # Cohesion
                cohesion += other.position
        
        if neighbor_count > 0:
            # Finalize forces
            separation = separation.normalized() * self.config['separation_strength']
            
            alignment = alignment / neighbor_count
            alignment = alignment.normalized() * self.config['alignment_strength']
            
            cohesion = cohesion / neighbor_count
            cohesion = (cohesion - self.pterodactyl.position).normalized() * self.config['cohesion_strength']
        
        return separation + alignment + cohesion
    
    def seek_thermals(self):
        """AI thermal seeking behavior"""
        # Simplified thermal detection - pterodactyls are experts at this
        best_thermal_force = Vec3(0, 0, 0)
        
        # Sample nearby positions for thermal activity
        for angle in range(0, 360, 30):
            for dist in [10, 20, 30]:
                sample_x = self.pterodactyl.x + math.cos(math.radians(angle)) * dist
                sample_z = self.pterodactyl.z + math.sin(math.radians(angle)) * dist
                
                # Simulate thermal detection (in real game, would use actual thermal system)
                thermal_strength = math.sin(sample_x * 0.05) * math.cos(sample_z * 0.05) + random.uniform(-0.5, 0.5)
                
                if thermal_strength > 0.3:
                    direction = Vec3(sample_x - self.pterodactyl.x, 5, sample_z - self.pterodactyl.z)
                    thermal_force = direction.normalized() * thermal_strength * 2
                    
                    if distance(thermal_force, Vec3(0, 0, 0)) > distance(best_thermal_force, Vec3(0, 0, 0)):
                        best_thermal_force = thermal_force
        
        return best_thermal_force
    
    def navigate_to_target(self):
        """Navigate towards current target"""
        if not self.target_position:
            return Vec3(0, 0, 0)
        
        direction = self.target_position - self.pterodactyl.position
        distance_to_target = distance(direction, Vec3(0, 0, 0))
        
        if distance_to_target < 1:
            return Vec3(0, 0, 0)
        
        # Normalized steering force
        steering_force = direction.normalized() * self.config['steering_strength']
        
        # Reduce force as we get closer
        if distance_to_target < 20:
            steering_force *= (distance_to_target / 20)
        
        return steering_force
    
    def find_nearest_thermal(self):
        """Find the nearest thermal for energy recovery"""
        # In a full implementation, this would search actual thermal map
        # For now, generate a nearby thermal location
        angle = random.uniform(0, 360)
        distance = random.uniform(30, 80)
        
        self.target_position = self.pterodactyl.position + Vec3(
            math.cos(math.radians(angle)) * distance,
            random.uniform(10, 30),
            math.sin(math.radians(angle)) * distance
        )
    
    def set_new_patrol_target(self):
        """Set a new random patrol target"""
        # Patrol around San Francisco landmarks
        patrol_areas = [
            Vec3(-80, 50, 120),  # Golden Gate Bridge
            Vec3(-20, 30, 100),  # Alcatraz
            Vec3(-45, 70, 45),   # Downtown
            Vec3(0, 80, 0),      # Twin Peaks
            Vec3(-60, 90, 60),   # Telegraph Hill
        ]
        
        base_target = random.choice(patrol_areas)
        offset = Vec3(
            random.uniform(-30, 30),
            random.uniform(-20, 20), 
            random.uniform(-30, 30)
        )
        
        self.target_position = base_target + offset
    
    def get_wind_force(self):
        """Environmental wind effects"""
        # San Francisco wind patterns
        wind = Vec3(
            math.sin(time.time() * 0.1) * 1.5,  # Variable wind
            0,
            math.cos(time.time() * 0.08) * 1.0
        )
        
        # Wind affects larger pterodactyls more
        wind_effect = wind * (self.wing_span / 15)
        return wind_effect
    
    def update_energy(self, dt, speed):
        """Update pterodactyl energy levels"""
        # Lose energy from flying
        energy_cost = (speed / self.max_speed) * 0.1 * dt
        
        # Gain energy from thermals and gliding
        if self.flight_mode == 'thermal':
            self.energy = min(1.0, self.energy + 0.2 * dt)
        elif speed < self.cruise_speed:
            self.energy = min(1.0, self.energy + 0.05 * dt)
        else:
            self.energy = max(0.0, self.energy - energy_cost)

class Pterodactyl(Entity):
    """Individual pterodactyl with species-specific characteristics"""
    
    def __init__(self, species_type, position=Vec3(0, 50, 0)):
        super().__init__()
        
        self.species_type = species_type
        self.species_config = self.get_species_config(species_type)
        self.position = position
        
        # Create model
        self.create_pterodactyl_model()
        
        # Initialize physics
        self.physics = PterodactylPhysics(self, self.species_config)
        
        # Animation state
        self.wing_beat_time = 0
        self.call_timer = random.uniform(0, 10)  # Random call timing
        
        # Behavior state
        self.last_call_time = 0
        self.territorial_center = position.copy()
    
    def get_species_config(self, species_type):
        """Get configuration for different pterodactyl species"""
        species_configs = {
            'pteranodon': {
                'mass': 25,  # kg
                'wing_span': 9,  # meters
                'wing_area': 12,
                'max_speed': 30,
                'cruise_speed': 15,
                'stall_speed': 8,
                'lift_coefficient': 1.2,
                'drag_coefficient': 0.02,
                'aggression': 0.3,
                'flocking_radius': 40,
                'separation_radius': 15,
                'separation_strength': 2.0,
                'alignment_strength': 1.0,
                'cohesion_strength': 0.8,
                'steering_strength': 1.5,
                'scale_factor': 1.0,
                'color': color.rgb(120, 80, 60),
            },
            'quetzalcoatlus': {
                'mass': 70,  # Massive flying reptile
                'wing_span': 15,
                'wing_area': 25,
                'max_speed': 25,
                'cruise_speed': 12,
                'stall_speed': 6,
                'lift_coefficient': 1.5,
                'drag_coefficient': 0.015,
                'aggression': 0.8,  # More aggressive
                'flocking_radius': 60,
                'separation_radius': 25,
                'separation_strength': 3.0,
                'alignment_strength': 0.8,
                'cohesion_strength': 0.5,
                'steering_strength': 1.0,
                'scale_factor': 1.8,
                'color': color.rgb(80, 60, 40),
            },
            'dimorphodon': {
                'mass': 12,  # Smaller, more agile
                'wing_span': 4,
                'wing_area': 6,
                'max_speed': 40,
                'cruise_speed': 20,
                'stall_speed': 10,
                'lift_coefficient': 1.0,
                'drag_coefficient': 0.025,
                'aggression': 0.9,  # Very aggressive, pack hunters
                'flocking_radius': 25,
                'separation_radius': 8,
                'separation_strength': 1.5,
                'alignment_strength': 1.5,
                'cohesion_strength': 1.2,
                'steering_strength': 2.0,
                'scale_factor': 0.6,
                'color': color.rgb(100, 90, 70),
            }
        }
        
        return species_configs.get(species_type, species_configs['pteranodon'])
    
    def create_pterodactyl_model(self):
        """Create detailed 3D pterodactyl model"""
        scale_factor = self.species_config['scale_factor']
        base_color = self.species_config['color']
        
        # Main body
        self.body = Entity(
            parent=self,
            model='cube',
            color=base_color,
            scale=(3 * scale_factor, 1.5 * scale_factor, 1 * scale_factor),
            position=(0, 0, 0)
        )
        
        # Head with long crest
        self.head = Entity(
            parent=self,
            model='cube',
            color=color.rgb(base_color.r + 20, base_color.g + 10, base_color.b + 10),
            scale=(1.5 * scale_factor, 1 * scale_factor, 2 * scale_factor),
            position=(0, 0.5 * scale_factor, 2 * scale_factor)
        )
        
        # Characteristic pterodactyl crest
        self.crest = Entity(
            parent=self.head,
            model='cube',
            color=color.rgb(base_color.r + 30, base_color.g + 20, base_color.b + 15),
            scale=(0.5, 2 * scale_factor, 1),
            position=(0, 1 * scale_factor, 0.5)
        )
        
        # Long beak
        self.beak = Entity(
            parent=self.head,
            model='cube',
            color=color.rgb(50, 50, 40),
            scale=(0.3, 0.3, 1.5 * scale_factor),
            position=(0, 0, 1.5 * scale_factor)
        )
        
        # Eyes
        for eye_x in [-0.4, 0.4]:
            eye = Entity(
                parent=self.head,
                model='sphere',
                color=color.yellow,
                scale=0.3 * scale_factor,
                position=(eye_x * scale_factor, 0.2, 0.5)
            )
        
        # Massive wings
        wing_length = self.species_config['wing_span'] / 2
        
        self.left_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(base_color.r, base_color.g, base_color.b, 220),
            scale=(wing_length, 0.2 * scale_factor, 2 * scale_factor),
            position=(-wing_length/2 - 1, 0, 0),
            rotation=(0, 0, 10)
        )
        
        self.right_wing = Entity(
            parent=self,
            model='cube',
            color=color.rgba(base_color.r, base_color.g, base_color.b, 220),
            scale=(wing_length, 0.2 * scale_factor, 2 * scale_factor),
            position=(wing_length/2 + 1, 0, 0),
            rotation=(0, 0, -10)
        )
        
        # Wing membranes with finger supports
        for wing, wing_side in [(self.left_wing, -1), (self.right_wing, 1)]:
            # Wing fingers (pterodactyl wing structure)
            for finger in range(3):
                finger_entity = Entity(
                    parent=wing,
                    model='cube',
                    color=color.rgb(40, 30, 20),
                    scale=(0.1, 0.1, wing_length * 0.8),
                    position=(wing_side * finger * 0.3, 0, finger * 0.2)
                )
        
        # Long neck
        self.neck = Entity(
            parent=self,
            model='cube',
            color=base_color,
            scale=(0.8 * scale_factor, 0.8 * scale_factor, 1.5 * scale_factor),
            position=(0, 0.3 * scale_factor, 1 * scale_factor)
        )
        
        # Tail
        self.tail = Entity(
            parent=self,
            model='cube',
            color=base_color,
            scale=(0.5 * scale_factor, 0.5 * scale_factor, 2 * scale_factor),
            position=(0, 0, -2.5 * scale_factor)
        )
        
        # Legs (for perching)
        for leg_x in [-0.8, 0.8]:
            leg = Entity(
                parent=self,
                model='cube',
                color=color.rgb(40, 30, 20),
                scale=(0.3 * scale_factor, 1.5 * scale_factor, 0.3 * scale_factor),
                position=(leg_x * scale_factor, -1 * scale_factor, 0)
            )
    
    def update(self, nearby_pterodactyls, player_position):
        """Update pterodactyl behavior and animation"""
        dt = time.dt
        
        # Update AI physics
        speed, flight_mode = self.physics.update_ai_flight(dt, nearby_pterodactyls, player_position)
        
        # Update animations
        self.update_animations(speed, flight_mode)
        
        # Pterodactyl calls
        self.update_vocalizations(dt)
        
        # Orient towards movement direction
        if distance(self.physics.velocity, Vec3(0, 0, 0)) > 1:
            forward = self.physics.velocity.normalized()
            self.look_at(self.position + forward, up=Vec3(0, 1, 0))
        
        return flight_mode
    
    def update_animations(self, speed, flight_mode):
        """Update pterodactyl wing animations and body language"""
        
        # Wing beat frequency based on species and speed
        base_frequency = 2.0 / self.species_config['wing_span']  # Larger wings beat slower
        speed_factor = max(0.5, speed / self.species_config['cruise_speed'])
        
        self.wing_beat_time += time.dt * base_frequency * speed_factor
        
        # Wing flapping animation
        if speed > self.species_config['stall_speed']:
            # Active flapping
            wing_flap = math.sin(self.wing_beat_time) * 25
            
            # Different modes have different wing positions
            if flight_mode == 'thermal':
                # Extended wings for soaring
                base_angle = 5
                wing_flap *= 0.3  # Less flapping in thermals
            elif flight_mode == 'hunt':
                # Aggressive wing position
                base_angle = 15
                wing_flap *= 1.2
            else:
                # Normal cruise
                base_angle = 10
            
            self.left_wing.rotation_z = base_angle + wing_flap
            self.right_wing.rotation_z = -base_angle - wing_flap
        else:
            # Gliding - minimal wing movement
            glide_adjust = math.sin(time.time() * 0.5) * 3
            self.left_wing.rotation_z = 5 + glide_adjust
            self.right_wing.rotation_z = -5 - glide_adjust
        
        # Head movement based on behavior
        if flight_mode == 'hunt':
            # Look towards target aggressively
            head_bob = math.sin(time.time() * 3) * 5
            self.head.rotation_x = -10 + head_bob
        elif flight_mode == 'flee':
            # Look around nervously
            head_scan = math.sin(time.time() * 4) * 15
            self.head.rotation_y = head_scan
        else:
            # Normal head position
            self.head.rotation_x = lerp(self.head.rotation_x, 0, 2 * time.dt)
            self.head.rotation_y = lerp(self.head.rotation_y, 0, 2 * time.dt)
    
    def update_vocalizations(self, dt):
        """Handle pterodactyl calls and sounds"""
        self.call_timer -= dt
        
        if self.call_timer <= 0:
            # Emit a pterodactyl call (visual indicator for now)
            self.emit_call()
            self.call_timer = random.uniform(8, 20)  # Next call in 8-20 seconds
    
    def emit_call(self):
        """Visual representation of pterodactyl call"""
        # Create a visual sound wave effect
        call_effect = Entity(
            model='sphere',
            color=color.rgba(255, 255, 0, 100),
            scale=1,
            position=self.position,
            parent=scene
        )
        
        # Animate the call effect
        call_effect.animate_scale(5, duration=2)
        call_effect.animate('color', color.rgba(255, 255, 0, 0), duration=2)
        
        # Clean up after animation
        destroy(call_effect, delay=2.1)

class PterodactylFlock:
    """Manages groups of pterodactyls with collective behavior"""
    
    def __init__(self, species_type, flock_size, center_position):
        self.species_type = species_type
        self.pterodactyls = []
        self.center_position = center_position
        self.flock_behavior = 'patrol'  # patrol, hunting, fleeing, feeding
        
        # Create flock members
        for i in range(flock_size):
            offset = Vec3(
                random.uniform(-20, 20),
                random.uniform(-10, 10),
                random.uniform(-20, 20)
            )
            
            pterodactyl = Pterodactyl(species_type, center_position + offset)
            self.pterodactyls.append(pterodactyl)
    
    def update(self, player_position, other_flocks=[]):
        """Update entire flock behavior"""
        
        # Update each pterodactyl
        for pterodactyl in self.pterodactyls:
            nearby_pterodactyls = self.get_nearby_pterodactyls(pterodactyl, 50)
            flight_mode = pterodactyl.update(nearby_pterodactyls, player_position)
        
        # Update flock-level behavior
        self.update_flock_behavior(player_position)
    
    def get_nearby_pterodactyls(self, target_pterodactyl, radius):
        """Get pterodactyls within radius of target"""
        nearby = []
        
        for pterodactyl in self.pterodactyls:
            if pterodactyl != target_pterodactyl:
                dist = distance(target_pterodactyl.position, pterodactyl.position)
                if dist < radius:
                    nearby.append(pterodactyl)
        
        return nearby
    
    def update_flock_behavior(self, player_position):
        """Coordinate flock-level decisions"""
        flock_center = self.get_flock_center()
        player_distance = distance(flock_center, player_position)
        
        # Collective decision making
        if player_distance < 30:
            if self.species_type == 'dimorphodon':
                self.flock_behavior = 'hunting'  # Pack hunters
            else:
                self.flock_behavior = 'fleeing'
        else:
            self.flock_behavior = 'patrol'
    
    def get_flock_center(self):
        """Calculate the center position of the flock"""
        if not self.pterodactyls:
            return self.center_position
        
        total_pos = Vec3(0, 0, 0)
        for pterodactyl in self.pterodactyls:
            total_pos += pterodactyl.position
        
        return total_pos / len(self.pterodactyls)

class PterodactylEcosystem:
    """Manages the entire pterodactyl ecosystem in San Francisco"""
    
    def __init__(self):
        self.flocks = []
        self.create_ecosystem()
    
    def create_ecosystem(self):
        """Create multiple flocks around San Francisco"""
        
        # Pteranodon flock around Golden Gate Bridge
        golden_gate_flock = PterodactylFlock(
            'pteranodon', 
            flock_size=6, 
            center_position=Vec3(-80, 80, 120)
        )
        self.flocks.append(golden_gate_flock)
        
        # Quetzalcoatlus pair (solitary giants) over Twin Peaks
        giant_flock = PterodactylFlock(
            'quetzalcoatlus',
            flock_size=2,
            center_position=Vec3(0, 120, 0)
        )
        self.flocks.append(giant_flock)
        
        # Dimorphodon pack hunters around Alcatraz
        hunter_flock = PterodactylFlock(
            'dimorphodon',
            flock_size=8,
            center_position=Vec3(-20, 60, 100)
        )
        self.flocks.append(hunter_flock)
        
        # Mixed flock over downtown SF
        downtown_flock = PterodactylFlock(
            'pteranodon',
            flock_size=4,
            center_position=Vec3(-45, 90, 45)
        )
        self.flocks.append(downtown_flock)
        
        print(f"Pterodactyl ecosystem created with {len(self.flocks)} flocks")
        print(f"Total pterodactyls: {sum(len(flock.pterodactyls) for flock in self.flocks)}")
    
    def update(self, player_position):
        """Update the entire ecosystem"""
        for flock in self.flocks:
            flock.update(player_position, self.flocks)
    
    def get_all_pterodactyls(self):
        """Get list of all pterodactyls in the ecosystem"""
        all_pterodactyls = []
        for flock in self.flocks:
            all_pterodactyls.extend(flock.pterodactyls)
        return all_pterodactyls 