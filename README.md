# Flying Squirrel Flight Simulator - Overhead View

A 3D flight simulator game with **Diablo 3-style overhead camera** where you control a flying squirrel through a beautiful, sparse natural environment optimized for strategic gameplay and enhanced 3D depth perception.

## ✨ New Features - Overhead View System

- **🎥 Diablo 3-Style Camera**: Strategic overhead view showing much more of the environment
- **🌍 Sparse, Varied Terrain**: Better 3D depth with distinct biomes (valleys, hills, mountains)
- **🌳 Strategic Tree Placement**: Trees in clusters for visual landmarks, not scattered clutter
- **🏔️ Environmental Landmarks**: Rock formations, lakes, and clearings for navigation
- **🐿️ Enhanced Squirrel Visibility**: Larger, more detailed model optimized for overhead view
- **📏 Altitude Indicators**: Ground shadows and altitude lines for depth perception
- **🎮 Multiple Camera Modes**: Overhead, cinematic, and scenic viewpoints

## 🎮 Enhanced Gameplay Features

- **Realistic Flight Physics**: Experience gliding mechanics similar to real flying squirrels
- **Thermal Updrafts**: Find and use rising air currents to gain altitude
- **Strategic Exploration**: Large world with varied terrain encouraging exploration
- **Collectible System**: Enhanced collectibles with beacons for overhead visibility
- **Objective System**: Multiple goals including map exploration and speed challenges
- **Dynamic Environment**: Particle effects, wing tip vortices, and atmospheric effects

## 🎛️ Camera Controls (New!)

- **Mouse Wheel**: Zoom in/out
- **Q/E Keys**: Alternative zoom controls
- **R/F Keys**: Adjust camera height
- **Right Click + Drag**: Rotate camera around squirrel
- **C Key**: Cycle between camera modes (Overhead/Scenic)
- **V Key**: Next scenic viewpoint (when in scenic mode)

## 🕹️ Flight Controls

- **W/A/S/D**: Pitch and yaw control
- **Space**: Glide boost / flare maneuver
- **Shift**: Dive for speed
- **Mouse**: Look around (in some camera modes)
- **ESC**: Pause/Exit game
- **F1**: Toggle HUD visibility
- **F11**: Toggle fullscreen

## 🎯 Game Objectives

1. **🌰 Collect 10 acorns** scattered throughout the forest
2. **📈 Reach 60 meters altitude** using thermal updrafts
3. **⏱️ Fly continuously for 3 minutes** without landing
4. **🗺️ Visit all 4 corners** of the map for exploration bonus
5. **💨 Achieve 25 m/s top speed** for speed demon achievement
6. **🌪️ Master thermal flying** to efficiently gain altitude

## 🚀 Installation & Setup

1. **Prerequisites**: Python 3.8+ required
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Game**:
   ```bash
   python game.py          # Enhanced overhead view (recommended)
   python main.py          # Original close-up view
   ```

## 🎨 Visual Enhancements

### Terrain System
- **Multiple Biomes**: Central valleys, rolling hills, mountain ranges
- **Height-Based Coloring**: Valleys (green) → Hills (brown) → Mountains (gray)
- **Strategic Spacing**: More open areas for better flight paths
- **Procedural Generation**: Varied, realistic landscape using multiple noise octaves

### Flying Squirrel Model
- **Enhanced Visibility**: 1.5x larger scale for overhead view
- **Detailed Anatomy**: Wings, tail membrane, legs, and body parts
- **Dynamic Animations**: Wing flapping, tail steering, speed-based scaling
- **Flight Effects**: Particle trails, wing tip vortices, altitude shadows

### Environmental Features
- **Sparse Forest**: Trees in strategic clusters, not random scatter
- **Visual Landmarks**: Rock formations, lakes, and clearings
- **Atmospheric Effects**: Optimized fog and lighting for overhead view
- **Particle Systems**: Wind effects and motion trails

## 🎪 Camera Modes

### 1. Overhead Mode (Default)
- **Strategic View**: Diablo 3-style overhead perspective
- **Smooth Following**: Camera tracks squirrel with configurable smoothing
- **Zoom Control**: 18-60 unit distance range
- **Height Adjustment**: 12-50 unit height range
- **Rotation**: Full 360° camera rotation around target

### 2. Cinematic Mode
- **Intro Sequence**: Automatic high-altitude overview of the world
- **Smooth Transitions**: Ease-in-out interpolation
- **Story Moments**: Can be triggered for special events

### 3. Scenic Mode
- **Fixed Viewpoints**: Pre-positioned scenic overlooks
- **World Showcase**: Multiple angles showing terrain variety
- **Manual Control**: Cycle through viewpoints with V key

## 🎲 Game Mechanics

### Physics System
- **Realistic Aerodynamics**: Lift, drag, gravity, and wind forces
- **Thermal Modeling**: 20+ thermal zones with varying strength
- **Stall Behavior**: Realistic flight envelope with stall recovery
- **G-Force Simulation**: Acceleration effects on maneuverability

### Exploration System
- **Map Tracking**: Automatic tracking of visited areas
- **Exploration Bonus**: Points for discovering new regions
- **Strategic Placement**: Collectibles positioned to encourage exploration
- **Landmark Navigation**: Visual waypoints for orientation

## 🛠️ Technical Features

- **Modular Architecture**: Clean separation of systems (physics, graphics, UI)
- **Performance Optimized**: Efficient for overhead view with reduced polygon count
- **Configurable Settings**: Extensive configuration via `game_config.py`
- **Professional Structure**: Organized codebase with proper imports and documentation

## 📁 Project Structure

```
game_1/
├── 🎮 game.py                 # Enhanced main game (overhead view)
├── 🎮 main.py                 # Original close-up view game
├── ⚙️ game_config.py          # Configuration settings
├── 🧪 test_overhead_game.py   # Test script for overhead system
├── 📖 README.md               # This file
├── 📋 requirements.txt        # Python dependencies
├── 📄 LICENSE                 # MIT License
├── 📦 setup.py               # Package configuration
└── 📂 src/                   # Source code modules
    ├── 🐿️ entities/           # Flying squirrel and game objects
    ├── ⚛️ physics/            # Advanced flight physics engine
    ├── 🎨 graphics/           # Environment, camera systems
    └── 🖥️ ui/                # HUD, menus, and interface
```

## 🎯 What Makes This Special

1. **🎥 Unique Perspective**: First flying squirrel game with strategic overhead view
2. **🌍 Intelligent Design**: Sparse, varied environment prioritizing 3D depth over clutter
3. **🎮 Professional Quality**: Advanced camera system rivaling commercial games
4. **🔬 Realistic Physics**: Scientifically-based aerodynamics and thermal modeling
5. **🏗️ Extensible Architecture**: Clean, modular codebase for easy enhancement

## 🎊 Getting Started Tips

1. **🏁 Start Simple**: Use WASD for basic flight, get comfortable with movement
2. **🎥 Explore Camera**: Try mouse wheel zoom and R/F height adjustment
3. **🌪️ Find Thermals**: Look for areas where LIFT indicator shows positive values
4. **🌰 Collect Items**: Follow the glowing beacons to find collectibles
5. **🗺️ Explore Actively**: Visit different terrain types for exploration bonus

## 🔧 Development

Built with modern Python game development practices:
- **Ursina Engine**: Advanced 3D rendering and scene management
- **NumPy**: High-performance physics calculations
- **Perlin Noise**: Realistic procedural terrain generation
- **Object-Oriented Design**: Clean, maintainable code structure

## 🎮 Performance

Optimized for smooth gameplay:
- **60 FPS Target**: Consistent frame rate on modern hardware
- **Efficient Rendering**: Reduced polygon count for overhead view
- **Smart LOD**: Level-of-detail optimization for distant objects
- **Configurable Quality**: Adjustable settings for different hardware

---

**🎉 Ready to soar? Launch `python game.py` and experience flight like never before!** 