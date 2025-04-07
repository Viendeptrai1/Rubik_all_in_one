import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Create figures directory if it doesn't exist
if not os.path.exists('analysis/figures'):
    os.makedirs('analysis/figures')

def load_data():
    """
    Load the latest measured and extrapolated data files
    
    Returns:
        Dictionary with loaded DataFrames
    """
    data = {}
    
    # Define files to load
    algorithms = ['bfs', 'astar']
    cube_types = ['rubik2x2', 'rubik3x3']
    
    for algorithm in algorithms:
        for cube_type in cube_types:
            # Load measured data
            measured_file = f"analysis/data/{algorithm}_{cube_type}_measured_latest.csv"
            extrapolated_file = f"analysis/data/{algorithm}_{cube_type}_extrapolated_latest.csv"
            
            if os.path.exists(measured_file) and os.path.exists(extrapolated_file):
                key = f"{algorithm}_{cube_type}"
                data[key] = {
                    'measured': pd.read_csv(measured_file),
                    'extrapolated': pd.read_csv(extrapolated_file)
                }
                print(f"Loaded data for {algorithm.upper()} on {cube_type}")
            else:
                print(f"Missing data files for {algorithm.upper()} on {cube_type}")
    
    return data

def plot_algorithm_comparison(data):
    """
    Create plots comparing BFS and A* algorithms for both cube types
    
    Args:
        data: Dictionary with loaded DataFrames
    """
    cube_types = ['rubik2x2', 'rubik3x3']
    
    for cube_type in cube_types:
        # Check if we have both BFS and A* data for this cube type
        if f"bfs_{cube_type}" in data and f"astar_{cube_type}" in data:
            plt.figure(figsize=(12, 8))
            
            # Plot measured data points for both algorithms
            bfs_measured = data[f"bfs_{cube_type}"]['measured']
            astar_measured = data[f"astar_{cube_type}"]['measured']
            
            plt.scatter(bfs_measured['sample_size'], bfs_measured['time_seconds'], 
                       s=100, marker='o', label='BFS Measured', color='blue')
            plt.scatter(astar_measured['sample_size'], astar_measured['time_seconds'], 
                       s=100, marker='s', label='A* Measured', color='green')
            
            # Plot extrapolated data points for both algorithms
            bfs_extrapolated = data[f"bfs_{cube_type}"]['extrapolated']
            astar_extrapolated = data[f"astar_{cube_type}"]['extrapolated']
            
            # Create a smooth curve for best-fit model
            x = np.linspace(
                min(min(bfs_measured['sample_size']), min(astar_measured['sample_size'])),
                max(max(bfs_extrapolated['sample_size']), max(astar_extrapolated['sample_size'])),
                1000
            )
            
            # Find which model was used for each algorithm
            bfs_model = bfs_extrapolated['model'].iloc[0]
            astar_model = astar_extrapolated['model'].iloc[0]
            
            # Plot extrapolated points
            plt.scatter(bfs_extrapolated['sample_size'], bfs_extrapolated['extrapolated_time_seconds'], 
                      s=150, marker='o', facecolors='none', edgecolors='blue', linewidth=2,
                      label=f'BFS Extrapolated ({bfs_model})')
            plt.scatter(astar_extrapolated['sample_size'], astar_extrapolated['extrapolated_time_seconds'], 
                      s=150, marker='s', facecolors='none', edgecolors='green', linewidth=2,
                      label=f'A* Extrapolated ({astar_model})')
            
            # Add annotations for largest extrapolated size
            largest_size = max(bfs_extrapolated['sample_size'])
            bfs_time = bfs_extrapolated[bfs_extrapolated['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
            astar_time = astar_extrapolated[astar_extrapolated['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
            
            plt.annotate(f"{bfs_time:.1f}s", 
                       (largest_size, bfs_time), 
                       xytext=(5, 10), textcoords='offset points', 
                       fontsize=12, color='blue')
            plt.annotate(f"{astar_time:.1f}s", 
                       (largest_size, astar_time), 
                       xytext=(5, -15), textcoords='offset points', 
                       fontsize=12, color='green')
            
            # Calculate speed-up ratio
            speedup = bfs_time / astar_time if astar_time > 0 else float('inf')
            
            # Set title and labels
            title = f"BFS vs A* Performance on {cube_type.upper()}"
            if 'rubik2x2' in cube_type:
                title += " (2x2 Cube)"
            else:
                title += " (3x3 Cube)"
                
            plt.title(title + f"\nFor n={largest_size:,}: A* is {speedup:.1f}x faster than BFS", fontsize=16)
            plt.xlabel('Sample Size (n)', fontsize=14)
            plt.ylabel('Execution Time (seconds)', fontsize=14)
            
            # Set log scales for better visualization
            plt.xscale('log')
            plt.yscale('log')
            
            # Add grid and legend
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(fontsize=12)
            
            # Format axes
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
            
            # Save the figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis/figures/algorithm_comparison_{cube_type}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
            # Also save with a standard name
            standard_filename = f"analysis/figures/algorithm_comparison_{cube_type}_latest.png"
            plt.savefig(standard_filename, dpi=300, bbox_inches='tight')
            
            plt.close()
            
            print(f"Comparison plot saved to {filename} and {standard_filename}")
        else:
            print(f"Missing data for comparison on {cube_type}")

def plot_cube_type_comparison(data):
    """
    Create plots comparing 2x2 and 3x3 cubes for each algorithm
    
    Args:
        data: Dictionary with loaded DataFrames
    """
    algorithms = ['bfs', 'astar']
    
    for algorithm in algorithms:
        # Check if we have both 2x2 and 3x3 data for this algorithm
        if f"{algorithm}_rubik2x2" in data and f"{algorithm}_rubik3x3" in data:
            plt.figure(figsize=(12, 8))
            
            # Plot measured data points for both cube types
            cube2x2_measured = data[f"{algorithm}_rubik2x2"]['measured']
            cube3x3_measured = data[f"{algorithm}_rubik3x3"]['measured']
            
            plt.scatter(cube2x2_measured['sample_size'], cube2x2_measured['time_seconds'], 
                       s=100, marker='o', label='2x2 Cube Measured', color='purple')
            plt.scatter(cube3x3_measured['sample_size'], cube3x3_measured['time_seconds'], 
                       s=100, marker='s', label='3x3 Cube Measured', color='orange')
            
            # Plot extrapolated data points for both cube types
            cube2x2_extrapolated = data[f"{algorithm}_rubik2x2"]['extrapolated']
            cube3x3_extrapolated = data[f"{algorithm}_rubik3x3"]['extrapolated']
            
            # Create a smooth curve for best-fit model
            x = np.linspace(
                min(min(cube2x2_measured['sample_size']), min(cube3x3_measured['sample_size'])),
                max(max(cube2x2_extrapolated['sample_size']), max(cube3x3_extrapolated['sample_size'])),
                1000
            )
            
            # Find which model was used for each cube type
            cube2x2_model = cube2x2_extrapolated['model'].iloc[0]
            cube3x3_model = cube3x3_extrapolated['model'].iloc[0]
            
            # Plot extrapolated points
            plt.scatter(cube2x2_extrapolated['sample_size'], cube2x2_extrapolated['extrapolated_time_seconds'], 
                      s=150, marker='o', facecolors='none', edgecolors='purple', linewidth=2,
                      label=f'2x2 Extrapolated ({cube2x2_model})')
            plt.scatter(cube3x3_extrapolated['sample_size'], cube3x3_extrapolated['extrapolated_time_seconds'], 
                      s=150, marker='s', facecolors='none', edgecolors='orange', linewidth=2,
                      label=f'3x3 Extrapolated ({cube3x3_model})')
            
            # Add annotations for largest extrapolated size
            largest_size = max(cube2x2_extrapolated['sample_size'])
            cube2x2_time = cube2x2_extrapolated[cube2x2_extrapolated['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
            cube3x3_time = cube3x3_extrapolated[cube3x3_extrapolated['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
            
            plt.annotate(f"{cube2x2_time:.1f}s", 
                       (largest_size, cube2x2_time), 
                       xytext=(5, 10), textcoords='offset points', 
                       fontsize=12, color='purple')
            plt.annotate(f"{cube3x3_time:.1f}s", 
                       (largest_size, cube3x3_time), 
                       xytext=(5, -15), textcoords='offset points', 
                       fontsize=12, color='orange')
            
            # Calculate complexity ratio
            complexity_ratio = cube3x3_time / cube2x2_time if cube2x2_time > 0 else float('inf')
            
            # Set title and labels
            algorithm_name = "Breadth-First Search" if algorithm == "bfs" else "A* Search"
            plt.title(f"{algorithm_name} Performance: 2x2 vs 3x3 Cube\n"
                     f"For n={largest_size:,}: 3x3 is {complexity_ratio:.1f}x more complex than 2x2", 
                     fontsize=16)
            plt.xlabel('Sample Size (n)', fontsize=14)
            plt.ylabel('Execution Time (seconds)', fontsize=14)
            
            # Set log scales for better visualization
            plt.xscale('log')
            plt.yscale('log')
            
            # Add grid and legend
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(fontsize=12)
            
            # Format axes
            plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
            
            # Save the figure
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis/figures/cube_comparison_{algorithm}_{timestamp}.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            
            # Also save with a standard name
            standard_filename = f"analysis/figures/cube_comparison_{algorithm}_latest.png"
            plt.savefig(standard_filename, dpi=300, bbox_inches='tight')
            
            plt.close()
            
            print(f"Cube comparison plot saved to {filename} and {standard_filename}")
        else:
            print(f"Missing data for cube comparison on {algorithm}")

def create_complexity_summary_table(data):
    """
    Create a summary table of the best complexity models and extrapolated times
    
    Args:
        data: Dictionary with loaded DataFrames
    """
    # Prepare data for the table
    table_data = []
    
    algorithms = ['bfs', 'astar']
    cube_types = ['rubik2x2', 'rubik3x3']
    
    for algorithm in algorithms:
        for cube_type in cube_types:
            key = f"{algorithm}_{cube_type}"
            
            if key in data:
                # Get the model and largest extrapolated time
                model = data[key]['extrapolated']['model'].iloc[0]
                largest_size = max(data[key]['extrapolated']['sample_size'])
                time = data[key]['extrapolated'][data[key]['extrapolated']['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
                
                alg_name = "BFS" if algorithm == "bfs" else "A*"
                cube_name = "2x2" if "2x2" in cube_type else "3x3"
                
                table_data.append([alg_name, cube_name, model, largest_size, time])
    
    if table_data:
        # Create DataFrame
        df = pd.DataFrame(table_data, columns=[
            'Algorithm', 'Cube Type', 'Best Fit Model', 'Max Size', 'Extrapolated Time (s)'
        ])
        
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/data/complexity_summary_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        # Also save with a standard name
        standard_filename = f"analysis/data/complexity_summary_latest.csv"
        df.to_csv(standard_filename, index=False)
        
        print(f"\nComplexity summary saved to {filename} and {standard_filename}")
        print("\nComplexity Summary:")
        print(df.to_string(index=False))
    else:
        print("\nNo data available for complexity summary")

def plot_combined_comparison(data):
    """
    Create a single plot comparing all algorithms and cube types
    
    Args:
        data: Dictionary with loaded DataFrames
    """
    if len(data) >= 2:  # Need at least 2 datasets to compare
        plt.figure(figsize=(14, 10))
        
        # Define colors and markers
        colors = {
            'bfs_rubik2x2': 'blue',
            'bfs_rubik3x3': 'red',
            'astar_rubik2x2': 'green',
            'astar_rubik3x3': 'purple'
        }
        
        markers = {
            'bfs_rubik2x2': 'o',
            'bfs_rubik3x3': 's',
            'astar_rubik2x2': '^',
            'astar_rubik3x3': 'd'
        }
        
        labels = {
            'bfs_rubik2x2': 'BFS - 2x2 Cube',
            'bfs_rubik3x3': 'BFS - 3x3 Cube',
            'astar_rubik2x2': 'A* - 2x2 Cube',
            'astar_rubik3x3': 'A* - 3x3 Cube'
        }
        
        # Track min and max values for axis scaling
        min_size = float('inf')
        max_size = 0
        largest_extrapolated_time = 0
        
        # Plot all datasets
        for key, dataset in data.items():
            if key in colors:
                # Plot measured data
                measured = dataset['measured']
                plt.scatter(measured['sample_size'], measured['time_seconds'], 
                          s=100, marker=markers[key], label=f"{labels[key]} (Measured)", 
                          color=colors[key])
                
                # Plot extrapolated data
                extrapolated = dataset['extrapolated']
                plt.scatter(extrapolated['sample_size'], extrapolated['extrapolated_time_seconds'], 
                          s=150, marker=markers[key], facecolors='none', edgecolors=colors[key], 
                          linewidth=2, label=f"{labels[key]} (Extrapolated - {extrapolated['model'].iloc[0]})")
                
                # Update min/max tracking
                min_size = min(min_size, min(measured['sample_size']))
                max_size = max(max_size, max(extrapolated['sample_size']))
                
                # Add annotation for largest size
                largest_size = max(extrapolated['sample_size'])
                extrapolated_time = extrapolated[extrapolated['sample_size'] == largest_size]['extrapolated_time_seconds'].iloc[0]
                largest_extrapolated_time = max(largest_extrapolated_time, extrapolated_time)
                
                plt.annotate(f"{extrapolated_time:.1f}s", 
                           (largest_size, extrapolated_time), 
                           xytext=(5, 5), textcoords='offset points', 
                           fontsize=10, color=colors[key])
        
        # Set title and labels
        plt.title(f"Algorithm Performance Comparison\nExtrapolated to {largest_size:,} samples", fontsize=16)
        plt.xlabel('Sample Size (n)', fontsize=14)
        plt.ylabel('Execution Time (seconds)', fontsize=14)
        
        # Set log scales for better visualization
        plt.xscale('log')
        plt.yscale('log')
        
        # Add grid and legend
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(fontsize=12)
        
        # Format axes
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
        
        # Save the figure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis/figures/combined_comparison_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        
        # Also save with a standard name
        standard_filename = f"analysis/figures/combined_comparison_latest.png"
        plt.savefig(standard_filename, dpi=300, bbox_inches='tight')
        
        plt.close()
        
        print(f"Combined comparison plot saved to {filename} and {standard_filename}")
    else:
        print("Not enough data for combined comparison plot")

def main():
    print("Loading benchmark data...")
    data = load_data()
    
    if data:
        print("\nCreating comparison plots...")
        plot_algorithm_comparison(data)
        plot_cube_type_comparison(data)
        plot_combined_comparison(data)
        create_complexity_summary_table(data)
        print("\nAll visualizations completed!")
    else:
        print("No benchmark data found. Run regression_benchmark.py first.")

if __name__ == "__main__":
    main() 