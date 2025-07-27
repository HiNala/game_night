"""
🏁 EPIC RACING & COLLECTION SYSTEM 🏁
Advanced point-to-point gameplay with rings, targets, waypoints, and challenges.
"""

import math
import random
from ursina import *

class NavigationRing(Entity):
    """Flying ring that players must pass through"""
    
    def __init__(self, position, ring_type='checkpoint', size=8):
        super().__init__()
        self.position = position
        self.ring_type = ring_type
        self.size = size
        self.passed = False
        
        # Ring properties
        if ring_type == 'checkpoint':
            self.color_primary = color.rgb(0, 255, 100)
            self.color_secondary = color.rgb(0, 150, 60)
            self.points = 100
        elif ring_type == 'speed_ring':
            self.color_primary = color.rgb(255, 100, 0)
            self.color_secondary = color.rgb(150, 60, 0)
            self.points = 200
            self.speed_bonus = True
        elif ring_type == 'precision_ring':
            self.color_primary = color.rgb(100, 100, 255)
            self.color_secondary = color.rgb(60, 60, 150)
            self.points = 300
            self.size = size * 0.7  # Smaller for precision
        else:  # bonus_ring
            self.color_primary = color.rgb(255, 255, 0)
            self.color_secondary = color.rgb(200, 200, 0)
            self.points = 500
        
        # Visual components
        self.create_ring_visual()
        
        # Detection zone
        self.detection_radius = self.size * 0.8
        
        # Animation state
        self.rotation_speed = 30
        self.pulse_time = 0
        self.glow_intensity = 1.0
        
        print(f"🎯 Navigation ring created: {ring_type} at {position}")
    
    def create_ring_visual(self):
        """Create epic ring visual"""
        # Outer ring
        self.outer_ring = Entity(
            parent=self,
            model='cube',
            color=self.color_primary,
            scale=(self.size, 0.5, self.size),
            position=(0, 0, 0)
        )
        
        # Inner ring (hollow effect)
        self.inner_ring = Entity(
            parent=self,
            model='cube',
            color=color.rgba(0, 0, 0, 0),  # Transparent
            scale=(self.size * 0.6, 0.6, self.size * 0.6),
            position=(0, 0, 0)
        )
        
        # Ring segments for detail
        num_segments = 12
        for i in range(num_segments):
            angle = (i / num_segments) * 360
            segment_x = math.cos(math.radians(angle)) * self.size * 0.5
            segment_z = math.sin(math.radians(angle)) * self.size * 0.5
            
            segment = Entity(
                parent=self,
                model='cube',
                color=self.color_secondary,
                scale=(0.8, 0.3, 0.8),
                position=(segment_x, 0, segment_z),
                rotation=(0, angle, 0)
            )
        
        # Center indicator
        self.center_indicator = Entity(
            parent=self,
            model='sphere',
            color=self.color_primary,
            scale=1.5,
            position=(0, 0, 0)
        )
        
        # Glow effect
        self.glow_effect = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 50),
            scale=self.size * 1.5,
            position=(0, 0, 0)
        )
        
        # Direction indicators (arrows)
        if hasattr(self, 'next_ring_direction'):
            self.create_direction_arrows()
    
    def create_direction_arrows(self):
        """Create arrows pointing to next ring"""
        for i in range(4):
            angle = i * 90
            arrow_x = math.cos(math.radians(angle)) * self.size * 0.8
            arrow_z = math.sin(math.radians(angle)) * self.size * 0.8
            
            arrow = Entity(
                parent=self,
                model='cube',
                color=color.rgba(255, 255, 255, 100),
                scale=(0.5, 0.2, 1.5),
                position=(arrow_x, 2, arrow_z),
                rotation=(0, angle, 0)
            )
    
    def check_passage(self, position, velocity):
        """Check if entity passed through ring"""
        if self.passed:
            return False
        
        # Distance check
        distance_to_ring = distance(position, self.position)
        
        if distance_to_ring < self.detection_radius:
            # Check if actually passed through (not just near)
            ring_plane_distance = abs((position - self.position).dot(self.up))
            
            if ring_plane_distance < 2.0:  # Within ring thickness
                self.passed = True
                self.trigger_passage_effect()
                return True
        
        return False
    
    def trigger_passage_effect(self):
        """Create epic passage effect"""
        # Ring flash
        self.outer_ring.color = color.white
        self.outer_ring.animate('color', self.color_primary, duration=0.5)
        
        # Expanding energy wave
        energy_wave = Entity(
            model='sphere',
            color=color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 100),
            scale=1,
            position=self.position,
            parent=scene
        )
        
        energy_wave.animate_scale(self.size * 3, duration=1.0)
        energy_wave.animate('color', color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 0), duration=1.0)
        destroy(energy_wave, delay=1.1)
        
        # Particle burst
        self.create_particle_burst()
        
        print(f"✨ Ring passed! Type: {self.ring_type}, Points: {self.points}")
    
    def create_particle_burst(self):
        """Create particle burst effect"""
        for _ in range(15):
            particle = Entity(
                model='sphere',
                color=self.color_primary,
                scale=0.3,
                position=self.position,
                parent=scene
            )
            
            # Random direction
            direction = Vec3(
                random.uniform(-1, 1),
                random.uniform(-0.5, 1),
                random.uniform(-1, 1)
            ).normalized()
            
            final_position = self.position + direction * random.uniform(5, 15)
            
            particle.animate_position(final_position, duration=2.0)
            particle.animate_scale(0, duration=2.0)
            particle.animate('color', color.rgba(self.color_primary.r, self.color_primary.g, self.color_primary.b, 0), duration=2.0)
            
            destroy(particle, delay=2.1)
    
    def update(self, dt):
        """Update ring animations"""
        if self.passed:
            return
        
        # Rotation animation
        self.rotation_y += self.rotation_speed * dt
        
        # Pulsing glow effect
        self.pulse_time += dt * 3
        pulse_factor = math.sin(self.pulse_time) * 0.3 + 0.7
        
        glow_alpha = int(50 * pulse_factor * self.glow_intensity)
        self.glow_effect.color = color.rgba(
            self.color_primary.r, 
            self.color_primary.g, 
            self.color_primary.b, 
            glow_alpha
        )
        
        # Center indicator pulse
        self.center_indicator.scale = 1.5 * pulse_factor

class CollectionTarget(Entity):
    """Targets that must be collected in sequence"""
    
    def __init__(self, position, target_type='orb', value=50):
        super().__init__()
        self.position = position
        self.target_type = target_type
        self.value = value
        self.collected = False
        
        # Target properties
        if target_type == 'orb':
            self.model_type = 'sphere'
            self.base_color = color.rgb(100, 200, 255)
            self.collection_radius = 3
        elif target_type == 'crystal':
            self.model_type = 'cube'
            self.base_color = color.rgb(255, 100, 200)
            self.collection_radius = 3.5
        elif target_type == 'energy_cell':
            self.model_type = 'sphere'
            self.base_color = color.rgb(255, 255, 100)
            self.collection_radius = 2.5
        else:  # artifact
            self.model_type = 'cube'
            self.base_color = color.rgb(200, 100, 255)
            self.collection_radius = 4
        
        # Visual components
        self.create_target_visual()
        
        # Animation properties
        self.float_time = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(60, 120)
        self.float_amplitude = random.uniform(1, 3)
        
        print(f"💎 Collection target created: {target_type} worth {value} points")
    
    def create_target_visual(self):
        """Create target visual"""
        # Main target
        self.target_body = Entity(
            parent=self,
            model=self.model_type,
            color=self.base_color,
            scale=2,
            position=(0, 0, 0)
        )
        
        # Energy aura
        self.energy_aura = Entity(
            parent=self,
            model='sphere',
            color=color.rgba(self.base_color.r, self.base_color.g, self.base_color.b, 80),
            scale=4,
            position=(0, 0, 0)
        )
        
        # Collection indicator
        self.collection_indicator = Entity(
            parent=self,
            model='cube',
            color=color.rgba(255, 255, 255, 100),
            scale=(8, 0.2, 8),
            position=(0, -3, 0)
        )
        
        # Beacon light
        self.beacon = Entity(
            parent=self,
            model='cube',
            color=color.rgba(self.base_color.r, self.base_color.g, self.base_color.b, 150),
            scale=(0.3, 10, 0.3),
            position=(0, 5, 0)
        )
    
    def check_collection(self, position):
        """Check if target should be collected"""
        if self.collected:
            return False
        
        distance_to_target = distance(position, self.position)
        
        if distance_to_target < self.collection_radius:
            self.collected = True
            self.trigger_collection_effect()
            return True
        
        return False
    
    def trigger_collection_effect(self):
        """Create collection effect"""
        # Target disappears with effect
        self.target_body.animate_scale(6, duration=0.3)
        self.target_body.animate('color', color.white, duration=0.3)
        
        # Energy implosion
        implosion = Entity(
            model='sphere',
            color=color.rgba(255, 255, 255, 200),
            scale=8,
            position=self.position,
            parent=scene
        )
        
        implosion.animate_scale(0.5, duration=0.5)
        implosion.animate('color', self.base_color, duration=0.5)
        destroy(implosion, delay=0.6)
        
        # Hide original
        self.visible = False
        
        print(f"💎 Target collected! Type: {self.target_type}, Value: {self.value}")
    
    def update(self, dt):
        """Update target animations"""
        if self.collected:
            return
        
        # Floating motion
        self.float_time += dt * 2
        float_offset = math.sin(self.float_time) * self.float_amplitude
        self.y += float_offset * dt
        
        # Rotation
        self.target_body.rotation_y += self.rotation_speed * dt
        
        # Pulsing aura
        pulse = math.sin(time.time() * 4) * 0.3 + 0.7
        aura_alpha = int(80 * pulse)
        self.energy_aura.color = color.rgba(
            self.base_color.r, 
            self.base_color.g, 
            self.base_color.b, 
            aura_alpha
        )
        
        # Beacon rotation
        self.beacon.rotation_y += 180 * dt

class RaceCourse:
    """Complete race course with multiple rings and targets"""
    
    def __init__(self, course_name, difficulty='normal'):
        self.course_name = course_name
        self.difficulty = difficulty
        self.rings = []
        self.targets = []
        self.waypoints = []
        
        # Course state
        self.current_ring_index = 0
        self.rings_completed = 0
        self.targets_collected = 0
        self.course_active = False
        self.start_time = 0
        self.best_time = None
        
        # Scoring
        self.total_score = 0
        self.time_bonus_remaining = 300  # 5 minutes for time bonus
        
        self.generate_course()
        print(f"🏁 Race course '{course_name}' created with {len(self.rings)} rings and {len(self.targets)} targets")
    
    def generate_course(self):
        """Generate race course layout"""
        if self.course_name == 'Golden Gate Circuit':
            self.create_golden_gate_circuit()
        elif self.course_name == 'Twin Peaks Challenge':
            self.create_twin_peaks_challenge()
        elif self.course_name == 'Alcatraz Run':
            self.create_alcatraz_run()
        elif self.course_name == 'Bay Tour':
            self.create_bay_tour()
        else:
            self.create_custom_course()
    
    def create_golden_gate_circuit(self):
        """Create circuit around Golden Gate Bridge"""
        # Start near Marin side
        self.rings.append(NavigationRing(Vec3(-120, 40, 120), 'checkpoint', 10))
        
        # Through the bridge
        self.rings.append(NavigationRing(Vec3(-80, 35, 120), 'speed_ring', 8))
        
        # Around south tower
        self.rings.append(NavigationRing(Vec3(-50, 50, 120), 'checkpoint', 10))
        
        # High approach to SF side
        self.rings.append(NavigationRing(Vec3(-40, 70, 100), 'precision_ring', 6))
        
        # Back through bridge (opposite direction)
        self.rings.append(NavigationRing(Vec3(-80, 45, 120), 'speed_ring', 8))
        
        # Finish at start
        self.rings.append(NavigationRing(Vec3(-120, 40, 120), 'bonus_ring', 12))
        
        # Add collection targets
        self.targets.append(CollectionTarget(Vec3(-100, 60, 130), 'orb', 100))
        self.targets.append(CollectionTarget(Vec3(-60, 80, 110), 'crystal', 150))
        self.targets.append(CollectionTarget(Vec3(-90, 55, 140), 'energy_cell', 120))
    
    def create_twin_peaks_challenge(self):
        """Create challenging course over Twin Peaks"""
        # Start low
        self.rings.append(NavigationRing(Vec3(-20, 30, -20), 'checkpoint', 12))
        
        # Up to first peak
        self.rings.append(NavigationRing(Vec3(-10, 150, -10), 'precision_ring', 6))
        
        # Between peaks
        self.rings.append(NavigationRing(Vec3(0, 280, 0), 'speed_ring', 8))
        
        # Down to second peak
        self.rings.append(NavigationRing(Vec3(10, 150, 10), 'precision_ring', 6))
        
        # Valley slalom
        self.rings.append(NavigationRing(Vec3(20, 80, 20), 'checkpoint', 10))
        self.rings.append(NavigationRing(Vec3(30, 60, 10), 'checkpoint', 10))
        self.rings.append(NavigationRing(Vec3(40, 80, 20), 'bonus_ring', 12))
        
        # High-altitude targets
        self.targets.append(CollectionTarget(Vec3(0, 300, 0), 'artifact', 300))
        self.targets.append(CollectionTarget(Vec3(-15, 180, 5), 'crystal', 200))
        self.targets.append(CollectionTarget(Vec3(15, 180, -5), 'crystal', 200))
    
    def create_alcatraz_run(self):
        """Create course around Alcatraz Island"""
        # Start at mainland
        self.rings.append(NavigationRing(Vec3(-60, 25, 80), 'checkpoint', 10))
        
        # Approach Alcatraz
        self.rings.append(NavigationRing(Vec3(-30, 35, 90), 'speed_ring', 9))
        
        # Around the island
        self.rings.append(NavigationRing(Vec3(-10, 20, 100), 'checkpoint', 8))
        self.rings.append(NavigationRing(Vec3(-20, 25, 110), 'precision_ring', 6))
        self.rings.append(NavigationRing(Vec3(-30, 30, 100), 'checkpoint', 8))
        
        # Back to mainland
        self.rings.append(NavigationRing(Vec3(-60, 40, 80), 'bonus_ring', 12))
        
        # Water-level targets (challenging)
        self.targets.append(CollectionTarget(Vec3(-20, 8, 100), 'orb', 250))  # Low over water
        self.targets.append(CollectionTarget(Vec3(-15, 15, 105), 'energy_cell', 180))
    
    def create_bay_tour(self):
        """Create scenic tour of entire bay"""
        waypoints = [
            Vec3(-100, 60, 80),   # Golden Gate approach
            Vec3(-60, 45, 60),    # Crissy Field
            Vec3(-45, 70, 45),    # Downtown
            Vec3(-20, 40, 100),   # Alcatraz
            Vec3(20, 80, 60),     # Bay Bridge area
            Vec3(0, 120, 0),      # Twin Peaks
            Vec3(-80, 80, 120),   # Back to Golden Gate
        ]
        
        for i, waypoint in enumerate(waypoints):
            ring_type = 'bonus_ring' if i == len(waypoints) - 1 else 'checkpoint'
            ring_size = 12 if ring_type == 'bonus_ring' else 10
            self.rings.append(NavigationRing(waypoint, ring_type, ring_size))
        
        # Scenic targets
        self.targets.append(CollectionTarget(Vec3(-80, 100, 120), 'artifact', 500))
        self.targets.append(CollectionTarget(Vec3(0, 150, 0), 'artifact', 500))
        self.targets.append(CollectionTarget(Vec3(-20, 60, 100), 'crystal', 300))
    
    def start_course(self):
        """Start the race course"""
        self.course_active = True
        self.start_time = time.time()
        self.current_ring_index = 0
        self.rings_completed = 0
        self.targets_collected = 0
        self.total_score = 0
        
        # Reset all rings and targets
        for ring in self.rings:
            ring.passed = False
        
        for target in self.targets:
            target.collected = False
            target.visible = True
        
        print(f"🏁 Race course '{self.course_name}' started!")
    
    def update(self, dt, player_position, player_velocity):
        """Update course progress"""
        if not self.course_active:
            return
        
        # Update rings
        for ring in self.rings:
            ring.update(dt)
        
        # Update targets
        for target in self.targets:
            target.update(dt)
        
        # Check ring passages
        if self.current_ring_index < len(self.rings):
            current_ring = self.rings[self.current_ring_index]
            
            if current_ring.check_passage(player_position, player_velocity):
                self.rings_completed += 1
                self.total_score += current_ring.points
                self.current_ring_index += 1
                
                # Speed bonus for speed rings
                if hasattr(current_ring, 'speed_bonus'):
                    speed = distance(player_velocity, Vec3(0, 0, 0))
                    if speed > 25:  # High speed bonus
                        bonus = int(speed * 10)
                        self.total_score += bonus
                        print(f"💨 Speed bonus: {bonus} points!")
        
        # Check target collections
        for target in self.targets:
            if target.check_collection(player_position):
                self.targets_collected += 1
                self.total_score += target.value
        
        # Check course completion
        if self.current_ring_index >= len(self.rings):
            self.complete_course()
    
    def complete_course(self):
        """Complete the course and calculate final score"""
        if not self.course_active:
            return
        
        self.course_active = False
        completion_time = time.time() - self.start_time
        
        # Time bonus
        if completion_time < self.time_bonus_remaining:
            time_bonus = int((self.time_bonus_remaining - completion_time) * 10)
            self.total_score += time_bonus
        
        # Perfect run bonus
        if self.targets_collected == len(self.targets):
            perfect_bonus = 1000
            self.total_score += perfect_bonus
            print(f"🏆 Perfect run bonus: {perfect_bonus} points!")
        
        # Update best time
        if self.best_time is None or completion_time < self.best_time:
            self.best_time = completion_time
            print(f"🥇 New best time: {completion_time:.2f} seconds!")
        
        print(f"🏁 Course completed!")
        print(f"   Time: {completion_time:.2f} seconds")
        print(f"   Rings: {self.rings_completed}/{len(self.rings)}")
        print(f"   Targets: {self.targets_collected}/{len(self.targets)}")
        print(f"   Final Score: {self.total_score}")
    
    def get_next_ring_position(self):
        """Get position of next ring for navigation aid"""
        if self.current_ring_index < len(self.rings):
            return self.rings[self.current_ring_index].position
        return None

class RacingManager:
    """Manages multiple race courses and racing gameplay"""
    
    def __init__(self):
        self.courses = {}
        self.active_course = None
        self.course_selector = 0
        
        # Create available courses
        self.create_courses()
        
        print(f"🏁 Racing Manager initialized with {len(self.courses)} courses")
    
    def create_courses(self):
        """Create all available race courses"""
        course_configs = [
            ('Golden Gate Circuit', 'normal'),
            ('Twin Peaks Challenge', 'hard'),
            ('Alcatraz Run', 'normal'),
            ('Bay Tour', 'easy'),
        ]
        
        for course_name, difficulty in course_configs:
            course = RaceCourse(course_name, difficulty)
            self.courses[course_name] = course
    
    def start_course(self, course_name):
        """Start a specific course"""
        if course_name in self.courses:
            self.active_course = self.courses[course_name]
            self.active_course.start_course()
            return True
        return False
    
    def update(self, dt, player_position, player_velocity):
        """Update active course"""
        if self.active_course:
            self.active_course.update(dt, player_position, player_velocity)
    
    def get_course_status(self):
        """Get current course status"""
        if not self.active_course:
            return None
        
        return {
            'course_name': self.active_course.course_name,
            'active': self.active_course.course_active,
            'rings_completed': self.active_course.rings_completed,
            'total_rings': len(self.active_course.rings),
            'targets_collected': self.active_course.targets_collected,
            'total_targets': len(self.active_course.targets),
            'score': self.active_course.total_score,
            'next_ring_pos': self.active_course.get_next_ring_position()
        }
    
    def get_available_courses(self):
        """Get list of available courses"""
        return list(self.courses.keys()) 