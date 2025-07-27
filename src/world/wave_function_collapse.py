"""
🌊 WAVE FUNCTION COLLAPSE - INFINITE WORLD GENERATOR 🌊
Advanced procedural generation system using WFC algorithm with logical rules.
Creates infinite, consistent worlds that follow realistic patterns.
"""

import math
import random
import numpy as np
from ursina import *
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class TerrainType(Enum):
    """Terrain tile types with logical properties"""
    WATER_DEEP = "water_deep"
    WATER_SHALLOW = "water_shallow"
    BEACH = "beach"
    PLAINS = "plains"
    HILLS_LOW = "hills_low"
    HILLS_HIGH = "hills_high"
    MOUNTAINS = "mountains"
    URBAN_LOW = "urban_low"
    URBAN_MED = "urban_med"
    URBAN_HIGH = "urban_high"
    FOREST = "forest"
    DESERT = "desert"
    BRIDGE = "bridge"
    AIRPORT = "airport"
    LANDMARK = "landmark"

@dataclass
class TerrainTile:
    """Individual terrain tile with properties"""
    terrain_type: TerrainType
    elevation: float
    population_density: float
    thermal_strength: float
    wind_resistance: float
    landmark_probability: float
    color: tuple
    model_scale: tuple

class WaveFunctionCollapse:
    """Advanced Wave Function Collapse algorithm for infinite world generation"""
    
    def __init__(self, chunk_size=32):
        self.chunk_size = chunk_size
        self.tile_types = self.define_tile_types()
        self.adjacency_rules = self.define_adjacency_rules()
        self.world_chunks = {}  # Dictionary of generated chunks
        self.active_chunks = set()  # Currently loaded chunks
        self.chunk_load_radius = 3  # Number of chunks to keep loaded around player
        
        # WFC state
        self.possible_states = {}  # What's possible at each position
        self.collapsed_tiles = {}  # Finalized tile positions
        self.propagation_queue = deque()
        
        print("🌊 Wave Function Collapse system initialized")
    
    def define_tile_types(self) -> Dict[TerrainType, TerrainTile]:
        """Define all possible terrain tile types with their properties"""
        tiles = {
            TerrainType.WATER_DEEP: TerrainTile(
                terrain_type=TerrainType.WATER_DEEP,
                elevation=-15.0,
                population_density=0.0,
                thermal_strength=0.2,
                wind_resistance=0.1,
                landmark_probability=0.0,
                color=(0.1, 0.3, 0.7),
                model_scale=(1, 0.1, 1)
            ),
            
            TerrainType.WATER_SHALLOW: TerrainTile(
                terrain_type=TerrainType.WATER_SHALLOW,
                elevation=-5.0,
                population_density=0.0,
                thermal_strength=0.3,
                wind_resistance=0.2,
                landmark_probability=0.05,
                color=(0.2, 0.5, 0.8),
                model_scale=(1, 0.2, 1)
            ),
            
            TerrainType.BEACH: TerrainTile(
                terrain_type=TerrainType.BEACH,
                elevation=2.0,
                population_density=0.1,
                thermal_strength=0.6,
                wind_resistance=0.3,
                landmark_probability=0.1,
                color=(0.9, 0.8, 0.6),
                model_scale=(1, 0.3, 1)
            ),
            
            TerrainType.PLAINS: TerrainTile(
                terrain_type=TerrainType.PLAINS,
                elevation=10.0,
                population_density=0.3,
                thermal_strength=0.7,
                wind_resistance=0.4,
                landmark_probability=0.15,
                color=(0.4, 0.7, 0.3),
                model_scale=(1, 0.4, 1)
            ),
            
            TerrainType.HILLS_LOW: TerrainTile(
                terrain_type=TerrainType.HILLS_LOW,
                elevation=50.0,
                population_density=0.2,
                thermal_strength=0.8,
                wind_resistance=0.6,
                landmark_probability=0.2,
                color=(0.5, 0.6, 0.3),
                model_scale=(1, 0.8, 1)
            ),
            
            TerrainType.HILLS_HIGH: TerrainTile(
                terrain_type=TerrainType.HILLS_HIGH,
                elevation=120.0,
                population_density=0.1,
                thermal_strength=1.0,
                wind_resistance=0.8,
                landmark_probability=0.3,
                color=(0.6, 0.5, 0.3),
                model_scale=(1, 1.5, 1)
            ),
            
            TerrainType.MOUNTAINS: TerrainTile(
                terrain_type=TerrainType.MOUNTAINS,
                elevation=300.0,
                population_density=0.05,
                thermal_strength=1.2,
                wind_resistance=1.0,
                landmark_probability=0.4,
                color=(0.7, 0.7, 0.7),
                model_scale=(1, 3.0, 1)
            ),
            
            TerrainType.URBAN_LOW: TerrainTile(
                terrain_type=TerrainType.URBAN_LOW,
                elevation=15.0,
                population_density=0.6,
                thermal_strength=0.9,
                wind_resistance=0.7,
                landmark_probability=0.25,
                color=(0.6, 0.6, 0.6),
                model_scale=(1, 0.6, 1)
            ),
            
            TerrainType.URBAN_MED: TerrainTile(
                terrain_type=TerrainType.URBAN_MED,
                elevation=20.0,
                population_density=0.8,
                thermal_strength=1.1,
                wind_resistance=0.9,
                landmark_probability=0.35,
                color=(0.5, 0.5, 0.5),
                model_scale=(1, 1.0, 1)
            ),
            
            TerrainType.URBAN_HIGH: TerrainTile(
                terrain_type=TerrainType.URBAN_HIGH,
                elevation=25.0,
                population_density=1.0,
                thermal_strength=1.4,
                wind_resistance=1.2,
                landmark_probability=0.5,
                color=(0.4, 0.4, 0.4),
                model_scale=(1, 2.0, 1)
            ),
            
            TerrainType.FOREST: TerrainTile(
                terrain_type=TerrainType.FOREST,
                elevation=25.0,
                population_density=0.05,
                thermal_strength=0.4,
                wind_resistance=0.5,
                landmark_probability=0.1,
                color=(0.2, 0.5, 0.2),
                model_scale=(1, 0.8, 1)
            ),
            
            TerrainType.DESERT: TerrainTile(
                terrain_type=TerrainType.DESERT,
                elevation=30.0,
                population_density=0.02,
                thermal_strength=1.5,
                wind_resistance=0.3,
                landmark_probability=0.05,
                color=(0.8, 0.7, 0.4),
                model_scale=(1, 0.5, 1)
            ),
            
            TerrainType.BRIDGE: TerrainTile(
                terrain_type=TerrainType.BRIDGE,
                elevation=30.0,
                population_density=0.0,
                thermal_strength=0.5,
                wind_resistance=0.8,
                landmark_probability=1.0,
                color=(0.8, 0.4, 0.2),
                model_scale=(1, 1.2, 1)
            ),
            
            TerrainType.AIRPORT: TerrainTile(
                terrain_type=TerrainType.AIRPORT,
                elevation=12.0,
                population_density=0.3,
                thermal_strength=0.8,
                wind_resistance=0.2,
                landmark_probability=1.0,
                color=(0.3, 0.3, 0.3),
                model_scale=(1, 0.4, 1)
            ),
            
            TerrainType.LANDMARK: TerrainTile(
                terrain_type=TerrainType.LANDMARK,
                elevation=100.0,
                population_density=0.2,
                thermal_strength=0.7,
                wind_resistance=0.6,
                landmark_probability=1.0,
                color=(0.9, 0.8, 0.1),
                model_scale=(1, 4.0, 1)
            )
        }
        
        return tiles
    
    def define_adjacency_rules(self) -> Dict[TerrainType, Dict[str, Set[TerrainType]]]:
        """Define what terrain types can be adjacent to each other"""
        rules = {}
        
        # Water rules - logical water body formation
        rules[TerrainType.WATER_DEEP] = {
            'north': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW},
            'south': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW},
            'east': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW},
            'west': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW}
        }
        
        rules[TerrainType.WATER_SHALLOW] = {
            'north': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.BRIDGE},
            'south': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.BRIDGE},
            'east': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.BRIDGE},
            'west': {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.BRIDGE}
        }
        
        # Coastal transition rules - realistic shoreline
        rules[TerrainType.BEACH] = {
            'north': {TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.PLAINS, TerrainType.URBAN_LOW},
            'south': {TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.PLAINS, TerrainType.URBAN_LOW},
            'east': {TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.PLAINS, TerrainType.URBAN_LOW},
            'west': {TerrainType.WATER_SHALLOW, TerrainType.BEACH, TerrainType.PLAINS, TerrainType.URBAN_LOW}
        }
        
        # Land elevation progression rules - realistic topography
        rules[TerrainType.PLAINS] = {
            'north': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.FOREST, 
                     TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'south': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.FOREST, 
                     TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'east': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.FOREST, 
                     TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'west': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.FOREST, 
                     TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.AIRPORT}
        }
        
        rules[TerrainType.HILLS_LOW] = {
            'north': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST, TerrainType.URBAN_LOW},
            'south': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST, TerrainType.URBAN_LOW},
            'east': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST, TerrainType.URBAN_LOW},
            'west': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST, TerrainType.URBAN_LOW}
        }
        
        rules[TerrainType.HILLS_HIGH] = {
            'north': {TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.FOREST, TerrainType.LANDMARK},
            'south': {TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.FOREST, TerrainType.LANDMARK},
            'east': {TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.FOREST, TerrainType.LANDMARK},
            'west': {TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.FOREST, TerrainType.LANDMARK}
        }
        
        rules[TerrainType.MOUNTAINS] = {
            'north': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.LANDMARK},
            'south': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.LANDMARK},
            'east': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.LANDMARK},
            'west': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.LANDMARK}
        }
        
        # Urban development rules - realistic city growth
        rules[TerrainType.URBAN_LOW] = {
            'north': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.URBAN_LOW, 
                     TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'south': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.URBAN_LOW, 
                     TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'east': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.URBAN_LOW, 
                     TerrainType.URBAN_MED, TerrainType.AIRPORT},
            'west': {TerrainType.BEACH, TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.URBAN_LOW, 
                     TerrainType.URBAN_MED, TerrainType.AIRPORT}
        }
        
        rules[TerrainType.URBAN_MED] = {
            'north': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.URBAN_HIGH},
            'south': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.URBAN_HIGH},
            'east': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.URBAN_HIGH},
            'west': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.URBAN_MED, TerrainType.URBAN_HIGH}
        }
        
        rules[TerrainType.URBAN_HIGH] = {
            'north': {TerrainType.URBAN_MED, TerrainType.URBAN_HIGH, TerrainType.LANDMARK},
            'south': {TerrainType.URBAN_MED, TerrainType.URBAN_HIGH, TerrainType.LANDMARK},
            'east': {TerrainType.URBAN_MED, TerrainType.URBAN_HIGH, TerrainType.LANDMARK},
            'west': {TerrainType.URBAN_MED, TerrainType.URBAN_HIGH, TerrainType.LANDMARK}
        }
        
        # Special feature rules
        rules[TerrainType.FOREST] = {
            'north': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST},
            'south': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST},
            'east': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST},
            'west': {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.HILLS_HIGH, TerrainType.FOREST}
        }
        
        rules[TerrainType.DESERT] = {
            'north': {TerrainType.PLAINS, TerrainType.DESERT, TerrainType.HILLS_LOW},
            'south': {TerrainType.PLAINS, TerrainType.DESERT, TerrainType.HILLS_LOW},
            'east': {TerrainType.PLAINS, TerrainType.DESERT, TerrainType.HILLS_LOW},
            'west': {TerrainType.PLAINS, TerrainType.DESERT, TerrainType.HILLS_LOW}
        }
        
        # Infrastructure rules
        rules[TerrainType.BRIDGE] = {
            'north': {TerrainType.WATER_SHALLOW, TerrainType.URBAN_LOW, TerrainType.URBAN_MED},
            'south': {TerrainType.WATER_SHALLOW, TerrainType.URBAN_LOW, TerrainType.URBAN_MED},
            'east': {TerrainType.WATER_SHALLOW, TerrainType.URBAN_LOW, TerrainType.URBAN_MED},
            'west': {TerrainType.WATER_SHALLOW, TerrainType.URBAN_LOW, TerrainType.URBAN_MED}
        }
        
        rules[TerrainType.AIRPORT] = {
            'north': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.DESERT},
            'south': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.DESERT},
            'east': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.DESERT},
            'west': {TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.DESERT}
        }
        
        rules[TerrainType.LANDMARK] = {
            'north': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.URBAN_HIGH},
            'south': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.URBAN_HIGH},
            'east': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.URBAN_HIGH},
            'west': {TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, TerrainType.URBAN_HIGH}
        }
        
        return rules
    
    def get_chunk_coordinates(self, world_x: float, world_z: float) -> Tuple[int, int]:
        """Convert world coordinates to chunk coordinates"""
        chunk_x = int(world_x // (self.chunk_size * 10))  # Each chunk is 10x10 world units
        chunk_z = int(world_z // (self.chunk_size * 10))
        return (chunk_x, chunk_z)
    
    def get_tile_coordinates(self, world_x: float, world_z: float) -> Tuple[int, int]:
        """Convert world coordinates to tile coordinates within a chunk"""
        tile_x = int((world_x % (self.chunk_size * 10)) // 10)
        tile_z = int((world_z % (self.chunk_size * 10)) // 10)
        return (tile_x, tile_z)
    
    def initialize_chunk(self, chunk_x: int, chunk_z: int):
        """Initialize a new chunk with all possibilities"""
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key in self.world_chunks:
            return
        
        # Initialize all positions in chunk with all possibilities
        for local_x in range(self.chunk_size):
            for local_z in range(self.chunk_size):
                global_x = chunk_x * self.chunk_size + local_x
                global_z = chunk_z * self.chunk_size + local_z
                pos_key = (global_x, global_z)
                
                # Start with all terrain types possible
                self.possible_states[pos_key] = set(self.tile_types.keys())
        
        # Apply biome-based constraints based on chunk position
        self.apply_biome_constraints(chunk_x, chunk_z)
        
        # Start collapse process for this chunk
        self.collapse_chunk(chunk_x, chunk_z)
        
        self.world_chunks[chunk_key] = True
        print(f"🌍 Generated chunk ({chunk_x}, {chunk_z})")
    
    def apply_biome_constraints(self, chunk_x: int, chunk_z: int):
        """Apply biome-based constraints to chunk generation"""
        # Create logical biome distribution
        biome_noise_x = chunk_x * 0.1
        biome_noise_z = chunk_z * 0.1
        
        # Distance from origin affects terrain type
        distance_from_origin = math.sqrt(chunk_x**2 + chunk_z**2)
        
        # Ocean probability increases with distance
        ocean_probability = min(0.8, distance_from_origin * 0.05)
        
        # Mountain probability based on noise
        mountain_noise = (math.sin(biome_noise_x * 2) + math.cos(biome_noise_z * 3)) / 2
        mountain_probability = max(0, mountain_noise * 0.3)
        
        # Urban probability decreases with distance
        urban_probability = max(0.1, 0.6 - distance_from_origin * 0.02)
        
        for local_x in range(self.chunk_size):
            for local_z in range(self.chunk_size):
                global_x = chunk_x * self.chunk_size + local_x
                global_z = chunk_z * self.chunk_size + local_z
                pos_key = (global_x, global_z)
                
                # Apply biome constraints
                if random.random() < ocean_probability:
                    # Ocean biome - remove land types
                    self.possible_states[pos_key] &= {
                        TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW, 
                        TerrainType.BEACH, TerrainType.BRIDGE
                    }
                elif random.random() < mountain_probability:
                    # Mountain biome - prefer elevated terrain
                    self.possible_states[pos_key] &= {
                        TerrainType.HILLS_HIGH, TerrainType.MOUNTAINS, 
                        TerrainType.FOREST, TerrainType.LANDMARK
                    }
                elif random.random() < urban_probability:
                    # Urban biome - prefer developed areas
                    self.possible_states[pos_key] &= {
                        TerrainType.PLAINS, TerrainType.URBAN_LOW, TerrainType.URBAN_MED, 
                        TerrainType.URBAN_HIGH, TerrainType.AIRPORT, TerrainType.LANDMARK
                    }
    
    def collapse_chunk(self, chunk_x: int, chunk_z: int):
        """Collapse an entire chunk using WFC algorithm"""
        # Find position with minimum entropy (fewest possibilities)
        while True:
            min_entropy_pos = self.find_minimum_entropy_position(chunk_x, chunk_z)
            
            if min_entropy_pos is None:
                break  # All positions collapsed
            
            # Collapse the minimum entropy position
            self.collapse_position(min_entropy_pos)
            
            # Propagate constraints
            self.propagate_constraints()
    
    def find_minimum_entropy_position(self, chunk_x: int, chunk_z: int) -> Optional[Tuple[int, int]]:
        """Find position with minimum entropy (fewest possibilities) in chunk"""
        min_entropy = float('inf')
        min_pos = None
        
        for local_x in range(self.chunk_size):
            for local_z in range(self.chunk_size):
                global_x = chunk_x * self.chunk_size + local_x
                global_z = chunk_z * self.chunk_size + local_z
                pos_key = (global_x, global_z)
                
                if pos_key in self.collapsed_tiles:
                    continue  # Already collapsed
                
                entropy = len(self.possible_states.get(pos_key, set()))
                
                if entropy == 0:
                    print(f"⚠️ Contradiction at position {pos_key}!")
                    # Handle contradiction by resetting
                    self.possible_states[pos_key] = {TerrainType.PLAINS}
                    entropy = 1
                
                if entropy < min_entropy and entropy > 0:
                    min_entropy = entropy
                    min_pos = pos_key
        
        return min_pos
    
    def collapse_position(self, position: Tuple[int, int]):
        """Collapse a position to a single state"""
        possible = list(self.possible_states.get(position, {TerrainType.PLAINS}))
        
        if not possible:
            chosen = TerrainType.PLAINS
        else:
            # Weight choices based on terrain properties
            weights = []
            for terrain_type in possible:
                tile = self.tile_types[terrain_type]
                # Prefer more common terrain types
                weight = 1.0
                
                if terrain_type in {TerrainType.PLAINS, TerrainType.HILLS_LOW, TerrainType.FOREST}:
                    weight = 3.0  # Common terrain
                elif terrain_type in {TerrainType.URBAN_LOW, TerrainType.WATER_SHALLOW}:
                    weight = 2.0  # Moderately common
                elif terrain_type in {TerrainType.LANDMARK, TerrainType.AIRPORT, TerrainType.BRIDGE}:
                    weight = 0.1  # Very rare
                
                weights.append(weight)
            
            chosen = random.choices(possible, weights=weights)[0]
        
        # Collapse to chosen state
        self.collapsed_tiles[position] = chosen
        self.possible_states[position] = {chosen}
        
        # Add neighbors to propagation queue
        x, z = position
        neighbors = [(x+1, z), (x-1, z), (x, z+1), (x, z-1)]
        
        for neighbor in neighbors:
            if neighbor not in self.collapsed_tiles:
                self.propagation_queue.append((position, neighbor))
    
    def propagate_constraints(self):
        """Propagate constraints using adjacency rules"""
        while self.propagation_queue:
            source_pos, target_pos = self.propagation_queue.popleft()
            
            if target_pos in self.collapsed_tiles:
                continue  # Target already collapsed
            
            # Determine direction
            dx = target_pos[0] - source_pos[0]
            dz = target_pos[1] - source_pos[1]
            
            if dx == 1:
                direction = 'east'
            elif dx == -1:
                direction = 'west'
            elif dz == 1:
                direction = 'north'
            elif dz == -1:
                direction = 'south'
            else:
                continue  # Not adjacent
            
            # Get source terrain type
            source_terrain = list(self.possible_states[source_pos])[0]
            
            # Get allowed adjacent types
            allowed_types = self.adjacency_rules.get(source_terrain, {}).get(direction, set())
            
            # Filter target possibilities
            old_possibilities = self.possible_states.get(target_pos, set())
            new_possibilities = old_possibilities & allowed_types
            
            if new_possibilities != old_possibilities:
                self.possible_states[target_pos] = new_possibilities
                
                # Add target's neighbors to queue if possibilities changed
                tx, tz = target_pos
                target_neighbors = [(tx+1, tz), (tx-1, tz), (tx, tz+1), (tx, tz-1)]
                
                for neighbor in target_neighbors:
                    if neighbor not in self.collapsed_tiles and neighbor != source_pos:
                        self.propagation_queue.append((target_pos, neighbor))
    
    def get_terrain_at_position(self, world_x: float, world_z: float) -> TerrainTile:
        """Get terrain type at world position"""
        chunk_x, chunk_z = self.get_chunk_coordinates(world_x, world_z)
        
        # Ensure chunk is generated
        if (chunk_x, chunk_z) not in self.world_chunks:
            self.initialize_chunk(chunk_x, chunk_z)
        
        # Get tile coordinates within chunk
        tile_x = int(world_x // 10)
        tile_z = int(world_z // 10)
        pos_key = (tile_x, tile_z)
        
        # Return terrain type
        terrain_type = self.collapsed_tiles.get(pos_key, TerrainType.PLAINS)
        return self.tile_types[terrain_type]
    
    def update_active_chunks(self, player_position: Vec3):
        """Update which chunks are active based on player position"""
        player_chunk_x, player_chunk_z = self.get_chunk_coordinates(player_position.x, player_position.z)
        
        new_active_chunks = set()
        
        # Load chunks around player
        for dx in range(-self.chunk_load_radius, self.chunk_load_radius + 1):
            for dz in range(-self.chunk_load_radius, self.chunk_load_radius + 1):
                chunk_x = player_chunk_x + dx
                chunk_z = player_chunk_z + dz
                chunk_key = (chunk_x, chunk_z)
                
                new_active_chunks.add(chunk_key)
                
                # Generate chunk if it doesn't exist
                if chunk_key not in self.world_chunks:
                    self.initialize_chunk(chunk_x, chunk_z)
        
        # Unload distant chunks (optional - for memory management)
        chunks_to_unload = self.active_chunks - new_active_chunks
        
        self.active_chunks = new_active_chunks
        
        return len(chunks_to_unload) > 0  # Return True if chunks were unloaded

class InfiniteWorldRenderer:
    """Renders the infinite world generated by WFC"""
    
    def __init__(self, wfc_generator: WaveFunctionCollapse):
        self.wfc = wfc_generator
        self.rendered_chunks = {}
        self.chunk_entities = {}
        self.tile_size = 10
        
        print("🎨 Infinite World Renderer initialized")
    
    def render_chunk(self, chunk_x: int, chunk_z: int):
        """Render a specific chunk"""
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key in self.rendered_chunks:
            return  # Already rendered
        
        chunk_entity = Entity(
            name=f"chunk_{chunk_x}_{chunk_z}",
            parent=scene
        )
        
        # Render each tile in the chunk
        for local_x in range(self.wfc.chunk_size):
            for local_z in range(self.wfc.chunk_size):
                global_x = chunk_x * self.wfc.chunk_size + local_x
                global_z = chunk_z * self.wfc.chunk_size + local_z
                
                world_x = global_x * self.tile_size
                world_z = global_z * self.tile_size
                
                terrain_tile = self.wfc.get_terrain_at_position(world_x, world_z)
                
                # Create tile entity
                tile_entity = Entity(
                    parent=chunk_entity,
                    model='cube',
                    color=color.rgb(*terrain_tile.color),
                    position=(world_x, terrain_tile.elevation, world_z),
                    scale=(self.tile_size * terrain_tile.model_scale[0],
                          terrain_tile.elevation * terrain_tile.model_scale[1] + 2,
                          self.tile_size * terrain_tile.model_scale[2])
                )
                
                # Add special features for certain terrain types
                self.add_terrain_features(tile_entity, terrain_tile, world_x, world_z)
        
        self.rendered_chunks[chunk_key] = True
        self.chunk_entities[chunk_key] = chunk_entity
        
        print(f"🎨 Rendered chunk ({chunk_x}, {chunk_z})")
    
    def add_terrain_features(self, tile_entity: Entity, terrain_tile: TerrainTile, world_x: float, world_z: float):
        """Add special features to terrain tiles"""
        if terrain_tile.terrain_type == TerrainType.FOREST:
            # Add trees
            for _ in range(random.randint(1, 4)):
                tree = Entity(
                    parent=tile_entity,
                    model='cube',
                    color=color.rgb(0.1, 0.4, 0.1),
                    position=(random.uniform(-4, 4), 8, random.uniform(-4, 4)),
                    scale=(1, 16, 1)
                )
        
        elif terrain_tile.terrain_type == TerrainType.URBAN_HIGH:
            # Add skyscrapers
            for _ in range(random.randint(2, 5)):
                building = Entity(
                    parent=tile_entity,
                    model='cube',
                    color=color.rgb(0.3, 0.3, 0.3),
                    position=(random.uniform(-3, 3), random.uniform(20, 80), random.uniform(-3, 3)),
                    scale=(random.uniform(2, 4), random.uniform(40, 160), random.uniform(2, 4))
                )
        
        elif terrain_tile.terrain_type == TerrainType.LANDMARK:
            # Add landmark structure
            landmark = Entity(
                parent=tile_entity,
                model='cube',
                color=color.rgb(0.9, 0.8, 0.1),
                position=(0, 50, 0),
                scale=(6, 100, 6)
            )
        
        elif terrain_tile.terrain_type == TerrainType.AIRPORT:
            # Add runway
            runway = Entity(
                parent=tile_entity,
                model='cube',
                color=color.rgb(0.2, 0.2, 0.2),
                position=(0, 1, 0),
                scale=(8, 0.2, 40)
            )
        
        elif terrain_tile.terrain_type == TerrainType.BRIDGE:
            # Add bridge structure
            bridge_deck = Entity(
                parent=tile_entity,
                model='cube',
                color=color.rgb(0.8, 0.4, 0.2),
                position=(0, 5, 0),
                scale=(8, 1, 40)
            )
            
            # Bridge towers
            for tower_z in [-15, 15]:
                tower = Entity(
                    parent=tile_entity,
                    model='cube',
                    color=color.rgb(0.8, 0.4, 0.2),
                    position=(0, 25, tower_z),
                    scale=(3, 50, 3)
                )
    
    def unload_chunk(self, chunk_x: int, chunk_z: int):
        """Unload and destroy a chunk's entities"""
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key in self.chunk_entities:
            destroy(self.chunk_entities[chunk_key])
            del self.chunk_entities[chunk_key]
            del self.rendered_chunks[chunk_key]
            print(f"🗑️ Unloaded chunk ({chunk_x}, {chunk_z})")
    
    def update(self, player_position: Vec3):
        """Update rendered chunks based on player position"""
        # Update WFC active chunks
        chunks_changed = self.wfc.update_active_chunks(player_position)
        
        # Render new active chunks
        for chunk_key in self.wfc.active_chunks:
            if chunk_key not in self.rendered_chunks:
                self.render_chunk(chunk_key[0], chunk_key[1])
        
        # Unload distant chunks
        player_chunk_x, player_chunk_z = self.wfc.get_chunk_coordinates(player_position.x, player_position.z)
        load_radius_squared = (self.wfc.chunk_load_radius + 1) ** 2
        
        chunks_to_unload = []
        for chunk_key in list(self.rendered_chunks.keys()):
            chunk_x, chunk_z = chunk_key
            distance_squared = (chunk_x - player_chunk_x)**2 + (chunk_z - player_chunk_z)**2
            
            if distance_squared > load_radius_squared:
                chunks_to_unload.append(chunk_key)
        
        for chunk_key in chunks_to_unload:
            self.unload_chunk(chunk_key[0], chunk_key[1])
    
    def get_terrain_effects_at_position(self, position: Vec3) -> Dict:
        """Get terrain-based effects at position"""
        terrain_tile = self.wfc.get_terrain_at_position(position.x, position.z)
        
        return {
            'thermal_strength': terrain_tile.thermal_strength,
            'wind_resistance': terrain_tile.wind_resistance,
            'elevation': terrain_tile.elevation,
            'population_density': terrain_tile.population_density,
            'terrain_type': terrain_tile.terrain_type.value
        }

# Flight Corridor System using WFC principles
class FlightCorridorManager:
    """Manages flight corridors and airspace using WFC logic"""
    
    def __init__(self, wfc_generator: WaveFunctionCollapse):
        self.wfc = wfc_generator
        self.flight_corridors = {}
        self.restricted_zones = {}
        self.navigation_aids = {}
        
        print("✈️ Flight Corridor Manager initialized")
    
    def generate_flight_corridors(self, chunk_x: int, chunk_z: int):
        """Generate flight corridors for a chunk based on terrain"""
        chunk_key = (chunk_x, chunk_z)
        
        if chunk_key in self.flight_corridors:
            return
        
        corridors = []
        
        # Analyze terrain in chunk
        for local_x in range(0, self.wfc.chunk_size, 4):  # Sample every 4th tile
            for local_z in range(0, self.wfc.chunk_size, 4):
                global_x = chunk_x * self.wfc.chunk_size + local_x
                global_z = chunk_z * self.wfc.chunk_size + local_z
                
                world_x = global_x * 10
                world_z = global_z * 10
                
                terrain_tile = self.wfc.get_terrain_at_position(world_x, world_z)
                
                # Create corridors based on terrain
                if terrain_tile.terrain_type in {TerrainType.URBAN_HIGH, TerrainType.LANDMARK}:
                    # High altitude corridor over cities
                    corridors.append({
                        'position': Vec3(world_x, terrain_tile.elevation + 100, world_z),
                        'type': 'high_altitude',
                        'min_altitude': terrain_tile.elevation + 80,
                        'max_altitude': terrain_tile.elevation + 200,
                        'width': 50
                    })
                
                elif terrain_tile.terrain_type == TerrainType.AIRPORT:
                    # Approach corridors for airports
                    corridors.append({
                        'position': Vec3(world_x, terrain_tile.elevation + 20, world_z),
                        'type': 'approach',
                        'min_altitude': terrain_tile.elevation + 5,
                        'max_altitude': terrain_tile.elevation + 50,
                        'width': 30
                    })
                
                elif terrain_tile.terrain_type in {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW}:
                    # Low altitude scenic routes over water
                    corridors.append({
                        'position': Vec3(world_x, terrain_tile.elevation + 30, world_z),
                        'type': 'scenic',
                        'min_altitude': terrain_tile.elevation + 10,
                        'max_altitude': terrain_tile.elevation + 60,
                        'width': 40
                    })
        
        self.flight_corridors[chunk_key] = corridors
    
    def get_recommended_altitude(self, position: Vec3) -> float:
        """Get recommended flight altitude at position"""
        terrain_tile = self.wfc.get_terrain_at_position(position.x, position.z)
        
        # Base altitude on terrain type
        if terrain_tile.terrain_type == TerrainType.MOUNTAINS:
            return terrain_tile.elevation + 150
        elif terrain_tile.terrain_type in {TerrainType.URBAN_HIGH, TerrainType.LANDMARK}:
            return terrain_tile.elevation + 100
        elif terrain_tile.terrain_type in {TerrainType.HILLS_HIGH, TerrainType.URBAN_MED}:
            return terrain_tile.elevation + 80
        elif terrain_tile.terrain_type in {TerrainType.WATER_DEEP, TerrainType.WATER_SHALLOW}:
            return terrain_tile.elevation + 30
        else:
            return terrain_tile.elevation + 50
    
    def check_airspace_restrictions(self, position: Vec3) -> List[str]:
        """Check for airspace restrictions at position"""
        warnings = []
        terrain_tile = self.wfc.get_terrain_at_position(position.x, position.z)
        
        # Height restrictions
        min_safe_altitude = terrain_tile.elevation + 20
        if position.y < min_safe_altitude:
            warnings.append('LOW_ALTITUDE_WARNING')
        
        # Terrain-specific restrictions
        if terrain_tile.terrain_type == TerrainType.AIRPORT:
            if 10 < position.y < 100:
                warnings.append('AIRPORT_AIRSPACE')
        
        elif terrain_tile.terrain_type == TerrainType.URBAN_HIGH:
            if position.y < terrain_tile.elevation + 50:
                warnings.append('URBAN_FLYOVER_RESTRICTION')
        
        elif terrain_tile.terrain_type == TerrainType.MOUNTAINS:
            if position.y < terrain_tile.elevation + 100:
                warnings.append('MOUNTAIN_WAVE_TURBULENCE')
        
        return warnings 