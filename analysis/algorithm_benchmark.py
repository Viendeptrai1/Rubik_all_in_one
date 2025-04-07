import sys
import os
import time
import tracemalloc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import random

# Add the parent directory to the path so we can import the required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Rubik state and solver functions
from RubikState.rubik_chen import RubikState
from RubikState.rubik_2x2 import Rubik2x2State
from RubikState.rubik_solver import bfs, a_star, solve_rubik

# For 3D visualization import
from rubik_2x2 import RubikCube2x2
from rubik_3x3 import RubikCube

# Create data directory if it doesn't exist
if not os.path.exists('analysis/data'):
    os.makedirs('analysis/data')

# Constants
TIME_LIMIT = 300  # 5 minutes limit for each search
MEMORY_LIMIT = 4 * 1024 * 1024 * 1024  # 4GB memory limit
NUM_SAMPLES = 5  # Number of scrambled cubes to test for each depth

def measure_memory_usage():
    """Measure current memory usage in MB"""
    current, peak = tracemalloc.get_traced_memory()
    return peak / 1024 / 1024  # Convert to MB

def manually_scramble_cube(cube_type, depth):
    """
    Manually scramble a cube by applying random moves
    
    Args:
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        depth: Number of random moves to apply
        
    Returns:
        scrambled_cube: The scrambled RubikState or Rubik2x2State
    """
    print(f"  Manually scrambling with {depth} moves")
    
    # Create a new solved cube
    if cube_type == 'Rubik2x2':
        cube = Rubik2x2State()
    else:
        cube = RubikState()
    
    # Get possible moves based on cube type
    if cube_type == 'Rubik2x2':
        moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    else:
        moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    
    # Apply random moves
    scramble_sequence = []
    for _ in range(depth):
        move = random.choice(moves)
        scramble_sequence.append(move)
        cube = cube.apply_move(move)
    
    print(f"  Applied scramble: {' '.join(scramble_sequence)}")
    
    return cube

def run_bfs_benchmark(cube_type, max_depth, samples_per_depth=NUM_SAMPLES):
    """
    Run BFS benchmarks on scrambled cubes of increasing depths
    
    Args:
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        max_depth: Maximum scramble depth to test
        samples_per_depth: Number of scrambled cubes to test per depth
        
    Returns:
        results: Dictionary with benchmark results
    """
    print(f"Starting BFS benchmark for {cube_type} up to depth {max_depth}")
    
    # Initialize result arrays
    depths = list(range(1, max_depth + 1))
    time_results = []
    memory_results = []
    success_rate = []
    nodes_expanded = []
    
    for depth in depths:
        success_count = 0
        depth_time = []
        depth_memory = []
        depth_nodes = []
        
        print(f"Testing depth {depth}...")
        
        for i in range(samples_per_depth):
            print(f"  Sample {i+1}/{samples_per_depth}", end=": ")
            
            # Manually scramble cube instead of using 3D model
            cube = manually_scramble_cube(cube_type, depth)
            
            # Debug - check the state
            print(f"  Scrambled state: {cube}")
            
            # Start memory tracing
            tracemalloc.start()
            
            # Measure time
            start_time = time.time()
            
            # Run BFS with time limit
            try:
                solution, nodes_visited, search_time = bfs(cube, time_limit=TIME_LIMIT)
                
                if solution:
                    success_count += 1
                    depth_time.append(search_time)
                    depth_memory.append(measure_memory_usage())
                    depth_nodes.append(nodes_visited)
                    print(f"Solved in {search_time:.2f}s, {nodes_visited} nodes")
                    print(f"Solution: {solution}")
                else:
                    print("Failed (no solution found within time limit)")
                    
                    # Try with solve_rubik as a fallback for debugging
                    print("  Trying with solve_rubik...")
                    solution_path, nodes, time_taken = solve_rubik(cube, algorithm="bfs", time_limit=10)
                    if solution_path:
                        print(f"  solve_rubik succeeded: {solution_path}")
                    else:
                        print("  solve_rubik also failed")
                
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
            
            # Stop memory tracing
            tracemalloc.stop()
        
        # Calculate average results for this depth
        if depth_time:
            avg_time = np.mean(depth_time)
            avg_memory = np.mean(depth_memory)
            avg_nodes = np.mean(depth_nodes)
        else:
            avg_time = float('nan')
            avg_memory = float('nan')
            avg_nodes = float('nan')
            
        success_percentage = (success_count / samples_per_depth) * 100
        
        time_results.append(avg_time)
        memory_results.append(avg_memory)
        success_rate.append(success_percentage)
        nodes_expanded.append(avg_nodes)
        
        print(f"Depth {depth} results: Success rate {success_percentage}%, "
              f"Avg time {avg_time:.2f}s, Avg memory {avg_memory:.2f}MB")
        
        # If success rate drops below 20%, stop testing deeper levels
        if success_percentage < 20:
            print(f"Success rate too low at depth {depth}, stopping...")
            break
            
    # Create results dictionary
    results = {
        'depths': depths[:len(time_results)],
        'time': time_results,
        'memory': memory_results,
        'success_rate': success_rate,
        'nodes_expanded': nodes_expanded
    }
    
    return results

def run_astar_benchmark(cube_type, max_depth, samples_per_depth=NUM_SAMPLES):
    """
    Run A* benchmarks on scrambled cubes of increasing depths
    
    Args:
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        max_depth: Maximum scramble depth to test
        samples_per_depth: Number of scrambled cubes to test per depth
        
    Returns:
        results: Dictionary with benchmark results
    """
    print(f"Starting A* benchmark for {cube_type} up to depth {max_depth}")
    
    # Initialize result arrays
    depths = list(range(1, max_depth + 1))
    time_results = []
    memory_results = []
    success_rate = []
    nodes_expanded = []
    
    for depth in depths:
        success_count = 0
        depth_time = []
        depth_memory = []
        depth_nodes = []
        
        print(f"Testing depth {depth}...")
        
        for i in range(samples_per_depth):
            print(f"  Sample {i+1}/{samples_per_depth}", end=": ")
            
            # Manually scramble cube instead of using 3D model
            cube = manually_scramble_cube(cube_type, depth)
            
            # Debug - check the state
            print(f"  Scrambled state: {cube}")
            
            # Start memory tracing
            tracemalloc.start()
            
            # Measure time
            start_time = time.time()
            
            # Run A* with time limit
            try:
                solution, nodes_visited, search_time = a_star(cube, time_limit=TIME_LIMIT)
                
                if solution:
                    success_count += 1
                    depth_time.append(search_time)
                    depth_memory.append(measure_memory_usage())
                    depth_nodes.append(nodes_visited)
                    print(f"Solved in {search_time:.2f}s, {nodes_visited} nodes")
                    print(f"Solution: {solution}")
                else:
                    print("Failed (no solution found within time limit)")
                    
                    # Try with solve_rubik as a fallback for debugging
                    print("  Trying with solve_rubik...")
                    solution_path, nodes, time_taken = solve_rubik(cube, algorithm="a_star", time_limit=10)
                    if solution_path:
                        print(f"  solve_rubik succeeded: {solution_path}")
                    else:
                        print("  solve_rubik also failed")
                    
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exc()
            
            # Stop memory tracing
            tracemalloc.stop()
        
        # Calculate average results for this depth
        if depth_time:
            avg_time = np.mean(depth_time)
            avg_memory = np.mean(depth_memory)
            avg_nodes = np.mean(depth_nodes)
        else:
            avg_time = float('nan')
            avg_memory = float('nan')
            avg_nodes = float('nan')
            
        success_percentage = (success_count / samples_per_depth) * 100
        
        time_results.append(avg_time)
        memory_results.append(avg_memory)
        success_rate.append(success_percentage)
        nodes_expanded.append(avg_nodes)
        
        print(f"Depth {depth} results: Success rate {success_percentage}%, "
              f"Avg time {avg_time:.2f}s, Avg memory {avg_memory:.2f}MB")
        
        # If success rate drops below 20%, stop testing deeper levels
        if success_percentage < 20:
            print(f"Success rate too low at depth {depth}, stopping...")
            break
            
    # Create results dictionary
    results = {
        'depths': depths[:len(time_results)],
        'time': time_results,
        'memory': memory_results,
        'success_rate': success_rate,
        'nodes_expanded': nodes_expanded
    }
    
    return results

def run_benchmarks():
    """Run all benchmarks and save results to CSV files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define parameters for benchmarks
    params = [
        # (algorithm, cube_type, max_depth)
        ('bfs', 'Rubik2x2', 9),
        ('bfs', 'Rubik3x3', 5),
        ('astar', 'Rubik2x2', 11),
        ('astar', 'Rubik3x3', 5)
    ]
    
    for algorithm, cube_type, max_depth in params:
        print(f"\n{'-'*80}\nRunning {algorithm.upper()} benchmark for {cube_type} (max depth: {max_depth})\n{'-'*80}")
        
        # Run appropriate benchmark
        if algorithm == 'bfs':
            results = run_bfs_benchmark(cube_type, max_depth)
        else:
            results = run_astar_benchmark(cube_type, max_depth)
        
        # Convert to DataFrame
        df = pd.DataFrame({
            'depth': results['depths'],
            'time_seconds': results['time'],
            'memory_mb': results['memory'],
            'success_rate': results['success_rate'],
            'nodes_expanded': results['nodes_expanded']
        })
        
        # Save to CSV
        filename = f"analysis/data/{algorithm}_{cube_type.lower()}_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"Results saved to {filename}")
        
        # Also save the most recent results with a standard name for the visualization script
        standard_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_latest.csv"
        df.to_csv(standard_filename, index=False)
        print(f"Results also saved to {standard_filename}")
    
    print("\nAll benchmarks completed!")

if __name__ == "__main__":
    import traceback
    run_benchmarks() 