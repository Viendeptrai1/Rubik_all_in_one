"""
Main Rubik's Cube solver module that imports and provides a unified interface
to both the 2x2 and 3x3 Rubik's cube solvers.
"""

from RubikState.rubik_chen import RubikState  
from RubikState.rubik_2x2 import Rubik2x2State

# Import specific solvers
from RubikState.rubik_solver_2x2 import solve_2x2, test_scramble_2x2, load_pattern_database, a_star_pdb_2x2
from RubikState.rubik_solver_3x3 import solve_3x3, test_scramble_3x3

# Import individual algorithm functions from 2x2 solver
from RubikState.rubik_solver_2x2 import (
    a_star_search_2x2,
    bfs_search_2x2,
    dfs_search_2x2,
    ucs_search_2x2,
    greedy_best_first_search_2x2,
    ids_search_2x2,
    ida_star_search_2x2,
    hill_climbing_max_search_2x2,
    hill_climbing_random_search_2x2
)

# Import individual algorithm functions from 3x3 solver
from RubikState.rubik_solver_3x3 import (
    a_star_search_3x3,
    bfs_search_3x3,
    dfs_search_3x3,
    ucs_search_3x3,
    greedy_best_first_search_3x3,
    ids_search_3x3,
    ida_star_search_3x3,
    hill_climbing_max_search_3x3,
    hill_climbing_random_search_3x3
)

# Load the pattern database for 2x2 cube
_pattern_database = None

def get_pattern_database():
    """Get or load the pattern database for 2x2 cube"""
    global _pattern_database
    if _pattern_database is None:
        _pattern_database = load_pattern_database()
    return _pattern_database

# Define wrapper functions for each algorithm to automatically detect cube type
def a_star(state, time_limit=30):
    """A* algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return a_star_search_2x2(state, time_limit=time_limit)
    return a_star_search_3x3(state, time_limit=time_limit)

def pdb_astar(state, time_limit=30):
    """Pattern Database A* algorithm for 2x2 Rubik's cube"""
    if isinstance(state, Rubik2x2State):
        pdb = get_pattern_database()
        return a_star_pdb_2x2(state, time_limit=time_limit, pdb=pdb)
    # For 3x3 cube, fall back to regular A*
    return a_star_search_3x3(state, time_limit=time_limit)

def bfs(state, time_limit=30):
    """BFS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return bfs_search_2x2(state, time_limit=time_limit)
    return bfs_search_3x3(state, time_limit=time_limit)

def dfs(state, time_limit=30):
    """DFS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return dfs_search_2x2(state, time_limit=time_limit)
    return dfs_search_3x3(state, time_limit=time_limit)

def ucs(state, time_limit=30):
    """UCS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ucs_search_2x2(state, time_limit=time_limit)
    return ucs_search_3x3(state, time_limit=time_limit)

def ids(state, time_limit=30):
    """IDS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ids_search_2x2(state, time_limit=time_limit)
    return ids_search_3x3(state, time_limit=time_limit)

def ida_star(state, time_limit=30):
    """IDA* algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ida_star_search_2x2(state, time_limit=time_limit)
    return ida_star_search_3x3(state, time_limit=time_limit)

def greedy_best_first(state, time_limit=30):
    """Greedy Best-First algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return greedy_best_first_search_2x2(state, time_limit=time_limit)
    return greedy_best_first_search_3x3(state, time_limit=time_limit)

def hill_climbing_max(state, time_limit=30):
    """Hill Climbing Max algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return hill_climbing_max_search_2x2(state, time_limit=time_limit)
    return hill_climbing_max_search_3x3(state, time_limit=time_limit)

def hill_climbing_random(state, time_limit=30):
    """Hill Climbing Random algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return hill_climbing_random_search_2x2(state, time_limit=time_limit)
    return hill_climbing_random_search_3x3(state, time_limit=time_limit)

def solve_rubik(start_state, algorithm="a_star", time_limit=30):
    """
    Unified solver for any type of Rubik's cube
    Automatically detects cube type and calls the appropriate solver
    
    Args:
        start_state: RubikState or Rubik2x2State
        algorithm: Name of algorithm to use
        time_limit: Time limit in seconds
        
    Returns:
        tuple: (solution_path, nodes_visited, time_taken)
    """
    if isinstance(start_state, Rubik2x2State):
        print("Detected 2x2 Rubik's cube")
        return solve_2x2(start_state, algorithm, time_limit)
    elif isinstance(start_state, RubikState):
        print("Detected 3x3 Rubik's cube")
        return solve_3x3(start_state, algorithm, time_limit)
    else:
        raise ValueError("Unsupported Rubik's cube state type")
        
def test_scramble(scramble_moves, cube_size=3, algorithm="a_star", time_limit=30):
    """
    Test solver with a specific scramble sequence
    
    Args:
        scramble_moves: List of move strings
        cube_size: Size of cube (2 or 3)
        algorithm: Algorithm to use
        time_limit: Time limit in seconds
        
    Returns:
        bool: True if solved successfully
    """
    if cube_size == 2:
        return test_scramble_2x2(scramble_moves, algorithm, time_limit)
    elif cube_size == 3:
        return test_scramble_3x3(scramble_moves, algorithm, time_limit)
    else:
        raise ValueError(f"Unsupported cube size: {cube_size}")
        
if __name__ == "__main__":
    # Simple test for both 2x2 and 3x3
    from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2
    from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3
    
    # Test 2x2
    print("\n===== TESTING 2x2 CUBE =====")
    scramble_2x2 = ["L", "U", "D'", "B'", "D'", "R'", "F", "L'", "R", "F", "L'", "B'"]
    state_2x2 = SOLVED_STATE_2x2.copy()
    for move in scramble_2x2:
        state_2x2 = state_2x2.apply_move(move, MOVES_2x2)
    
    # First try with PDB if available
    print("Testing with Pattern Database (PDB) algorithm:")
    test_scramble(scramble_2x2, cube_size=2, algorithm="pdb", time_limit=60)
    
    # Then with normal A*
    print("\nTesting with regular A* algorithm:")
    test_scramble(scramble_2x2, cube_size=2, algorithm="a_star", time_limit=60)
    
    # Test 3x3
    print("\n===== TESTING 3x3 CUBE =====")
    scramble_3x3 = ["R", "U", "R'", "U'", "F'", "L", "F"]
    test_scramble(scramble_3x3, cube_size=3, algorithm="a_star", time_limit=60)

