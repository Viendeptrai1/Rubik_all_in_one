import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def load_algorithm_data():
    """
    Load benchmark data for all algorithms
    
    Returns:
        Dictionary with algorithm data
    """
    # All algorithms to check
    algorithms = [
        'bfs', 'astar', 'dfs', 'ids', 'ucs', 
        'greedy', 'ida_star', 'hill_max', 'hill_random', 'pdb'
    ]
    cube_type = 'rubik2x2'
    
    # Dictionary to store data
    algorithm_data = {}
    
    # For each algorithm, try to load its data
    for algorithm in algorithms:
        extrapolated_file = f"analysis/data/{algorithm}_{cube_type}_extrapolated_latest.csv"
        measured_file = f"analysis/data/{algorithm}_{cube_type}_latest.csv"
        
        if os.path.exists(extrapolated_file) and os.path.exists(measured_file):
            # Load the data
            extrapolated_df = pd.read_csv(extrapolated_file)
            measured_df = pd.read_csv(measured_file)
            
            # Store in our dictionary
            algorithm_data[algorithm] = {
                'extrapolated': extrapolated_df,
                'measured': measured_df,
                'model': extrapolated_df['model'].iloc[0] if 'model' in extrapolated_df.columns else None
            }
            print(f"Loaded data for {algorithm}")
        else:
            print(f"Data for {algorithm} not found")
    
    return algorithm_data

def create_comprehensive_comparison(algorithm_data, sample_size=50000):
    """
    Create a comprehensive comparison chart of all algorithms
    
    Args:
        algorithm_data: Dictionary with algorithm data
        sample_size: Size to compare at (default: 50000)
    """
    # Check which algorithms have data
    available_algorithms = []
    algorithm_times = {}
    algorithm_models = {}
    
    for algorithm, data in algorithm_data.items():
        try:
            extrapolated_df = data['extrapolated']
            if 'sample_size' in extrapolated_df.columns and sample_size in extrapolated_df['sample_size'].values:
                if 'estimated_time' in extrapolated_df.columns:
                    time_value = float(extrapolated_df[extrapolated_df['sample_size'] == sample_size]['estimated_time'])
                elif 'extrapolated_time_seconds' in extrapolated_df.columns:
                    time_value = float(extrapolated_df[extrapolated_df['sample_size'] == sample_size]['extrapolated_time_seconds'])
                else:
                    continue
                    
                algorithm_times[algorithm] = time_value
                algorithm_models[algorithm] = data['model']
                available_algorithms.append(algorithm)
        except Exception as e:
            print(f"Error processing {algorithm}: {e}")
    
    # Sort algorithms by execution time
    sorted_algorithms = sorted(available_algorithms, key=lambda x: algorithm_times[x])
    
    # Create the figure
    plt.figure(figsize=(15, 10))
    
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
    
    # Add model name on top of bars
    for i, algo in enumerate(sorted_algorithms):
        if algo in algorithm_models:
            plt.text(i, algorithm_times[algo] * 1.05, 
                    f"{algorithm_models[algo]}", 
                    ha='center', va='bottom', 
                    fontweight='bold', color='black',
                    fontsize=9)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height * 1.01,
                f'{height:.1f}s',
                ha='center', va='bottom', fontsize=10)
    
    # Set labels and title
    plt.xlabel('Algorithm', fontsize=14)
    plt.ylabel('Estimated execution time (seconds)', fontsize=14)
    plt.title(f'Algorithm Comparison for Rubik 2x2 - {sample_size:,} States', fontsize=16)
    
    # Add grid for better readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Rotate x-labels for better readability
    plt.xticks(rotation=45, ha='right')
    
    # Tight layout to ensure everything fits
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/figures/comprehensive_algorithm_comparison_{timestamp}.png"
    latest_filename = f"analysis/figures/comprehensive_algorithm_comparison_latest.png"
    plt.savefig(filename, dpi=300)
    plt.savefig(latest_filename, dpi=300)
    print(f"Comprehensive comparison figure saved to {filename}")
    
    # Close the figure to free memory
    plt.close()

def create_complexity_summary_table(algorithm_data):
    """
    Create a summary table of complexity models for all algorithms
    
    Args:
        algorithm_data: Dictionary with algorithm data
    """
    # Check which algorithms have model data
    algorithm_models = {}
    algorithm_times_100k = {}
    
    for algorithm, data in algorithm_data.items():
        try:
            if 'model' in data and data['model'] is not None:
                algorithm_models[algorithm] = data['model']
                
                # Get time for 100,000 samples
                extrapolated_df = data['extrapolated']
                if 'sample_size' in extrapolated_df.columns and 100000 in extrapolated_df['sample_size'].values:
                    if 'estimated_time' in extrapolated_df.columns:
                        time_value = float(extrapolated_df[extrapolated_df['sample_size'] == 100000]['estimated_time'])
                    elif 'extrapolated_time_seconds' in extrapolated_df.columns:
                        time_value = float(extrapolated_df[extrapolated_df['sample_size'] == 100000]['extrapolated_time_seconds'])
                    else:
                        continue
                        
                    algorithm_times_100k[algorithm] = time_value
        except Exception as e:
            print(f"Error processing model for {algorithm}: {e}")
    
    # Create a DataFrame to store the summary
    summary_data = {
        'algorithm': [],
        'complexity_model': [],
        'time_for_100k_samples': []
    }
    
    for algorithm in sorted(algorithm_models.keys()):
        summary_data['algorithm'].append(algorithm)
        summary_data['complexity_model'].append(algorithm_models.get(algorithm, 'N/A'))
        summary_data['time_for_100k_samples'].append(algorithm_times_100k.get(algorithm, float('nan')))
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save the summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis/data/extended_complexity_summary_{timestamp}.csv"
    latest_filename = f"analysis/data/extended_complexity_summary_latest.csv"
    summary_df.to_csv(filename, index=False)
    summary_df.to_csv(latest_filename, index=False)
    
    print(f"Complexity summary saved to {filename}")
    print(summary_df)

def main():
    # Create output directories if they don't exist
    os.makedirs("analysis/figures", exist_ok=True)
    os.makedirs("analysis/data", exist_ok=True)
    
    # Load data for all algorithms
    algorithm_data = load_algorithm_data()
    
    # Create comprehensive comparison
    create_comprehensive_comparison(algorithm_data)
    
    # Create complexity summary table
    create_complexity_summary_table(algorithm_data)

if __name__ == "__main__":
    main() 