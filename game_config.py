"""
Game Configuration Settings
Centralized configuration for the Flying Squirrel Flight Simulator
"""

# World Settings
WORLD_SIZE = 200
TERRAIN_SCALE = 0.1
TERRAIN_HEIGHT_MULTIPLIER = 20
TREE_COUNT = 300

# Physics Settings
GRAVITY = -9.8
WIND_STRENGTH = 0.5
AIR_DENSITY = 1.225  # kg/m³ at sea level

# Flying Squirrel Settings
SQUIRREL_PHYSICS = {
    'max_speed': 25,
    'glide_ratio': 4.0,
    'lift_coefficient': 0.8,
    'drag_coefficient': 0.02,
    'mass': 1.5,  # kg
    'wing_area': 2.0,  # m²
    'max_pitch_rate': 2.0,  # rad/s
    'max_yaw_rate': 2.0,   # rad/s
    'max_roll_angle': 0.5,  # rad
}

# Visual Settings
GRAPHICS = {
    'enable_shadows': True,
    'enable_fog': True,
    'fog_distance': 100,
    'fog_color': (0.7, 0.8, 0.9),
    'sky_color': (0.5, 0.7, 1.0),
    'ambient_light': (0.4, 0.4, 0.4),
    'sun_intensity': 1.0,
}

# Game Settings
GAME = {
    'start_altitude': 20,
    'respawn_altitude': 15,
    'collision_detection': True,
    'thermal_updrafts': True,
    'weather_effects': False,
}

# Controls Settings
CONTROLS = {
    'mouse_sensitivity': 1.0,
    'keyboard_sensitivity': 1.0,
    'invert_pitch': False,
    'camera_smoothing': 0.9,
}

# Debug Settings
DEBUG = {
    'show_fps': True,
    'show_physics_debug': False,
    'show_collision_bounds': False,
    'god_mode': False,
} 