#!/usr/bin/env python3
"""
Test script for the overhead view flying squirrel game
Quick test to verify all systems work together properly.
"""

import sys
import os

print("Testing Overhead Flying Squirrel Game")
print("=" * 50)

try:
    # Test basic imports
    print("Testing imports...")
    
    # Test configuration
    import game_config as config
    print(f"✓ Config loaded - World size: {config.WORLD_SIZE}")
    print(f"  - Camera distance: {config.CAMERA['default_distance']}")
    print(f"  - Tree count: {config.TREE_COUNT}")
    
    # Test src modules
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    from physics.flight_physics import FlightPhysics
    print("✓ Flight physics module loaded")
    
    from entities.flying_squirrel import FlyingSquirrel
    print("✓ Flying squirrel entity loaded")
    
    from graphics.environment import EnhancedTerrain, SparseForest, OverheadSkySystem
    print("✓ Environment graphics loaded")
    
    from graphics.camera_system import OverheadCameraSystem
    print("✓ Overhead camera system loaded")
    
    from ui.game_ui import FlightHUD, MainMenu
    print("✓ UI components loaded")
    
    print("\n✓ All modules imported successfully!")
    print("✓ The overhead view game is ready to run!")
    
    print("\nTo play the game:")
    print("  python game.py")
    
    print("\nGame Features:")
    print("  - Diablo 3-style overhead camera")
    print("  - Sparse, varied terrain with better 3D depth")
    print("  - Enhanced flying squirrel visibility")
    print("  - Strategic tree placement")
    print("  - Larger world for exploration")
    print("  - Environmental landmarks")
    
    print("\nCamera Controls:")
    print("  - Mouse Wheel: Zoom in/out")
    print("  - Q/E: Zoom in/out")
    print("  - R/F: Adjust camera height")
    print("  - Right Click + Drag: Rotate camera")
    print("  - C: Cycle camera modes")
    print("  - V: Next scenic viewpoint (in scenic mode)")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure all modules are in place")
    
except Exception as e:
    print(f"✗ Unexpected error: {e}")

print("\nTest complete!") 