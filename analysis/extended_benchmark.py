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
from RubikState.rubik_solver import (
    bfs, a_star, dfs, ids, greedy_best_first, 
    ida_star, hill_climbing_max, hill_climbing_random,
    ucs, pdb_astar, solve_rubik
)

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
# Number of repetitions for each sample size
NUM_REPETITIONS = 2
# Maximum time limit for an individual test
TIME_LIMIT = 10  # seconds
# List of complexity models to fit
COMPLEXITY_MODELS = ["O(n)", "O(n log n)", "O(n^2)", "O(n^3)"]

# Dictionary that maps algorithm names to their functions
ALGORITHM_FUNCTIONS = {
    'bfs': bfs,
    'astar': a_star,
    'dfs': dfs,
    'ids': ids,
    'ucs': ucs,
    'greedy': greedy_best_first,
    'ida_star': ida_star,
    'hill_max': hill_climbing_max,
    'hill_random': hill_climbing_random,
    'pdb': pdb_astar
}

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
        algorithm: String name of the algorithm to test (key from ALGORITHM_FUNCTIONS)
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        sample_sizes: List of sample sizes to test
        repetitions: Number of repetitions for each sample size
        
    Returns:
        results: Dictionary with benchmark results
    """
    print(f"Benchmarking {algorithm.upper()} for {cube_type}")
    
    # Get algorithm function
    algorithm_func = ALGORITHM_FUNCTIONS.get(algorithm)
    if not algorithm_func:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    # Results storage
    times = []
    memories = []
    sample_sizes_actual = []
    success_rates = []
    nodes_per_state = []
    
    for n_samples in sample_sizes:
        print(f"\nTesting with {n_samples} states...")
        
        # Create scrambled states (do this only once for each sample size)
        scramble_depth = 2  # Small scramble depth for regression testing
        states = create_scrambled_states(cube_type, n_samples, scramble_depth)
        
        repetition_times = []
        repetition_memories = []
        repetition_success_rates = []
        repetition_nodes_per_state = []
        
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
            success_count = 0
            
            # Run algorithm on each state in the subset
            for i, state in enumerate(subset_states):
                try:
                    solution, nodes, _ = algorithm_func(state, time_limit=TIME_LIMIT)
                    
                    if solution is not None:
                        success_count += 1
                    
                    nodes_total += nodes
                    
                    # Print progress occasionally
                    if (i+1) % 10 == 0:
                        print(f"    Processed {i+1}/{subset_size} states")
                        
                except Exception as e:
                    print(f"    Error on state {i+1}: {e}")
            
            # Calculate total time and estimate for full dataset
            elapsed_time = time.time() - start_time
            estimated_full_time = (elapsed_time / subset_size) * n_samples
            success_rate = (success_count / subset_size) * 100
            avg_nodes = nodes_total / subset_size
            
            print(f"    Subset processed in {elapsed_time:.2f}s")
            print(f"    Estimated time for full dataset: {estimated_full_time:.2f}s")
            print(f"    Success rate: {success_rate:.1f}%")
            print(f"    Average nodes per state: {avg_nodes:.1f}")
            
            # Record memory and stop tracing
            memory_used = measure_memory_usage()
            tracemalloc.stop()
            
            repetition_times.append(estimated_full_time)
            repetition_memories.append(memory_used)
            repetition_success_rates.append(success_rate)
            repetition_nodes_per_state.append(avg_nodes)
        
        # Average the repetitions
        avg_time = np.mean(repetition_times)
        avg_memory = np.mean(repetition_memories)
        avg_success_rate = np.mean(repetition_success_rates)
        avg_nodes_per_state = np.mean(repetition_nodes_per_state)
        
        times.append(avg_time)
        memories.append(avg_memory)
        sample_sizes_actual.append(n_samples)
        success_rates.append(avg_success_rate)
        nodes_per_state.append(avg_nodes_per_state)
        
        print(f"  Average time for {n_samples} states: {avg_time:.2f}s")
        print(f"  Average memory: {avg_memory:.2f}MB")
        print(f"  Average success rate: {avg_success_rate:.1f}%")
        print(f"  Average nodes per state: {avg_nodes_per_state:.1f}")
    
    return {
        'sample_sizes': sample_sizes_actual,
        'times': times,
        'memories': memories,
        'success_rates': success_rates,
        'nodes_per_state': nodes_per_state
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
    if r_squared:
        best_model = max(r_squared, key=r_squared.get)
        print(f"Best model: {best_model} with R² = {r_squared[best_model]:.4f}")
    else:
        best_model = None
        print("No model could be fitted to the data")
    
    # Extrapolate to larger sample sizes
    extrapolations = {}
    if best_model and best_model in models:
        for size in EXTRAPOLATE_SIZES:
            extrapolations[size] = float(models[best_model]['function'](
                size, *models[best_model]['params']
            ))
            print(f"Extrapolated {best_model} time for {size} samples: {extrapolations[size]:.2f}s")
    
    return best_model, models, extrapolations

def plot_results(results, algorithm, cube_type, best_model, models, extrapolations):
    """
    Plot benchmark results, fitted models, and extrapolations
    
    Args:
        results: Dictionary with benchmark results
        algorithm: String name of the algorithm
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        best_model: Name of the best fitting model
        models: Dictionary of fitted models
        extrapolations: Dictionary of extrapolated values
    """
    sample_sizes = results['sample_sizes']
    times = results['times']
    
    # Create figure
    plt.figure(figsize=(12, 8))
    
    # Plot measured data points
    plt.scatter(sample_sizes, times, s=100, c='blue', label='Measured data', zorder=5)
    
    # Plot fitted models
    x_fit = np.linspace(min(sample_sizes) * 0.9, max(sample_sizes) * 1.1, 100)
    for name, model in models.items():
        y_fit = model['function'](x_fit, *model['params'])
        plt.plot(x_fit, y_fit, '--', label=f"{name} fit (R² = {model['r_squared']:.4f})")
    
    # Plot extrapolation points
    if best_model and best_model in models:
        extrapolation_sizes = list(extrapolations.keys())
        extrapolation_times = list(extrapolations.values())
        plt.scatter(extrapolation_sizes, extrapolation_times, s=100, c='red', 
                   marker='*', label='Extrapolated data', zorder=5)
        
        # Add text labels for extrapolated points
        for size, time_val in zip(extrapolation_sizes, extrapolation_times):
            plt.text(size, time_val * 1.07, f"{size}: {time_val:.1f}s", 
                    ha='center', va='bottom', fontweight='bold')
        
        # Plot extended best model line to show trend
        x_extend = np.linspace(min(sample_sizes) * 0.9, max(extrapolation_sizes) * 1.1, 100)
        y_extend = models[best_model]['function'](x_extend, *models[best_model]['params'])
        plt.plot(x_extend, y_extend, 'r-', linewidth=2, 
                label=f"Best model: {best_model}", zorder=4)
    
    # Set labels and title
    plt.xlabel('Number of states', fontsize=14)
    plt.ylabel('Execution time (seconds)', fontsize=14)
    plt.title(f'{algorithm.upper()} algorithm on {cube_type} - Extrapolation Analysis', fontsize=16)
    
    # Log scales for better visualization
    plt.xscale('log')
    plt.yscale('log')
    
    # Grid, legend and style
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/figures/{algorithm}_{cube_type.lower()}_extrapolation_{timestamp}.png"
    latest_filename = f"analysis/figures/{algorithm}_{cube_type.lower()}_extrapolation_latest.png"
    plt.savefig(filename, dpi=300)
    plt.savefig(latest_filename, dpi=300)
    print(f"Figure saved to {filename}")
    
    # Close the figure to free memory
    plt.close()

def save_results(results, algorithm, cube_type, best_model, extrapolations):
    """
    Save benchmark results and extrapolations to CSV files
    
    Args:
        results: Dictionary with benchmark results
        algorithm: String name of the algorithm
        cube_type: Either 'Rubik2x2' or 'Rubik3x3'
        best_model: Name of the best fitting model
        extrapolations: Dictionary of extrapolated values
    """
    # Create timestamps
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save measured results
    measured_data = {
        'sample_size': results['sample_sizes'],
        'execution_time': results['times'],
        'memory_usage': results['memories'],
        'success_rate': results['success_rates'],
        'nodes_per_state': results['nodes_per_state']
    }
    measured_df = pd.DataFrame(measured_data)
    measured_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_{timestamp}.csv"
    latest_measured_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_latest.csv"
    measured_df.to_csv(measured_filename, index=False)
    measured_df.to_csv(latest_measured_filename, index=False)
    
    # Save extrapolated results
    if best_model and extrapolations:
        extrapolated_data = {
            'sample_size': list(extrapolations.keys()),
            'estimated_time': list(extrapolations.values()),
            'model': [best_model] * len(extrapolations)
        }
        extrapolated_df = pd.DataFrame(extrapolated_data)
        extrapolated_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_extrapolated_{timestamp}.csv"
        latest_extrapolated_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_extrapolated_latest.csv"
        extrapolated_df.to_csv(extrapolated_filename, index=False)
        extrapolated_df.to_csv(latest_extrapolated_filename, index=False)
    
    print(f"Results saved to {measured_filename} and {latest_measured_filename}")

def run_extended_benchmarks():
    """Run benchmarks for all algorithms and extrapolate using regression analysis"""
    
    # Define parameters for benchmarks - use all algorithms on Rubik2x2 for now
    params = [
        # Skip BFS and A* since they were already benchmarked
        # ('bfs', 'Rubik2x2'),
        # ('astar', 'Rubik2x2'),
        ('dfs', 'Rubik2x2'),
        ('ids', 'Rubik2x2'),
        ('ucs', 'Rubik2x2'),
        ('greedy', 'Rubik2x2'),
        ('ida_star', 'Rubik2x2'),
        ('hill_max', 'Rubik2x2'),
        ('hill_random', 'Rubik2x2'),
        ('pdb', 'Rubik2x2')
    ]
    
    for algorithm, cube_type in params:
        print(f"\n{'-'*80}\nRunning {algorithm.upper()} regression benchmark for {cube_type}\n{'-'*80}")
        
        try:
            # Run benchmark
            results = benchmark_algorithm(algorithm, cube_type)
            
            # Fit complexity models and extrapolate
            best_model, models, extrapolations = fit_complexity_models(results['sample_sizes'], results['times'])
            
            # Plot results
            plot_results(results, algorithm, cube_type, best_model, models, extrapolations)
            
            # Save results
            save_results(results, algorithm, cube_type, best_model, extrapolations)
        
        except Exception as e:
            print(f"Error benchmarking {algorithm} on {cube_type}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\nAll extended benchmarks completed!")

def create_algorithm_comparison_plot():
    """Create a comparison plot of all benchmarked algorithms"""
    algorithms = [
        'bfs', 'astar', 'dfs', 'ids', 'ucs', 
        'greedy', 'ida_star', 'hill_max', 'hill_random', 'pdb'
    ]
    cube_type = 'Rubik2x2'  # Focus on 2x2 for now
    
    plt.figure(figsize=(14, 10))
    
    # Extrapolation size to compare (choose the 2nd largest for better visibility)
    size_to_compare = EXTRAPOLATE_SIZES[-2]  # 50,000
    
    # Collect data for algorithms
    algorithm_times = {}
    success_rates = {}
    
    for algorithm in algorithms:
        try:
            # Try to load the extrapolated data
            filename = f"analysis/data/{algorithm}_{cube_type.lower()}_extrapolated_latest.csv"
            if os.path.exists(filename):
                df = pd.read_csv(filename)
                if size_to_compare in df['sample_size'].values:
                    time_value = float(df[df['sample_size'] == size_to_compare]['estimated_time'])
                    algorithm_times[algorithm] = time_value
            
            # Load success rate from measured data
            measured_filename = f"analysis/data/{algorithm}_{cube_type.lower()}_latest.csv"
            if os.path.exists(measured_filename):
                df = pd.read_csv(measured_filename)
                if not df.empty:
                    success_rates[algorithm] = df['success_rate'].mean()
        except Exception as e:
            print(f"Error loading data for {algorithm}: {e}")
    
    # Sort algorithms by execution time
    sorted_algorithms = sorted(algorithm_times.keys(), key=lambda x: algorithm_times[x])
    
    # Assign colors based on algorithm category
    colors = {
        'bfs': 'royalblue',
        'astar': 'forestgreen',
        'dfs': 'firebrick',
        'ids': 'darkorange',
        'ucs': 'mediumorchid',
        'greedy': 'gold',
        'ida_star': 'teal',
        'hill_max': 'crimson',
        'hill_random': 'indianred',
        'pdb': 'darkgreen'
    }
    
    # Plot execution times
    bars = plt.bar(sorted_algorithms, 
                  [algorithm_times[algo] for algo in sorted_algorithms],
                  color=[colors.get(algo, 'gray') for algo in sorted_algorithms])
    
    # Add success rate as text on bars
    for i, algo in enumerate(sorted_algorithms):
        if algo in success_rates:
            plt.text(i, algorithm_times[algo] * 1.05, 
                    f"{success_rates[algo]:.1f}%", 
                    ha='center', va='bottom', 
                    fontweight='bold', color='black')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height * 1.01,
                f'{height:.1f}s',
                ha='center', va='bottom', fontsize=10)
    
    # Set labels and title
    plt.xlabel('Algorithm', fontsize=14)
    plt.ylabel('Estimated execution time (seconds)', fontsize=14)
    plt.title(f'Algorithm Comparison for {cube_type} - {size_to_compare} States', fontsize=16)
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Rotate x-labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout to ensure everything fits
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/figures/algorithm_comparison_extended_{cube_type.lower()}_{timestamp}.png"
    latest_filename = f"analysis/figures/algorithm_comparison_extended_{cube_type.lower()}_latest.png"
    plt.savefig(filename, dpi=300)
    plt.savefig(latest_filename, dpi=300)
    print(f"Comparison figure saved to {filename}")
    
    # Close the figure to free memory
    plt.close()

if __name__ == "__main__":
    import traceback
    try:
        run_extended_benchmarks()
        create_algorithm_comparison_plot()
    except Exception as e:
        print(f"Error in benchmark: {e}")
        traceback.print_exc() 