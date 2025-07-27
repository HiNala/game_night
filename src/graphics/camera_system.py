"""
Overhead Camera System - Diablo 3 Style
Provides strategic overhead view for better environmental awareness and 3D depth perception.
"""

from ursina import *
import math

class OverheadCameraSystem:
    """Diablo 3-style overhead camera with smooth following and strategic positioning"""
    
    def __init__(self, target_entity, config=None):
        self.target = target_entity
        
        # Camera configuration
        self.config = config or {
            'distance': 25,      # Distance from target (much farther back)
            'height': 20,        # Height above target
            'angle': 45,         # Viewing angle (degrees)
            'smoothing': 0.05,   # Camera movement smoothing
            'rotation_speed': 2.0,
            'zoom_speed': 2.0,
            'min_distance': 15,
            'max_distance': 50,
            'min_height': 10,
            'max_height': 40
        }
        
        # Camera state
        self.current_distance = self.config['distance']
        self.current_height = self.config['height']
        self.current_angle = self.config['angle']
        self.target_distance = self.current_distance
        self.target_height = self.current_height
        
        # Smooth following
        self.smooth_position = Vec3(0, 0, 0)
        self.camera_offset = Vec3(0, 0, 0)
        
        # Setup camera
        self.setup_camera()
        
        print(f"Overhead camera initialized - Distance: {self.current_distance}, Height: {self.current_height}")
    
    def setup_camera(self):
        """Initialize camera settings for overhead view"""
        # Detach camera from any parent
        camera.parent = scene
        
        # Set initial position
        if self.target:
            self.smooth_position = self.target.position.copy()
        
        # Set camera parameters
        camera.fov = 60  # Wide field of view for better environmental visibility
        
        # Calculate initial camera position
        self.update_camera_position()
    
    def update_camera_position(self):
        """Update camera position based on target and settings"""
        if not self.target:
            return
        
        # Smooth follow target position
        target_pos = self.target.position
        self.smooth_position = lerp(
            self.smooth_position, 
            target_pos, 
            self.config['smoothing']
        )
        
        # Calculate camera offset based on distance and height
        offset_x = -self.current_distance * math.cos(math.radians(self.current_angle))
        offset_z = -self.current_distance * math.sin(math.radians(self.current_angle))
        offset_y = self.current_height
        
        self.camera_offset = Vec3(offset_x, offset_y, offset_z)
        
        # Set camera position
        camera.position = self.smooth_position + self.camera_offset
        
        # Look at target with slight offset for better view
        look_at_pos = self.smooth_position + Vec3(0, 2, 0)  # Look slightly above target
        camera.look_at(look_at_pos)
    
    def handle_input(self):
        """Handle camera control inputs"""
        # Mouse wheel for zoom
        if mouse.wheel_up:
            self.zoom_in()
        elif mouse.wheel_down:
            self.zoom_out()
        
        # Right mouse button for camera rotation (optional)
        if held_keys['right mouse']:
            if mouse.velocity.x != 0:
                self.rotate_camera(mouse.velocity.x * self.config['rotation_speed'])
        
        # Keyboard controls for camera adjustment
        if held_keys['q']:
            self.zoom_out()
        elif held_keys['e']:
            self.zoom_in()
        
        # Camera height adjustment
        if held_keys['r']:
            self.adjust_height(1)
        elif held_keys['f']:
            self.adjust_height(-1)
    
    def zoom_in(self):
        """Zoom camera closer to target"""
        self.target_distance = max(
            self.config['min_distance'], 
            self.current_distance - self.config['zoom_speed']
        )
        self.target_height = max(
            self.config['min_height'],
            self.current_height - self.config['zoom_speed'] * 0.5
        )
    
    def zoom_out(self):
        """Zoom camera farther from target"""
        self.target_distance = min(
            self.config['max_distance'], 
            self.current_distance + self.config['zoom_speed']
        )
        self.target_height = min(
            self.config['max_height'],
            self.current_height + self.config['zoom_speed'] * 0.5
        )
    
    def rotate_camera(self, delta_angle):
        """Rotate camera around target"""
        self.current_angle += delta_angle
        self.current_angle = self.current_angle % 360
    
    def adjust_height(self, delta):
        """Adjust camera height"""
        self.target_height = max(
            self.config['min_height'],
            min(self.config['max_height'], self.current_height + delta)
        )
    
    def update(self):
        """Update camera system each frame"""
        # Handle input
        self.handle_input()
        
        # Smooth camera distance and height changes
        self.current_distance = lerp(
            self.current_distance, 
            self.target_distance, 
            0.1
        )
        self.current_height = lerp(
            self.current_height, 
            self.target_height, 
            0.1
        )
        
        # Update camera position
        self.update_camera_position()
    
    def set_target(self, new_target):
        """Change camera target"""
        self.target = new_target
        if new_target:
            self.smooth_position = new_target.position.copy()
    
    def get_camera_info(self):
        """Get current camera information for debugging"""
        return {
            'distance': self.current_distance,
            'height': self.current_height,
            'angle': self.current_angle,
            'position': camera.position,
            'target_position': self.target.position if self.target else None
        }

class CinematicCamera:
    """Cinematic camera for dramatic shots and transitions"""
    
    def __init__(self):
        self.is_active = False
        self.duration = 0
        self.elapsed_time = 0
        self.start_position = Vec3(0, 0, 0)
        self.end_position = Vec3(0, 0, 0)
        self.start_rotation = Vec3(0, 0, 0)
        self.end_rotation = Vec3(0, 0, 0)
        self.callback = None
    
    def start_cinematic(self, end_pos, end_rot, duration=3.0, callback=None):
        """Start a cinematic camera movement"""
        self.is_active = True
        self.duration = duration
        self.elapsed_time = 0
        self.start_position = camera.position.copy()
        self.end_position = end_pos
        self.start_rotation = camera.rotation.copy()
        self.end_rotation = end_rot
        self.callback = callback
    
    def update(self):
        """Update cinematic camera"""
        if not self.is_active:
            return False
        
        self.elapsed_time += time.dt
        progress = min(1.0, self.elapsed_time / self.duration)
        
        # Smooth interpolation using ease-in-out
        smooth_progress = progress * progress * (3.0 - 2.0 * progress)
        
        # Interpolate position and rotation
        camera.position = lerp(self.start_position, self.end_position, smooth_progress)
        camera.rotation = lerp(self.start_rotation, self.end_rotation, smooth_progress)
        
        # Check if cinematic is complete
        if progress >= 1.0:
            self.is_active = False
            if self.callback:
                self.callback()
            return True
        
        return False

class EnvironmentViewCamera:
    """Special camera modes for showcasing the environment"""
    
    def __init__(self, terrain):
        self.terrain = terrain
        self.is_active = False
        self.view_points = []
        self.current_point = 0
        self.auto_rotate = False
        
        self.generate_scenic_viewpoints()
    
    def generate_scenic_viewpoints(self):
        """Generate scenic viewpoints across the terrain"""
        # High overlook points
        for angle in range(0, 360, 60):
            x = math.cos(math.radians(angle)) * 100
            z = math.sin(math.radians(angle)) * 100
            y = self.terrain.get_height_at_position(x, z) + 30
            
            viewpoint = {
                'position': Vec3(x, y, z),
                'look_at': Vec3(0, 10, 0),  # Look toward center
                'name': f'Overlook {angle//60 + 1}'
            }
            self.view_points.append(viewpoint)
    
    def activate_scenic_view(self, point_index=None):
        """Activate scenic camera view"""
        if point_index is None:
            point_index = random.randint(0, len(self.view_points) - 1)
        
        self.current_point = point_index % len(self.view_points)
        viewpoint = self.view_points[self.current_point]
        
        camera.position = viewpoint['position']
        camera.look_at(viewpoint['look_at'])
        
        self.is_active = True
        print(f"Scenic view activated: {viewpoint['name']}")
    
    def next_viewpoint(self):
        """Move to next scenic viewpoint"""
        self.current_point = (self.current_point + 1) % len(self.view_points)
        self.activate_scenic_view(self.current_point)
    
    def deactivate(self):
        """Deactivate scenic camera"""
        self.is_active = False 