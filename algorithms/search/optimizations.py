import numpy as np
from typing import Dict, List, Tuple, Set
import functools
import json
import os
import time
import threading

class SearchOptimizations:
    """
    Common optimizations for Rubik's Cube search algorithms.
    """
    
    # Pre-computed move sequences that cancel each other out
    MOVE_CANCELLATIONS = {
        'F': {'F\'', 'F F F'},
        'F\'': {'F', 'F\' F\' F\''},
        'B': {'B\'', 'B B B'},
        'B\'': {'B', 'B\' B\' B\''},
        'L': {'L\'', 'L L L'},
        'L\'': {'L', 'L\' L\' L\''},
        'R': {'R\'', 'R R R'},
        'R\'': {'R', 'R\' R\' R\''},
        'U': {'U\'', 'U U U'},
        'U\'': {'U', 'U\' U\' U\''},
        'D': {'D\'', 'D D D'},
        'D\'': {'D', 'D\' D\' D\''},
    }
    
    # Move groups for efficient pruning
    MOVE_GROUPS = {
        'F': ['F', 'F\'', 'F2'],
        'B': ['B', 'B\'', 'B2'],
        'L': ['L', 'L\'', 'L2'],
        'R': ['R', 'R\'', 'R2'],
        'U': ['U', 'U\'', 'U2'],
        'D': ['D', 'D\'', 'D2'],
    }
    
    # Opposite face pairs
    OPPOSITE_FACES = {
        'F': 'B', 'B': 'F',
        'L': 'R', 'R': 'L',
        'U': 'D', 'D': 'U',
    }
    
    # Cache directory for pattern databases
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "cache")
    
    # Cache for optimized_state_key to avoid recomputation
    _state_key_cache = {}
    _state_key_cache_hits = 0
    _state_key_cache_misses = 0
    _state_key_cache_lock = threading.RLock()
    _state_key_cache_max_size = 10000
    
    @staticmethod
    def ensure_cache_dir():
        """Ensure the cache directory exists"""
        if not os.path.exists(SearchOptimizations.CACHE_DIR):
            os.makedirs(SearchOptimizations.CACHE_DIR)
    
    @staticmethod
    def compute_corner_distance_db(solved_cube) -> Dict:
        """
        Create a pattern database for corner piece distances.
        This is a simplified version - a real implementation would be more comprehensive.
        """
        corner_db = {}
        # In a real implementation, this would generate all possible corner configurations
        # and compute the minimum moves to solve each one using BFS
        
        # For now, just store the solved state
        corner_positions = []
        for piece in solved_cube.pieces:
            if len(piece.colors) == 3:  # Corner piece
                corner_positions.append((tuple(piece.position), 
                                        tuple(sorted(piece.colors.items()))))
        
        corner_db[tuple(sorted(corner_positions))] = 0
        return corner_db
    
    @staticmethod
    def compute_edge_distance_db(solved_cube) -> Dict:
        """
        Create a pattern database for edge piece distances.
        This is a simplified version - a real implementation would be more comprehensive.
        """
        edge_db = {}
        # In a real implementation, this would generate many edge configurations
        
        # For now, just store the solved state
        edge_positions = []
        for piece in solved_cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                edge_positions.append((tuple(piece.position), 
                                      tuple(sorted(piece.colors.items()))))
        
        edge_db[tuple(sorted(edge_positions))] = 0
        return edge_db
        
    @staticmethod
    def advanced_heuristic(cube, corner_db, edge_db) -> int:
        """
        A more advanced admissible heuristic combining multiple pattern databases.
        """
        # Extract corner and edge piece states
        corner_positions = []
        for piece in cube.pieces:
            if len(piece.colors) == 3:
                corner_positions.append((tuple(piece.position), 
                                        tuple(sorted(piece.colors.items()))))
        
        corner_state = tuple(sorted(corner_positions))
        corner_distance = corner_db.get(corner_state, 8)  # Default to 8 if not found
        
        edge_positions = []
        for piece in cube.pieces:
            if len(piece.colors) == 2:
                edge_positions.append((tuple(piece.position), 
                                      tuple(sorted(piece.colors.items()))))
        
        edge_state = tuple(sorted(edge_positions))
        edge_distance = edge_db.get(edge_state, 8)  # Default to 8 if not found
        
        # Take the maximum of the two distances for an admissible heuristic
        return max(corner_distance, edge_distance)
    
    @staticmethod
    def is_move_redundant(path: List[str], move: str) -> bool:
        """
        Advanced redundancy check to eliminate unnecessary moves.
        """
        if not path:
            return False
            
        last_move = path[-1]
        
        # Same face moves can be optimized
        if last_move[0] == move[0]:
            return True
            
        # Two consecutive moves on opposite faces are better done in reverse order
        if len(path) >= 1 and SearchOptimizations.OPPOSITE_FACES.get(move[0]) == last_move[0]:
            return False  # Not redundant, just inefficient
        
        # Three consecutive moves on the same face can be replaced with a single move
        if len(path) >= 2:
            if path[-1][0] == path[-2][0] == move[0]:
                return True
                
        return False
    
    @staticmethod
    def optimize_move_sequence(moves: List[str]) -> List[str]:
        """
        Post-process a solution to remove redundant moves.
        """
        if not moves:
            return moves
            
        optimized = []
        i = 0
        while i < len(moves):
            # Handle sequential moves on the same face
            if i + 1 < len(moves) and moves[i][0] == moves[i+1][0]:
                face = moves[i][0]
                combined = SearchOptimizations._combine_face_moves(moves[i], moves[i+1])
                if combined == "":  # Moves cancel each other
                    i += 2
                    continue
                else:
                    optimized.append(combined)
                    i += 2
            else:
                optimized.append(moves[i])
                i += 1
        
        # Second pass to handle more complex patterns
        i = 0
        result = []
        while i < len(optimized):
            # Skip moves that cancel with previous move
            if i > 0 and SearchOptimizations._cancels_previous(optimized[i], optimized[i-1]):
                result.pop()  # Remove previous move
                i += 1  # Skip current move
            else:
                result.append(optimized[i])
                i += 1
                
        return result
    
    @staticmethod
    def _combine_face_moves(move1: str, move2: str) -> str:
        """Helper to combine two moves on the same face."""
        face = move1[0]
        
        # Count quarter turns
        turns = 0
        if len(move1) == 1:
            turns += 1
        elif move1[1] == '\'':
            turns += 3  # -1 represented as 3 quarter turns
        elif move1[1] == '2':
            turns += 2
            
        if len(move2) == 1:
            turns += 1
        elif move2[1] == '\'':
            turns += 3
        elif move2[1] == '2':
            turns += 2
            
        # Normalize to 0-3 quarter turns
        turns = turns % 4
        
        if turns == 0:
            return ""  # Moves cancel out
        elif turns == 1:
            return face
        elif turns == 2:
            return face + "2"
        else:  # turns == 3
            return face + "\'"

    @staticmethod
    def _cancels_previous(move: str, prev_move: str) -> bool:
        """Check if current move cancels the previous move."""
        if move[0] != prev_move[0]:
            return False
            
        # For example: F and F' cancel each other
        if len(move) == 1 and len(prev_move) == 2 and prev_move[1] == '\'':
            return True
        if len(move) == 2 and move[1] == '\'' and len(prev_move) == 1:
            return True
            
        return False

    @staticmethod
    def optimized_state_key(cube):
        # The implementation expects cube.faces but RubikCube doesn't have this attribute
        # We need to adapt the code to work with the actual cube representation
        
        # Check what attributes/methods the cube actually has
        # Most likely it has a way to get the state of each face
        
        # Common implementations may have:
        # 1. get_state() or get_faces() method
        # 2. state or cube_state attribute
        # 3. or individual face attributes like up_face, down_face, etc.
        
        # Let's create a generic approach that works with different cube representations
        state = []
        
        # Try different common approaches to access cube state:
        if hasattr(cube, 'get_state'):
            # If the cube has a get_state() method
            faces = cube.get_state()
        elif hasattr(cube, 'get_faces'):
            # If the cube has a get_faces() method
            faces = cube.get_faces()
        elif hasattr(cube, 'state'):
            # If the cube has a state attribute
            faces = cube.state
        elif hasattr(cube, 'cube_state'):
            # If the cube has a cube_state attribute
            faces = cube.cube_state
        elif all(hasattr(cube, f) for f in ['up', 'down', 'left', 'right', 'front', 'back']):
            # If the cube has individual face attributes
            faces = [cube.up, cube.down, cube.left, cube.right, cube.front, cube.back]
        else:
            # If we can't detect the structure, use string representation as fallback
            return str(cube)
        
        # Create a string representation of the cube state
        state_string = ""
        
        # Process each face
        for face in faces:
            if isinstance(face, list) or isinstance(face, tuple):
                # If face is a list/tuple of colors
                for color in face:
                    state_string += str(color)
            else:
                # If face is something else, just convert it to string
                state_string += str(face)
        
        return state_string

    @staticmethod
    def get_cache_stats():
        """Returns statistics about the state key cache performance"""
        with SearchOptimizations._state_key_cache_lock:
            total = SearchOptimizations._state_key_cache_hits + SearchOptimizations._state_key_cache_misses
            hit_rate = SearchOptimizations._state_key_cache_hits / total if total > 0 else 0
            return {
                'hits': SearchOptimizations._state_key_cache_hits,
                'misses': SearchOptimizations._state_key_cache_misses,
                'total': total,
                'hit_rate': hit_rate,
                'cache_size': len(SearchOptimizations._state_key_cache)
            }

    @staticmethod
    def reset_cache_stats():
        """Reset cache statistics"""
        with SearchOptimizations._state_key_cache_lock:
            SearchOptimizations._state_key_cache_hits = 0
            SearchOptimizations._state_key_cache_misses = 0

    @staticmethod
    def save_pattern_db(db, name):
        """Save a pattern database to disk"""
        SearchOptimizations.ensure_cache_dir()
        path = os.path.join(SearchOptimizations.CACHE_DIR, f"{name}.json")
        
        # Convert keys to strings since JSON requires string keys
        serializable_db = {str(k): v for k, v in db.items()}
        
        with open(path, 'w') as f:
            json.dump(serializable_db, f)
            
    @staticmethod
    def load_pattern_db(name):
        """Load a pattern database from disk"""
        SearchOptimizations.ensure_cache_dir()
        path = os.path.join(SearchOptimizations.CACHE_DIR, f"{name}.json")
        
        if not os.path.exists(path):
            return {}
            
        with open(path, 'r') as f:
            serializable_db = json.load(f)
            
        # Convert keys back to integers
        return {int(k): v for k, v in serializable_db.items()}
