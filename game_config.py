"""
Game Configuration Settings - Optimized for Overhead View
Centralized configuration for the Flying Squirrel Flight Simulator with Diablo 3-style camera.
"""

# World Settings - Enhanced for Overhead View
WORLD_SIZE = 300  # Larger world for better exploration
TERRAIN_SCALE = 0.02  # Larger terrain features
TERRAIN_HEIGHT_MULTIPLIER = 40  # More dramatic height differences
TREE_COUNT = 100  # Reduced for less clutter and better performance

# Physics Settings
GRAVITY = -9.8
WIND_STRENGTH = 0.8  # Slightly stronger for overhead gameplay
AIR_DENSITY = 1.225  # kg/m³ at sea level

# Flying Squirrel Settings - Optimized for Overhead View
SQUIRREL_PHYSICS = {
    'max_speed': 30,      # Increased for larger world
    'glide_ratio': 4.5,   # Improved gliding
    'lift_coefficient': 0.9,
    'drag_coefficient': 0.018,  # Reduced for better performance
    'mass': 1.2,          # Lighter for better maneuverability
    'wing_area': 2.5,     # Larger wing area
    'max_pitch_rate': 2.5,
    'max_yaw_rate': 2.5,
    'max_roll_angle': 0.6,
    'start_altitude': 25,  # Higher starting altitude
}

# Visual Settings - Optimized for Overhead View
GRAPHICS = {
    'enable_shadows': False,     # Disabled for better performance
    'enable_fog': True,
    'fog_distance': 150,         # Increased for larger world
    'fog_color': (0.8, 0.9, 1.0),
    'sky_color': (0.6, 0.8, 1.0),
    'ambient_light': (0.5, 0.5, 0.5),  # Brighter for better visibility
    'sun_intensity': 1.2,
}

# Game Settings - Enhanced for Overhead Gameplay
GAME = {
    'start_altitude': 25,        # Higher starting position
    'respawn_altitude': 20,
    'collision_detection': True,
    'thermal_updrafts': True,
    'weather_effects': False,    # Disabled for clearer visibility
    'collectible_count': 25,     # Total collectibles
    'exploration_bonus': True,   # Bonus for visiting new areas
}

# Camera Settings - New for Overhead View
CAMERA = {
    'default_distance': 30,      # Distance from squirrel
    'default_height': 25,        # Height above squirrel
    'viewing_angle': 45,         # Degrees
    'smoothing': 0.08,          # Camera following smoothness
    'zoom_speed': 2.5,
    'min_distance': 18,
    'max_distance': 60,
    'min_height': 12,
    'max_height': 50,
    'fov': 70,                  # Field of view for better overview
}

# Controls Settings
CONTROLS = {
    'mouse_sensitivity': 1.2,    # Slightly higher for overhead view
    'keyboard_sensitivity': 1.0,
    'invert_pitch': False,
    'camera_smoothing': 0.9,
    'zoom_sensitivity': 1.5,
}

# Performance Settings - Optimized for Overhead View
PERFORMANCE = {
    'terrain_resolution': 50,    # Good balance for overhead view
    'tree_clusters': 12,         # Strategic tree placement
    'trees_per_cluster': 6,      # Average trees per cluster
    'particle_count': 30,        # Reduced for better performance
    'update_frequency': 60,      # Target FPS
}

# Debug Settings
DEBUG = {
    'show_fps': True,
    'show_physics_debug': False,
    'show_collision_bounds': False,
    'show_camera_info': False,   # Camera position debugging
    'god_mode': False,
} 