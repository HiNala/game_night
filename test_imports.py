#!/usr/bin/env python3
"""
Test script to verify module imports and basic functionality
"""

import sys
import os

print("Flying Squirrel Flight Simulator - Import Test")
print("=" * 50)

# Test basic imports
try:
    import math
    import random
    print("✓ Basic Python modules imported successfully")
except ImportError as e:
    print(f"✗ Error importing basic modules: {e}")

# Test our configuration
try:
    import game_config as config
    print("✓ Game configuration loaded")
    print(f"  - World size: {config.WORLD_SIZE}")
    print(f"  - Tree count: {config.TREE_COUNT}")
except ImportError as e:
    print(f"✗ Error importing game config: {e}")

# Test our modules (without Ursina)
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    # Test physics module structure
    import src.physics
    print("✓ Physics package structure is valid")
    
    # Test entities module structure  
    import src.entities
    print("✓ Entities package structure is valid")
    
    # Test graphics module structure
    import src.graphics
    print("✓ Graphics package structure is valid")
    
    # Test UI module structure
    import src.ui
    print("✓ UI package structure is valid")
    
except ImportError as e:
    print(f"✗ Error importing our modules: {e}")

# Test Ursina (optional)
try:
    import ursina
    version = getattr(ursina, '__version__', 'unknown')
    print(f"✓ Ursina imported successfully (version: {version})")
    print("  Ready to run the full game!")
except ImportError:
    print("⚠ Ursina not installed - install requirements.txt to run the game")
except Exception as e:
    print(f"⚠ Ursina import issue: {e}")

print("\nModule structure test complete!")
print("\nTo run the game:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the enhanced game: python game.py")
print("3. Or run the simple version: python main.py") 