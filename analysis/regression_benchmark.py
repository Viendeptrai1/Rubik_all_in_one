import sys
import os
import time
import tracemalloc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
from scipy.optimize import curve_fit
import random

# Add the parent directory to the path so we can import the required modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Rubik state and solver functions
from RubikState.rubik_chen import RubikState
from RubikState.rubik_2x2 import Rubik2x2State
from RubikState.rubik_solver import bfs, a_star, solve_rubik

# Create data directory if it doesn't exist
if not os.path.exists('analysis/data'):
    os.makedirs('analysis/data')

# Create figures directory if it doesn't exist
if not os.path.exists('analysis/figures'):
    os.makedirs('analysis/figures')

# Sample sizes to test (reduced for quick demonstration)
SAMPLE_SIZES = [100, 200, 500, 1000, 2000]
# Sizes to extrapolate to
EXTRAPOLATE_SIZES = [5000, 10000, 50000, 100000]
# Number of repetitions for each sample size (reduced for quick demonstration)
NUM_REPETITIONS = 2
# Maximum time limit for an individual test
TIME_LIMIT = 10  # seconds
# List of complexity models to fit
COMPLEXITY_MODELS = ["O(n)", "O(n log n)", "O(n^2)", "O(n^3)"]

def measure_memory_usage():
    """Measure current memory usage in MB"""
    current, peak = tracemalloc.get_traced_memory()
    return peak / 1024 / 1024  # Convert to MB

def create_scrambled_states(cube_type, n_samples, scramble_depth=3):
    """
    Create a specific number of scrambled Rubik's cube states
    
    Args:
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        n_samples: Number of scrambled states to create
        scramble_depth: Number of random moves for scrambling
        
    Returns:
        list of scrambled states
    """
    print(f"Creating {n_samples} scrambled {cube_type} states...")
    states = []
    
    # Get possible moves based on cube type
    if cube_type == 'Rubik2x2':
        moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    else:
        moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    
    for i in range(n_samples):
        # Create a new solved cube
        if cube_type == 'Rubik2x2':
            cube = Rubik2x2State()
        else:
            cube = RubikState()
        
        # Apply random moves
        for _ in range(scramble_depth):
            move = random.choice(moves)
            cube = cube.apply_move(move)
        
        states.append(cube)
        
        # Print progress
        if (i+1) % 1000 == 0 or i+1 == n_samples:
            print(f"  Created {i+1}/{n_samples} states")
    
    return states

def benchmark_algorithm(algorithm, cube_type, sample_sizes=SAMPLE_SIZES, repetitions=NUM_REPETITIONS):
    """
    Benchmark an algorithm with different sample sizes and measure execution time
    
    Args:
        algorithm: Either 'bfs' or 'astar'
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        sample_sizes: List of sample sizes to test
        repetitions: Number of repetitions for each sample size
        
    Returns:
        results: Dictionary with benchmark results
    """
    print(f"Benchmarking {algorithm.upper()} for {cube_type}")
    
    # Results storage
    times = []
    memories = []
    sample_sizes_actual = []
    
    for n_samples in sample_sizes:
        print(f"\nTesting with {n_samples} states...")
        
        # Create scrambled states (do this only once for each sample size)
        scramble_depth = 2  # Small scramble depth for regression testing
        states = create_scrambled_states(cube_type, n_samples, scramble_depth)
        
        repetition_times = []
        repetition_memories = []
        
        for rep in range(repetitions):
            print(f"  Repetition {rep+1}/{repetitions}")
            
            # Start memory tracing
            tracemalloc.start()
            
            # Measure time
            start_time = time.time()
            
            # Process a subset of states to avoid excessive runtime
            subset_size = min(n_samples, 50)  # Process at most 50 states
            subset_states = random.sample(states, subset_size)
            
            nodes_total = 0
            
            # Run algorithm on each state in the subset
            for i, state in enumerate(subset_states):
                try:
                    if algorithm == 'bfs':
                        solution, nodes, _ = bfs(state, time_limit=TIME_LIMIT)
                    else:  # a_star
                        solution, nodes, _ = a_star(state, time_limit=TIME_LIMIT)
                    
                    nodes_total += nodes
                    
                    # Print progress occasionally
                    if (i+1) % 10 == 0:
                        print(f"    Processed {i+1}/{subset_size} states")
                        
                except Exception as e:
                    print(f"    Error on state {i+1}: {e}")
            
            # Calculate total time and estimate for full dataset
            elapsed_time = time.time() - start_time
            estimated_full_time = (elapsed_time / subset_size) * n_samples
            
            print(f"    Subset processed in {elapsed_time:.2f}s")
            print(f"    Estimated time for full dataset: {estimated_full_time:.2f}s")
            print(f"    Average nodes per state: {nodes_total/subset_size:.1f}")
            
            # Record memory and stop tracing
            memory_used = measure_memory_usage()
            tracemalloc.stop()
            
            repetition_times.append(estimated_full_time)
            repetition_memories.append(memory_used)
        
        # Average the repetitions
        avg_time = np.mean(repetition_times)
        avg_memory = np.mean(repetition_memories)
        
        times.append(avg_time)
        memories.append(avg_memory)
        sample_sizes_actual.append(n_samples)
        
        print(f"  Average time for {n_samples} states: {avg_time:.2f}s")
        print(f"  Average memory: {avg_memory:.2f}MB")
    
    return {
        'sample_sizes': sample_sizes_actual,
        'times': times,
        'memories': memories
    }

def linear_complexity(x, a, b):
    """O(n) complexity model: y = a*x + b"""
    return a * x + b

def linearithmic_complexity(x, a, b):
    """O(n log n) complexity model: y = a*x*log(x) + b"""
    return a * x * np.log(x) + b

def quadratic_complexity(x, a, b):
    """O(n^2) complexity model: y = a*x^2 + b"""
    return a * x**2 + b

def cubic_complexity(x, a, b):
    """O(n^3) complexity model: y = a*x^3 + b"""
    return a * x**3 + b

def fit_complexity_models(sample_sizes, times):
    """
    Fit different complexity models to the data and determine the best fit
    
    Args:
        sample_sizes: List of sample sizes
        times: List of execution times
        
    Returns:
        best_model: Name of the best fitting model
        models: Dictionary of fitted models
        extrapolations: Dictionary of extrapolated values
    """
    sample_sizes_array = np.array(sample_sizes)
    times_array = np.array(times)
    
    # Models to test
    complexity_functions = {
        "O(n)": linear_complexity,
        "O(n log n)": linearithmic_complexity,
        "O(n^2)": quadratic_complexity,
        "O(n^3)": cubic_complexity
    }
    
    # Fit each model
    models = {}
    r_squared = {}
    
    for name, func in complexity_functions.items():
        try:
            # Curve fitting
            params, _ = curve_fit(func, sample_sizes_array, times_array)
            
            # Make predictions
            predictions = func(sample_sizes_array, *params)
            
            # Calculate R^2
            ss_total = np.sum((times_array - np.mean(times_array))**2)
            ss_residual = np.sum((times_array - predictions)**2)
            r2 = 1 - (ss_residual / ss_total)
            
            models[name] = {
                'function': func,
                'params': params,
                'r_squared': r2
            }
            
            r_squared[name] = r2
            
            print(f"{name} fit: R² = {r2:.4f}, parameters = {params}")
            
        except Exception as e:
            print(f"Error fitting {name} model: {e}")
    
    # Find the best model (highest R²)
    best_model = max(r_squared.items(), key=lambda x: x[1])[0]
    print(f"Best fitting model: {best_model} (R² = {r_squared[best_model]:.4f})")
    
    # Extrapolate for larger sizes
    extrapolations = {}
    for size in EXTRAPOLATE_SIZES:
        extrapolations[size] = {}
        for name, model in models.items():
            func = model['function']
            params = model['params']
            extrapolated_time = func(size, *params)
            extrapolations[size][name] = extrapolated_time
            print(f"Extrapolated time for {size} samples with {name}: {extrapolated_time:.2f}s")
    
    return best_model, models, extrapolations

def plot_results(results, algorithm, cube_type, best_model, models, extrapolations):
    """
    Plot the benchmark results and extrapolations
    
    Args:
        results: Dictionary with benchmark results
        algorithm: The algorithm name
        cube_type: The cube type
        best_model: Name of the best fitting model
        models: Dictionary of fitted models
        extrapolations: Dictionary of extrapolated values
    """
    plt.figure(figsize=(12, 8))
    
    # Plot actual data points
    plt.scatter(results['sample_sizes'], results['times'], s=100, c='blue', 
                label='Measured data', zorder=5)
    
    # Create a smooth curve for each model
    x = np.linspace(min(results['sample_sizes']), max(EXTRAPOLATE_SIZES), 1000)
    for name, model in models.items():
        func = model['function']
        params = model['params']
        y = func(x, *params)
        
        # Highlight the best model
        if name == best_model:
            plt.plot(x, y, linewidth=3, label=f"{name} (Best fit, R²={model['r_squared']:.4f})")
        else:
            plt.plot(x, y, '--', linewidth=1.5, label=f"{name} (R²={model['r_squared']:.4f})")
    
    # Plot extrapolations for the best model
    markers = ['o', 's', 'd', '^']
    for i, size in enumerate(EXTRAPOLATE_SIZES):
        plt.scatter(size, extrapolations[size][best_model], s=150, c='red', 
                    marker=markers[i % len(markers)], 
                    label=f'Extrapolated ({size:,}): {extrapolations[size][best_model]:.2f}s',
                    zorder=5)
    
    # Set labels and title
    plt.xlabel('Sample Size (n)', fontsize=14)
    plt.ylabel('Execution Time (seconds)', fontsize=14)
    plt.title(f'Performance of {algorithm.upper()} on {cube_type} with Extrapolation', fontsize=16)
    
    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Format x-axis with comma separator for thousands
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    
    # Use logarithmic scale for better visualization
    plt.xscale('log')
    plt.yscale('log')
    
    # Save the figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/figures/{algorithm}_{cube_type.lower()}_extrapolation_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    
    # Also save with a standard name
    standard_filename = f"analysis/figures/{algorithm}_{cube_type.lower()}_extrapolation_latest.png"
    plt.savefig(standard_filename, dpi=300, bbox_inches='tight')
    
    plt.close()
    
    print(f"Plot saved to {filename} and {standard_filename}")

def save_results(results, algorithm, cube_type, best_model, extrapolations):
    """
    Save benchmark results and extrapolations to CSV
    
    Args:
        results: Dictionary with benchmark results
        algorithm: The algorithm name
        cube_type: The cube type
        best_model: Name of the best fitting model
        extrapolations: Dictionary of extrapolated values
    """
    # Create DataFrame for measured results
    df_measured = pd.DataFrame({
        'sample_size': results['sample_sizes'],
        'time_seconds': results['times'],
        'memory_mb': results['memories']
    })
    
    # Create DataFrame for extrapolated results
    extrapolated_sizes = []
    extrapolated_times = []
    
    for size in EXTRAPOLATE_SIZES:
        extrapolated_sizes.append(size)
        extrapolated_times.append(extrapolations[size][best_model])
    
    df_extrapolated = pd.DataFrame({
        'sample_size': extrapolated_sizes,
        'extrapolated_time_seconds': extrapolated_times,
        'model': [best_model] * len(extrapolated_sizes)
    })
    
    # Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    measured_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_measured_{timestamp}.csv"
    df_measured.to_csv(measured_filename, index=False)
    
    extrapolated_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_extrapolated_{timestamp}.csv"
    df_extrapolated.to_csv(extrapolated_filename, index=False)
    
    # Also save with standard names
    df_measured.to_csv(f"analysis/data/{algorithm}_{cube_type.lower()}_measured_latest.csv", index=False)
    df_extrapolated.to_csv(f"analysis/data/{algorithm}_{cube_type.lower()}_extrapolated_latest.csv", index=False)
    
    print(f"Results saved to {measured_filename} and {extrapolated_filename}")

def run_regression_benchmarks():
    """Run benchmarks and extrapolate using regression analysis"""
    # Define parameters for benchmarks
    params = [
        # (algorithm, cube_type)
        ('bfs', 'Rubik2x2'),
        ('astar', 'Rubik2x2'),
        # Use only 2x2 for quick demo
        # ('bfs', 'Rubik3x3'),
        # ('astar', 'Rubik3x3')
    ]
    
    for algorithm, cube_type in params:
        print(f"\n{'-'*80}\nRunning {algorithm.upper()} regression benchmark for {cube_type}\n{'-'*80}")
        
        # Run benchmark
        results = benchmark_algorithm(algorithm, cube_type)
        
        # Fit complexity models and extrapolate
        best_model, models, extrapolations = fit_complexity_models(results['sample_sizes'], results['times'])
        
        # Plot results
        plot_results(results, algorithm, cube_type, best_model, models, extrapolations)
        
        # Save results
        save_results(results, algorithm, cube_type, best_model, extrapolations)
    
    print("\nAll regression benchmarks completed!")

if __name__ == "__main__":
    import traceback
    try:
        run_regression_benchmarks()
    except Exception as e:
        print(f"Error in benchmark: {e}")
        traceback.print_exc() 