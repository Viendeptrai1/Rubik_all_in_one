"""
Rubik's Cube 3x3 Solver Module

This module provides implementations of various search algorithms
specifically optimized for solving the 3x3 Rubik's cube.
"""

import time
import random
import heapq
import os
import pickle
from collections import deque

# Import 3x3 specific classes and constants
from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVES_3x3, heuristic_3x3

def a_star_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    A* search algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    # Priority queue for A*: (f_value, state_hash, state, path)
    # Using state hash to avoid direct comparison of state objects
    h_value = heuristic_3x3(start_state)
    queue = [(h_value, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their g_values
    visited = {start_state: 0}  # state -> g_value

    start_time = time.time()
    while queue and time.time() - start_time < time_limit:
        f_value, _, state, path = heapq.heappop(queue)
        g_value = len(path)
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # If we already found a better path to this state, skip it
        if g_value > visited.get(state, float('inf')):
            continue

        for move in move_names:
            nodes_visited += 1
            new_state = state.apply_move(move, moves_dict)
            new_g_value = g_value + 1
            
            # Skip if we've seen this state with a shorter or equal path
            if new_state in visited and visited[new_state] <= new_g_value:
                continue
            
            # Update visited and add to frontier
            visited[new_state] = new_g_value
            h_score = heuristic_3x3(new_state)
            f_score = new_g_value + h_score
            heapq.heappush(queue, (f_score, hash(new_state), new_state, path + [move]))

    return None, nodes_visited, time.time() - start_time

def bfs_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    BFS algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    queue = deque([(start_state, [])])  # (state, path)
    visited = {start_state}
    
    start_time = time.time()
    while queue and time.time() - start_time < time_limit:
        state, path = queue.popleft()
        nodes_visited += 1
        
        if state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        for move in move_names:
            new_state = state.apply_move(move, moves_dict)
            
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [move]))
    
    end_time = time.time()
    return None, nodes_visited, end_time - start_time

def dfs_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=20):
    """
    DFS algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
        max_depth: Maximum search depth (default is 20)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    start_time = time.time()
    visited = set()
    node_count = 0
    
    def dfs_recursive(state, path, depth):
        nonlocal node_count
        
        if time.time() - start_time > time_limit:
            return None
        
        node_count += 1
        
        if state == goal_state:
            return path
        
        if depth >= max_depth:
            return None
        
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            if new_state not in visited:
                visited.add(new_state)
                result = dfs_recursive(new_state, path + [move], depth + 1)
                if result:
                    return result
                visited.remove(new_state)  # Backtrack
        
        return None
    
    visited.add(start_state)
    result = dfs_recursive(start_state, [], 0)
    
    return result, node_count, time.time() - start_time

def ucs_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Uniform Cost Search algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    # Count time
    start_time = time.time()
    nodes_visited = 0
    
    # Create priority queue with (cost, hash of state, state, path)
    queue = [(0, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their lowest costs
    visited = {start_state: 0}  # state -> cost
    
    while queue and time.time() - start_time < time_limit:
        cost, _, state, path = heapq.heappop(queue)
        nodes_visited += 1
        
        # If current state has higher cost than the best known state, skip
        if cost > visited.get(state, float('inf')):
            continue
            
        if state == goal_state:
            return path, nodes_visited, time.time() - start_time
            
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            new_cost = cost + 1
            
            # Only update if not visited or found a shorter path
            if new_state not in visited or new_cost < visited[new_state]:
                visited[new_state] = new_cost
                heapq.heappush(queue, (new_cost, hash(new_state), new_state, path + [move]))
    
    return None, nodes_visited, time.time() - start_time

def greedy_best_first_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    Greedy Best-First Search algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    start_time = time.time()
    
    # Create priority queue with (heuristic, hash of state, state, path)
    h = heuristic_3x3(start_state)
    queue = [(h, hash(start_state), start_state, [])]
    
    visited = set([start_state])
    node_count = 0
    
    while queue and time.time() - start_time < time_limit:
        _, _, state, path = heapq.heappop(queue)
        node_count += 1
        
        if state == goal_state:
            return path, node_count, time.time() - start_time
        
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            if new_state not in visited:
                visited.add(new_state)
                h = heuristic_3x3(new_state)
                heapq.heappush(queue, (h, hash(new_state), new_state, path + [move]))
    
    return None, node_count, time.time() - start_time

def ids_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_depth=20):
    """
    Iterative Deepening Search algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
        max_depth: Maximum search depth (default is 20)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    start_time = time.time()
    node_count = 0
    
    for depth in range(1, max_depth + 1):
        visited = set()
        visited.add(start_state)
        
        def dls(state, path, current_depth):
            nonlocal node_count
            
            if time.time() - start_time > time_limit:
                return None
            
            node_count += 1
            
            if state == goal_state:
                return path
            
            if current_depth == depth:
                return None
            
            for move in moves_dict:
                new_state = state.apply_move(move, moves_dict)
                if new_state not in visited:
                    visited.add(new_state)
                    result = dls(new_state, path + [move], current_depth + 1)
                    if result:
                        return result
                    visited.remove(new_state)  # Backtrack
            
            return None
        
        result = dls(start_state, [], 0)
        if result:
            return result, node_count, time.time() - start_time
        
        if time.time() - start_time > time_limit:
            break
    
    return None, node_count, time.time() - start_time

def ida_star_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30):
    """
    IDA* Search algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    start_time = time.time()
    visited_nodes = 0
    threshold = heuristic_3x3(start_state)
    
    while time.time() - start_time < time_limit:
        visited = set()
        path, found, new_threshold, nodes = _dfs_with_limit_3x3(
            start_state, goal_state, [], 0, threshold, visited, 
            moves_dict, start_time, time_limit
        )
        visited_nodes += nodes
        
        if found:
            return path, visited_nodes, time.time() - start_time
        
        if new_threshold == float('inf'):
            return None, visited_nodes, time.time() - start_time
        
        threshold = new_threshold
    
    return None, visited_nodes, time.time() - start_time

def _dfs_with_limit_3x3(state, goal_state, path, g, threshold, visited, moves_dict, start_time, time_limit):
    """
    Helper function for IDA* search for 3x3, performs depth-first search up to a limit
    
    Args:
        state: Current state
        goal_state: Target state
        path: Current path
        g: Current cost
        threshold: Current f-value threshold
        visited: Set of visited states
        moves_dict: Dictionary of moves
        start_time: Start time of the search
        time_limit: Time limit for the search
    
    Returns:
        tuple: (path, found, new_threshold, nodes_visited)
    """
    if time.time() - start_time >= time_limit:
        return None, False, float('inf'), 0
    
    if state == goal_state:
        return path, True, threshold, 1
    
    visited.add(state)
    nodes_visited = 1
    
    f = g + heuristic_3x3(state)
    if f > threshold:
        return None, False, f, nodes_visited
    
    min_threshold = float('inf')
    
    for move in moves_dict:
        new_state = state.apply_move(move, moves_dict)
        if new_state in visited:
            continue
            
        new_path, found, new_threshold, nodes = _dfs_with_limit_3x3(
            new_state, goal_state, path + [move], g + 1, threshold, visited.copy(), 
            moves_dict, start_time, time_limit
        )
        
        nodes_visited += nodes
        
        if found:
            return new_path, True, threshold, nodes_visited
            
        if new_threshold < min_threshold:
            min_threshold = new_threshold
    
    visited.remove(state)  # Backtrack
    return None, False, min_threshold, nodes_visited

def hill_climbing_max_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Hill Climbing Max algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    current_state = start_state
    current_h = heuristic_3x3(current_state)
    path = []
    
    start_time = time.time()
    
    # Iterate until goal is reached or no further improvement
    for iteration in range(max_iterations):
        if time.time() - start_time > time_limit:  # Check time limit first
            return None, nodes_visited, time.time() - start_time
            
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Find the best neighbor
        best_neighbor = None
        best_move = None
        best_h = current_h
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_3x3(neighbor)
            
            # Find neighbor with lowest heuristic (best)
            if neighbor_h < best_h:
                best_neighbor = neighbor
                best_move = move
                best_h = neighbor_h
        
        # If no improvement, end
        if best_neighbor is None:
            break
        
        # Move to the best state
        current_state = best_neighbor
        current_h = best_h
        path.append(best_move)
    
    # If goal is reached, return path
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # No path found
    return None, nodes_visited, time.time() - start_time

def hill_climbing_random_search_3x3(start_state, goal_state=None, moves_dict=None, time_limit=30, max_iterations=1000):
    """
    Hill Climbing Random algorithm for 3x3 Rubik's cube
    
    Args:
        start_state: Starting state (RubikState)
        goal_state: Goal state (default is SOLVED_STATE_3x3)
        moves_dict: Dictionary of moves (default is MOVES_3x3)
        time_limit: Time limit in seconds (default is 30)
        max_iterations: Maximum number of iterations (default is 1000)
    
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    # Set defaults if not provided
    goal_state = goal_state or SOLVED_STATE_3x3
    moves_dict = moves_dict or MOVES_3x3
    
    # Get list of move names
    move_names = list(moves_dict.keys())
    
    # Count visited nodes
    nodes_visited = 0
    
    current_state = start_state
    current_h = heuristic_3x3(current_state)
    path = []
    
    start_time = time.time()
    
    # Iterate until goal is reached or no further improvement
    for iteration in range(max_iterations):
        if time.time() - start_time > time_limit:  # Check time limit first
            return None, nodes_visited, time.time() - start_time
            
        if current_state == goal_state:
            end_time = time.time()
            return path, nodes_visited, end_time - start_time
        
        # Find all better neighbors
        better_neighbors = []
        
        for move in move_names:
            nodes_visited += 1
            neighbor = current_state.apply_move(move, moves_dict)
            neighbor_h = heuristic_3x3(neighbor)
            
            # Find neighbors with better heuristic
            if neighbor_h < current_h:
                better_neighbors.append((neighbor, move, neighbor_h))
        
        # If no improvement, end
        if not better_neighbors:
            break
        
        # Randomly choose a better neighbor
        chosen = random.choice(better_neighbors)
        current_state, best_move, current_h = chosen
        path.append(best_move)
    
    # If goal is reached, return path
    if current_state == goal_state:
        end_time = time.time()
        return path, nodes_visited, end_time - start_time
    
    # No path found
    return None, nodes_visited, time.time() - start_time

def solve_3x3(start_state, algorithm="a_star", time_limit=30):
    """
    Main function to solve a 3x3 Rubik's cube with the specified algorithm
    
    Args:
        start_state: Starting state (RubikState)
        algorithm: Algorithm to use (default is "a_star")
        time_limit: Time limit in seconds (default is 30)
        
    Returns:
        tuple: (path, nodes_visited, time_taken)
    """
    print(f"Solving 3x3 Rubik's cube with {algorithm} algorithm...")
    
    # Select appropriate algorithm
    if algorithm.lower() == "a_star":
        return a_star_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "bfs":
        return bfs_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "dfs":
        return dfs_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "ucs":
        return ucs_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "greedy":
        return greedy_best_first_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "ids":
        return ids_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "ida_star":
        return ida_star_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "hill_climbing" or algorithm.lower() == "hill_max":
        return hill_climbing_max_search_3x3(start_state, time_limit=time_limit)
    elif algorithm.lower() == "hill_random":
        return hill_climbing_random_search_3x3(start_state, time_limit=time_limit)
    else:
        print(f"Unknown algorithm: {algorithm}, using A* instead")
        return a_star_search_3x3(start_state, time_limit=time_limit)

def test_scramble_3x3(scramble_moves, algorithm="a_star", time_limit=30):
    """
    Test a specific scramble sequence on a 3x3 Rubik's cube
    
    Args:
        scramble_moves: List of move strings
        algorithm: Algorithm to use (default is "a_star")
        time_limit: Time limit in seconds (default is 30)
        
    Returns:
        bool: True if solved successfully
    """
    # Create a solved state and apply scramble
    start_state = SOLVED_STATE_3x3.copy()
    print(f"Testing scramble: {' '.join(scramble_moves)}")
    
    # Apply scramble moves
    for move in scramble_moves:
        start_state = start_state.apply_move(move, MOVES_3x3)
    
    # Solve the scrambled state
    solution, nodes, time_taken = solve_3x3(start_state, algorithm, time_limit)
    
    # Check if solved
    if solution:
        print(f"Solution found: {' '.join(solution)}")
        print(f"Solution length: {len(solution)}")
        print(f"Nodes explored: {nodes}")
        print(f"Time taken: {time_taken:.2f} seconds")
        
        # Verify solution
        test_state = start_state.copy()
        for move in solution:
            test_state = test_state.apply_move(move, MOVES_3x3)
        
        if test_state == SOLVED_STATE_3x3:
            print("✓ Solution verified")
            return True
        else:
            print("✗ Solution verification failed!")
            return False
    else:
        print(f"No solution found within {time_limit} seconds")
        print(f"Nodes explored: {nodes}")
        return False

if __name__ == "__main__":
    # Test the 3x3 solver with a simple scramble
    scramble = ["R", "U", "R'", "U'"]
    test_scramble_3x3(scramble) 