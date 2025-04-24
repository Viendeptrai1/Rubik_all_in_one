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
    hill_climbing_random_search_2x2,
    simulated_annealing_search_2x2,
    genetic_algorithm_search_2x2,
    local_beam_search_2x2,
    and_or_graph_search_2x2,
    belief_states_search_2x2,
    ac3_search_2x2,
    backtracking_search_strategy1_2x2,
    backtracking_search_strategy2_2x2
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
    hill_climbing_random_search_3x3,
    simulated_annealing_search_3x3,
    genetic_algorithm_search_3x3,
    local_beam_search_3x3,
    and_or_graph_search_3x3,
    belief_states_search_3x3,
    ac3_search_3x3,
    backtracking_search_strategy1_3x3,
    backtracking_search_strategy2_3x3
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
def a_star(state, time_limit=30, return_stats=False):
    """A* algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return a_star_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return a_star_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def pdb_astar(state, time_limit=30, return_stats=False):
    """Pattern Database A* algorithm for 2x2 Rubik's cube"""
    if isinstance(state, Rubik2x2State):
        pdb = get_pattern_database()
        return a_star_pdb_2x2(state, time_limit=time_limit, pdb=pdb, return_stats=return_stats)
    # For 3x3 cube, fall back to regular A*
    return a_star_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def bfs(state, time_limit=30, return_stats=False):
    """BFS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return bfs_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return bfs_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def dfs(state, time_limit=30, return_stats=False):
    """DFS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return dfs_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return dfs_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def ucs(state, time_limit=30, return_stats=False):
    """UCS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ucs_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return ucs_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def ids(state, time_limit=30, return_stats=False):
    """IDS algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ids_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return ids_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def ida_star(state, time_limit=30, return_stats=False):
    """IDA* algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ida_star_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return ida_star_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def greedy_best_first(state, time_limit=30, return_stats=False):
    """Greedy Best-First algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return greedy_best_first_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return greedy_best_first_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def hill_climbing_max(state, time_limit=30, return_stats=False):
    """Hill Climbing Max algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return hill_climbing_max_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return hill_climbing_max_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def hill_climbing_random(state, time_limit=30, return_stats=False):
    """Hill Climbing Random algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return hill_climbing_random_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return hill_climbing_random_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def simulated_annealing(state, time_limit=30, return_stats=False):
    """Simulated Annealing algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return simulated_annealing_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return simulated_annealing_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def genetic_algorithm(state, time_limit=30, return_stats=False):
    """Genetic Algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return genetic_algorithm_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return genetic_algorithm_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def local_beam_search(state, time_limit=30, return_stats=False):
    """Local Beam Search algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return local_beam_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return local_beam_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def and_or_graph_search(state, time_limit=30, return_stats=False):
    """AND-OR Graph Search algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return and_or_graph_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return and_or_graph_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def belief_states_search(state, time_limit=30, return_stats=False):
    """Belief States Search algorithm for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return belief_states_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return belief_states_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def ac3_search(state, time_limit=30, return_stats=False):
    """AC-3 (Arc Consistency Algorithm 3) for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return ac3_search_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return ac3_search_3x3(state, time_limit=time_limit, return_stats=return_stats)

def backtracking_search_strategy1(state, time_limit=30, return_stats=False):
    """Backtracking Search Strategy 1 for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return backtracking_search_strategy1_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return backtracking_search_strategy1_3x3(state, time_limit=time_limit, return_stats=return_stats)

def backtracking_search_strategy2(state, time_limit=30, return_stats=False):
    """Backtracking Search Strategy 2 for any Rubik's cube (auto detects type)"""
    if isinstance(state, Rubik2x2State):
        return backtracking_search_strategy2_2x2(state, time_limit=time_limit, return_stats=return_stats)
    return backtracking_search_strategy2_3x3(state, time_limit=time_limit, return_stats=return_stats)

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
