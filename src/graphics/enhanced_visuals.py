"""
✨ ENHANCED VISUAL EFFECTS SYSTEM ✨
Next-generation graphics with advanced lighting, particles, and atmospheric effects.
"""

import math
import random
from ursina import *

class AdvancedParticleSystem:
    """High-performance particle system with multiple effect types"""
    
    def __init__(self, max_particles=200):
        self.max_particles = max_particles
        self.particle_pools = {
            'trail': [],
            'explosion': [],
            'smoke': [],
            'sparkle': [],
            'wind': [],
            'thermal': [],
            'wing_tip_vortex': []
        }
        
        # Pre-create particle pools for performance
        self.initialize_particle_pools()
        
        print(f"✨ Advanced Particle System initialized with {max_particles} particles")
    
    def initialize_particle_pools(self):
        """Pre-create particle objects for reuse"""
        particles_per_type = self.max_particles // len(self.particle_pools)
        
        for effect_type in self.particle_pools:
            for _ in range(particles_per_type):
                particle = Entity(
                    model='cube',
                    color=color.white,
                    scale=0.1,
                    visible=False,
                    parent=scene
                )
                particle.velocity = Vec3(0, 0, 0)
                particle.life = 0
                particle.max_life = 1
                particle.active = False
                
                self.particle_pools[effect_type].append(particle)
    
    def emit_trail_particles(self, position, velocity, intensity=1.0):
        """Emit trail particles behind flying object"""
        num_particles = int(3 * intensity)
        
        for _ in range(num_particles):
            particle = self.get_available_particle('trail')
            if not particle:
                return
            
            # Position with some spread
            offset = Vec3(
                random.uniform(-0.5, 0.5),
                random.uniform(-0.3, 0.3),
                random.uniform(-0.5, 0.5)
            )
            particle.position = position + offset
            
            # Velocity based on object movement
            particle.velocity = -velocity * 0.3 + Vec3(
                random.uniform(-1, 1),
                random.uniform(-0.5, 0.5),
                random.uniform(-1, 1)
            )
            
            # Appearance
            particle.color = color.rgba(255, 200, 100, 150)
            particle.scale = random.uniform(0.05, 0.15)
            particle.life = 0
            particle.max_life = random.uniform(1.0, 2.5)
            particle.active = True
            particle.visible = True
    
    def emit_wing_tip_vortices(self, left_wing_tip, right_wing_tip, velocity, intensity=1.0):
        """Emit wing tip vortex particles"""
        for wing_tip in [left_wing_tip, right_wing_tip]:
            if not wing_tip:
                continue
            
            for _ in range(int(2 * intensity)):
                particle = self.get_available_particle('wing_tip_vortex')
                if not particle:
                    continue
                
                # Spiral pattern for vortex
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0.2, 0.8)
                
                offset = Vec3(
                    math.cos(angle) * radius,
                    random.uniform(-0.2, 0.2),
                    math.sin(angle) * radius
                )
                
                particle.position = wing_tip + offset
                
                # Circular velocity for vortex
                vortex_velocity = Vec3(
                    -math.sin(angle) * 2,
                    random.uniform(-0.5, 0.5),
                    math.cos(angle) * 2
                )
                
                particle.velocity = vortex_velocity + velocity * 0.1
                
                # Appearance
                particle.color = color.rgba(200, 220, 255, 80)
                particle.scale = random.uniform(0.03, 0.08)
                particle.life = 0
                particle.max_life = random.uniform(2.0, 4.0)
                particle.active = True
                particle.visible = True
    
    def emit_thermal_particles(self, position, strength):
        """Emit thermal updraft visualization particles"""
        num_particles = int(5 * strength)
        
        for _ in range(num_particles):
            particle = self.get_available_particle('thermal')
            if not particle:
                return
            
            # Random position in thermal column
            radius = random.uniform(0, strength * 3)
            angle = random.uniform(0, 2 * math.pi)
            
            offset = Vec3(
                math.cos(angle) * radius,
                random.uniform(-2, 0),
                math.sin(angle) * radius
            )
            
            particle.position = position + offset
            
            # Upward velocity with some rotation
            particle.velocity = Vec3(
                math.sin(angle) * 0.5,
                strength * 2,
                math.cos(angle) * 0.5
            )
            
            # Appearance
            particle.color = color.rgba(255, 255, 200, 60)
            particle.scale = random.uniform(0.1, 0.3)
            particle.life = 0
            particle.max_life = random.uniform(3.0, 6.0)
            particle.active = True
            particle.visible = True
    
    def emit_explosion_particles(self, position, intensity=1.0):
        """Emit explosion particles"""
        num_particles = int(15 * intensity)
        
        for _ in range(num_particles):
            particle = self.get_available_particle('explosion')
            if not particle:
                return
            
            particle.position = position
            
            # Random explosion direction
            direction = Vec3(
                random.uniform(-1, 1),
                random.uniform(-0.5, 1),
                random.uniform(-1, 1)
            ).normalized()
            
            particle.velocity = direction * random.uniform(5, 15)
            
            # Appearance
            particle.color = color.rgba(255, random.randint(100, 200), 0, 200)
            particle.scale = random.uniform(0.1, 0.4)
            particle.life = 0
            particle.max_life = random.uniform(0.8, 2.0)
            particle.active = True
            particle.visible = True
    
    def get_available_particle(self, effect_type):
        """Get an available particle from the pool"""
        for particle in self.particle_pools[effect_type]:
            if not particle.active:
                return particle
        return None
    
    def update(self, dt):
        """Update all active particles"""
        for effect_type, particles in self.particle_pools.items():
            for particle in particles:
                if not particle.active:
                    continue
                
                # Update life
                particle.life += dt
                
                if particle.life >= particle.max_life:
                    # Particle expired
                    particle.active = False
                    particle.visible = False
                    continue
                
                # Update position
                particle.position += particle.velocity * dt
                
                # Apply gravity to some particle types
                if effect_type in ['explosion', 'smoke']:
                    particle.velocity.y -= 9.8 * dt
                
                # Apply drag
                particle.velocity *= 0.98
                
                # Update appearance based on life
                life_factor = particle.life / particle.max_life
                
                # Fade out over time
                if effect_type == 'trail':
                    alpha = int(150 * (1 - life_factor))
                    particle.color = color.rgba(255, 200, 100, alpha)
                elif effect_type == 'thermal':
                    alpha = int(60 * (1 - life_factor**2))
                    particle.color = color.rgba(255, 255, 200, alpha)
                elif effect_type == 'wing_tip_vortex':
                    alpha = int(80 * (1 - life_factor))
                    particle.color = color.rgba(200, 220, 255, alpha)
                elif effect_type == 'explosion':
                    alpha = int(200 * (1 - life_factor))
                    red_component = max(100, 255 - int(life_factor * 155))
                    particle.color = color.rgba(255, red_component, 0, alpha)
                
                # Scale changes
                if effect_type == 'explosion':
                    particle.scale = particle.scale * (1 + dt * 2)  # Expand
                elif effect_type == 'thermal':
                    particle.scale = particle.scale * (1 + dt * 0.5)  # Gentle expansion

class DynamicLightingSystem:
    """Advanced lighting system with time of day and weather effects"""
    
    def __init__(self):
        self.time_of_day = 12.0  # 24-hour format
        self.weather_condition = 'clear'  # clear, cloudy, stormy, foggy
        self.lighting_intensity = 1.0
        
        # Light sources
        self.sun_light = None
        self.ambient_light = None
        self.fog_settings = {
            'density': 0.005,
            'color': color.rgb(0.8, 0.9, 1.0)
        }
        
        self.setup_lighting()
        print("💡 Dynamic Lighting System initialized")
    
    def setup_lighting(self):
        """Initialize lighting components"""
        # Sun/Moon directional light
        self.sun_light = DirectionalLight(
            color=color.rgb(255, 220, 180),
            rotation=(60, 45, 0)
        )
        
        # Ambient lighting
        self.ambient_light = AmbientLight(
            color=color.rgb(100, 120, 150)
        )
        
        # Sky dome
        self.sky = Sky(texture='sky_default')
    
    def update_time_of_day(self, dt, time_speed=1.0):
        """Update lighting based on time of day"""
        self.time_of_day += (dt * time_speed / 3600)  # Convert to hours
        if self.time_of_day >= 24:
            self.time_of_day -= 24
        
        # Calculate sun position
        hour_angle = (self.time_of_day - 12) * 15  # Degrees from noon
        sun_elevation = 90 - abs(hour_angle)  # Simplified sun path
        
        # Adjust sun light
        if sun_elevation > 0:
            # Daytime
            intensity = max(0.3, sun_elevation / 90)
            
            # Color temperature changes throughout day
            if 6 <= self.time_of_day <= 18:  # Day
                red = 255
                green = int(220 + (self.time_of_day - 12) * 5)
                blue = int(180 + (self.time_of_day - 12) * 10)
            else:  # Dawn/Dusk
                red = 255
                green = int(150 + abs(self.time_of_day - 12) * 5)
                blue = int(100 + abs(self.time_of_day - 12) * 8)
            
            self.sun_light.color = color.rgb(red, green, blue)
            self.sun_light.rotation = (sun_elevation, hour_angle, 0)
            
            # Ambient light
            ambient_intensity = intensity * 0.4
            self.ambient_light.color = color.rgb(
                int(100 * ambient_intensity),
                int(120 * ambient_intensity),
                int(150 * ambient_intensity)
            )
        else:
            # Nighttime
            self.sun_light.color = color.rgb(50, 70, 120)  # Moonlight
            self.ambient_light.color = color.rgb(20, 30, 50)
    
    def set_weather_condition(self, condition):
        """Change weather and adjust lighting accordingly"""
        self.weather_condition = condition
        
        if condition == 'clear':
            self.lighting_intensity = 1.0
            self.fog_settings['density'] = 0.005
            self.fog_settings['color'] = color.rgb(0.8, 0.9, 1.0)
        
        elif condition == 'cloudy':
            self.lighting_intensity = 0.7
            self.fog_settings['density'] = 0.008
            self.fog_settings['color'] = color.rgb(0.7, 0.7, 0.8)
        
        elif condition == 'stormy':
            self.lighting_intensity = 0.4
            self.fog_settings['density'] = 0.015
            self.fog_settings['color'] = color.rgb(0.5, 0.5, 0.6)
        
        elif condition == 'foggy':
            self.lighting_intensity = 0.6
            self.fog_settings['density'] = 0.025
            self.fog_settings['color'] = color.rgb(0.9, 0.9, 0.9)
        
        # Apply fog settings
        scene.fog_density = self.fog_settings['density']
        scene.fog_color = self.fog_settings['color']
    
    def create_lightning_flash(self, position):
        """Create dramatic lightning effect"""
        # Temporary bright light
        lightning_light = PointLight(
            position=position,
            color=color.rgb(255, 255, 255),
            intensity=3.0
        )
        
        # Flash effect
        flash_entity = Entity(
            model='sphere',
            color=color.rgba(255, 255, 255, 100),
            scale=50,
            position=position,
            parent=scene
        )
        
        # Animate flash
        flash_entity.animate('color', color.rgba(255, 255, 255, 0), duration=0.2)
        flash_entity.animate_scale(100, duration=0.2)
        
        # Cleanup
        destroy(lightning_light, delay=0.2)
        destroy(flash_entity, delay=0.3)

class WeatherSystem:
    """Dynamic weather system with multiple conditions"""
    
    def __init__(self, lighting_system):
        self.lighting_system = lighting_system
        self.current_weather = 'clear'
        self.weather_transition_time = 0
        self.weather_duration = random.uniform(300, 600)  # 5-10 minutes
        
        # Weather particles
        self.rain_particles = []
        self.snow_particles = []
        self.cloud_shadows = []
        
        print("🌤️ Weather System initialized")
    
    def update(self, dt):
        """Update weather conditions"""
        self.weather_transition_time += dt
        
        # Change weather periodically
        if self.weather_transition_time >= self.weather_duration:
            self.transition_weather()
            self.weather_transition_time = 0
            self.weather_duration = random.uniform(300, 600)
        
        # Update weather effects
        self.update_weather_effects(dt)
    
    def transition_weather(self):
        """Transition to new weather condition"""
        weather_options = ['clear', 'cloudy', 'stormy', 'foggy']
        
        # Weighted random selection (favor clear weather)
        weights = [0.4, 0.3, 0.2, 0.1]
        
        self.current_weather = random.choices(weather_options, weights)[0]
        self.lighting_system.set_weather_condition(self.current_weather)
        
        print(f"🌤️ Weather changed to: {self.current_weather}")
    
    def update_weather_effects(self, dt):
        """Update visual weather effects"""
        if self.current_weather == 'stormy':
            self.update_storm_effects(dt)
        elif self.current_weather == 'foggy':
            self.update_fog_effects(dt)
    
    def update_storm_effects(self, dt):
        """Update storm visual effects"""
        # Occasional lightning
        if random.random() < 0.001:  # 0.1% chance per frame
            lightning_pos = Vec3(
                random.uniform(-200, 200),
                random.uniform(80, 150),
                random.uniform(-200, 200)
            )
            self.lighting_system.create_lightning_flash(lightning_pos)
    
    def update_fog_effects(self, dt):
        """Update fog rolling effects"""
        # Fog density variation
        base_density = 0.025
        variation = math.sin(time.time() * 0.1) * 0.005
        scene.fog_density = base_density + variation

class EnhancedUI:
    """Enhanced UI with better visual appeal"""
    
    def __init__(self):
        self.hud_elements = {}
        self.setup_enhanced_hud()
        print("🎨 Enhanced UI initialized")
    
    def setup_enhanced_hud(self):
        """Create enhanced HUD elements"""
        # Flight data panel with background
        self.flight_panel = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(0, 0, 0, 100),
            scale=(0.35, 0.25, 1),
            position=(-0.65, 0.35, 0)
        )
        
        # Enhanced flight instruments
        self.create_artificial_horizon()
        self.create_speed_indicator()
        self.create_altitude_tape()
        self.create_compass_rose()
    
    def create_artificial_horizon(self):
        """Create artificial horizon instrument"""
        # Horizon background
        horizon_bg = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(20, 20, 40, 200),
            scale=(0.15, 0.15, 1),
            position=(-0.75, 0.4, 0)
        )
        
        # Sky portion
        sky_portion = Entity(
            parent=horizon_bg,
            model='cube',
            color=color.rgba(100, 150, 255, 150),
            scale=(1, 0.5, 1),
            position=(0, 0.25, 0)
        )
        
        # Ground portion
        ground_portion = Entity(
            parent=horizon_bg,
            model='cube',
            color=color.rgba(139, 69, 19, 150),
            scale=(1, 0.5, 1),
            position=(0, -0.25, 0)
        )
        
        # Horizon line
        horizon_line = Entity(
            parent=horizon_bg,
            model='cube',
            color=color.white,
            scale=(1.2, 0.02, 1),
            position=(0, 0, 0.01)
        )
        
        self.hud_elements['horizon'] = {
            'background': horizon_bg,
            'sky': sky_portion,
            'ground': ground_portion,
            'line': horizon_line
        }
    
    def create_speed_indicator(self):
        """Create speed tape indicator"""
        # Speed tape background
        speed_bg = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.08, 0.3, 1),
            position=(-0.9, 0.2, 0)
        )
        
        # Speed text
        speed_text = Text(
            '0',
            parent=camera.ui,
            scale=2,
            color=color.lime,
            position=(-0.9, 0.2, 0),
            origin=(0, 0)
        )
        
        self.hud_elements['speed'] = {
            'background': speed_bg,
            'text': speed_text
        }
    
    def create_altitude_tape(self):
        """Create altitude tape indicator"""
        # Altitude tape background
        alt_bg = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.08, 0.3, 1),
            position=(-0.55, 0.2, 0)
        )
        
        # Altitude text
        alt_text = Text(
            '0',
            parent=camera.ui,
            scale=2,
            color=color.cyan,
            position=(-0.55, 0.2, 0),
            origin=(0, 0)
        )
        
        self.hud_elements['altitude'] = {
            'background': alt_bg,
            'text': alt_text
        }
    
    def create_compass_rose(self):
        """Create compass rose"""
        # Compass background
        compass_bg = Entity(
            parent=camera.ui,
            model='cube',
            color=color.rgba(0, 0, 0, 150),
            scale=(0.12, 0.12, 1),
            position=(-0.75, 0.15, 0)
        )
        
        # Compass needle
        compass_needle = Entity(
            parent=compass_bg,
            model='cube',
            color=color.red,
            scale=(0.05, 0.8, 1),
            position=(0, 0, 0.01)
        )
        
        # Direction markers
        for i, direction in enumerate(['N', 'E', 'S', 'W']):
            angle = i * 90
            marker_x = math.cos(math.radians(angle)) * 0.4
            marker_y = math.sin(math.radians(angle)) * 0.4
            
            direction_text = Text(
                direction,
                parent=compass_bg,
                scale=1.5,
                color=color.white,
                position=(marker_x, marker_y, 0.01),
                origin=(0, 0)
            )
        
        self.hud_elements['compass'] = {
            'background': compass_bg,
            'needle': compass_needle
        }
    
    def update_flight_instruments(self, flight_data):
        """Update all flight instruments"""
        # Update speed
        if 'speed' in self.hud_elements:
            speed = flight_data.get('speed', 0)
            self.hud_elements['speed']['text'].text = f"{speed:.0f}"
            
            # Color coding for speed
            if speed > 35:
                self.hud_elements['speed']['text'].color = color.red
            elif speed > 25:
                self.hud_elements['speed']['text'].color = color.yellow
            else:
                self.hud_elements['speed']['text'].color = color.lime
        
        # Update altitude
        if 'altitude' in self.hud_elements:
            altitude = flight_data.get('altitude', 0)
            self.hud_elements['altitude']['text'].text = f"{altitude:.0f}"
            
            # Color coding for altitude
            if altitude < 10:
                self.hud_elements['altitude']['text'].color = color.red
            elif altitude < 25:
                self.hud_elements['altitude']['text'].color = color.yellow
            else:
                self.hud_elements['altitude']['text'].color = color.cyan
        
        # Update compass
        if 'compass' in self.hud_elements:
            heading = flight_data.get('heading', 0)
            self.hud_elements['compass']['needle'].rotation_z = -heading
        
        # Update artificial horizon
        if 'horizon' in self.hud_elements:
            pitch = flight_data.get('pitch', 0)
            roll = flight_data.get('roll', 0)
            
            # Rotate horizon based on roll
            self.hud_elements['horizon']['line'].rotation_z = roll
            
            # Move horizon based on pitch
            pitch_offset = pitch * 0.01  # Scale factor
            self.hud_elements['horizon']['line'].y = pitch_offset 