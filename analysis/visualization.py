import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
import matplotlib
import glob

# Set the style for more professional-looking graphs
plt.style.use('seaborn-v0_8-whitegrid')
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.labelsize'] = 14
matplotlib.rcParams['axes.titlesize'] = 18
matplotlib.rcParams['xtick.labelsize'] = 12
matplotlib.rcParams['ytick.labelsize'] = 12
matplotlib.rcParams['legend.fontsize'] = 12

# Create output directory if it doesn't exist
if not os.path.exists('analysis/figures'):
    os.makedirs('analysis/figures')

def load_benchmark_data():
    """
    Load benchmark data from CSV files
    
    Returns:
        Dictionary containing DataFrames for each algorithm and cube type
    """
    data = {}
    
    # Check for latest result files
    for algo in ['bfs', 'astar']:
        for cube_type in ['rubik2x2', 'rubik3x3']:
            filename = f"analysis/data/{algo}_{cube_type}_latest.csv"
            if os.path.exists(filename):
                data[f"{algo}_{cube_type}"] = pd.read_csv(filename)
            else:
                print(f"Warning: {filename} not found. Run algorithm_benchmark.py first.")
                # Create empty dataframe with the expected columns
                data[f"{algo}_{cube_type}"] = pd.DataFrame({
                    'depth': [],
                    'time_seconds': [],
                    'memory_mb': [],
                    'success_rate': [],
                    'nodes_expanded': []
                })
    
    return data

def generate_bfs_performance_plots(data):
    """Generate BFS performance plots"""
    plt.figure(figsize=(12, 8))
    
    # Get the data
    bfs_2x2 = data['bfs_rubik2x2']
    bfs_3x3 = data['bfs_rubik3x3']
    
    # Create log-scale plot for time
    plt.subplot(2, 1, 1)
    if not bfs_2x2.empty:
        plt.semilogy(bfs_2x2['depth'], bfs_2x2['time_seconds'], 'o-', label='Rubik 2x2', linewidth=2)
    if not bfs_3x3.empty:
        plt.semilogy(bfs_3x3['depth'], bfs_3x3['time_seconds'], 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Thời gian tìm kiếm (giây)')
    plt.title('Hiệu suất thời gian của thuật toán BFS')
    plt.legend()
    
    # Create log-scale plot for memory
    plt.subplot(2, 1, 2)
    if not bfs_2x2.empty:
        plt.semilogy(bfs_2x2['depth'], bfs_2x2['memory_mb'], 'o-', label='Rubik 2x2', linewidth=2)
    if not bfs_3x3.empty:
        plt.semilogy(bfs_3x3['depth'], bfs_3x3['memory_mb'], 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Bộ nhớ sử dụng (MB)')
    plt.title('Sử dụng bộ nhớ của thuật toán BFS')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/bfs_performance.png', dpi=300, bbox_inches='tight')
    print("Generated BFS performance plots")

def generate_astar_performance_plots(data):
    """Generate A* performance plots"""
    plt.figure(figsize=(12, 8))
    
    # Get the data
    astar_2x2 = data['astar_rubik2x2']
    astar_3x3 = data['astar_rubik3x3']
    
    # Create log-scale plot for time
    plt.subplot(2, 1, 1)
    if not astar_2x2.empty:
        plt.semilogy(astar_2x2['depth'], astar_2x2['time_seconds'], 'o-', label='Rubik 2x2', linewidth=2)
    if not astar_3x3.empty:
        plt.semilogy(astar_3x3['depth'], astar_3x3['time_seconds'], 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Thời gian tìm kiếm (giây)')
    plt.title('Hiệu suất thời gian của thuật toán A*')
    plt.legend()
    
    # Create log-scale plot for memory
    plt.subplot(2, 1, 2)
    if not astar_2x2.empty:
        plt.semilogy(astar_2x2['depth'], astar_2x2['memory_mb'], 'o-', label='Rubik 2x2', linewidth=2)
    if not astar_3x3.empty:
        plt.semilogy(astar_3x3['depth'], astar_3x3['memory_mb'], 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Bộ nhớ sử dụng (MB)')
    plt.title('Sử dụng bộ nhớ của thuật toán A*')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/astar_performance.png', dpi=300, bbox_inches='tight')
    print("Generated A* performance plots")

def generate_algorithm_time_comparison(data):
    """Generate algorithm time comparison plot"""
    plt.figure(figsize=(10, 6))
    
    # Get the data
    bfs_3x3 = data['bfs_rubik3x3']
    astar_3x3 = data['astar_rubik3x3']
    
    # Find the common depths to compare
    if not bfs_3x3.empty and not astar_3x3.empty:
        # Get common depths
        common_depths = sorted(list(set(bfs_3x3['depth']).intersection(set(astar_3x3['depth']))))
        
        if common_depths:
            # Filter data for common depths
            bfs_time = bfs_3x3[bfs_3x3['depth'].isin(common_depths)].sort_values('depth')
            astar_time = astar_3x3[astar_3x3['depth'].isin(common_depths)].sort_values('depth')
            
            plt.semilogy(bfs_time['depth'], bfs_time['time_seconds'], 'o-', label='BFS', linewidth=2)
            plt.semilogy(astar_time['depth'], astar_time['time_seconds'], 's-', label='A*', linewidth=2)
            plt.grid(True, which="both", ls="-", alpha=0.2)
            plt.xlabel('Độ sâu của lời giải (số bước)')
            plt.ylabel('Thời gian tìm kiếm (giây)')
            plt.title('So sánh thời gian thực thi giữa các thuật toán (Rubik 3x3)')
            plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/algorithm_time_comparison.png', dpi=300, bbox_inches='tight')
    print("Generated algorithm time comparison plot")

def generate_algorithm_memory_comparison(data):
    """Generate algorithm memory comparison plot"""
    plt.figure(figsize=(10, 6))
    
    # Get the data
    bfs_3x3 = data['bfs_rubik3x3']
    astar_3x3 = data['astar_rubik3x3']
    
    # Find the common depths to compare
    if not bfs_3x3.empty and not astar_3x3.empty:
        # Get common depths
        common_depths = sorted(list(set(bfs_3x3['depth']).intersection(set(astar_3x3['depth']))))
        
        if common_depths:
            # Filter data for common depths
            bfs_memory = bfs_3x3[bfs_3x3['depth'].isin(common_depths)].sort_values('depth')
            astar_memory = astar_3x3[astar_3x3['depth'].isin(common_depths)].sort_values('depth')
            
            plt.semilogy(bfs_memory['depth'], bfs_memory['memory_mb'], 'o-', label='BFS', linewidth=2)
            plt.semilogy(astar_memory['depth'], astar_memory['memory_mb'], 's-', label='A*', linewidth=2)
            plt.grid(True, which="both", ls="-", alpha=0.2)
            plt.xlabel('Độ sâu của lời giải (số bước)')
            plt.ylabel('Bộ nhớ sử dụng (MB)')
            plt.title('So sánh sử dụng bộ nhớ giữa các thuật toán (Rubik 3x3)')
            plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/algorithm_memory_comparison.png', dpi=300, bbox_inches='tight')
    print("Generated algorithm memory comparison plot")

def generate_success_rate_plots(data):
    """Generate success rate plots"""
    plt.figure(figsize=(10, 6))
    
    # Get the data
    bfs_2x2 = data['bfs_rubik2x2']
    bfs_3x3 = data['bfs_rubik3x3']
    astar_2x2 = data['astar_rubik2x2']
    astar_3x3 = data['astar_rubik3x3']
    
    if not bfs_2x2.empty:
        plt.plot(bfs_2x2['depth'], bfs_2x2['success_rate'], 'o-', label='BFS - Rubik 2x2', linewidth=2)
    if not bfs_3x3.empty:
        plt.plot(bfs_3x3['depth'], bfs_3x3['success_rate'], 's-', label='BFS - Rubik 3x3', linewidth=2)
    if not astar_2x2.empty:
        plt.plot(astar_2x2['depth'], astar_2x2['success_rate'], '^-', label='A* - Rubik 2x2', linewidth=2)
    if not astar_3x3.empty:
        plt.plot(astar_3x3['depth'], astar_3x3['success_rate'], 'D-', label='A* - Rubik 3x3', linewidth=2)
    
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Tỷ lệ thành công (%)')
    plt.title('Tỷ lệ thành công theo độ sâu')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/success_rate_by_depth.png', dpi=300, bbox_inches='tight')
    print("Generated success rate plots")

def generate_state_space_complexity():
    """Generate state space complexity plot"""
    plt.figure(figsize=(10, 6))
    
    # State space data (fixed theoretical values)
    cube_types = ['2x2', '3x3']
    states = [3.6e6, 4.3e19]  # 3.6 million for 2x2, 4.3 × 10^19 for 3x3
    gods_number = [11, 20]  # 11 for 2x2, 20 for 3x3
    
    ax = plt.subplot(111)
    bars = ax.bar(cube_types, states, color=['#3498db', '#e74c3c'])
    
    # Add God's number markers
    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                 f"God's Number: {gods_number[i]}",
                 ha='center', va='center', color='white', fontweight='bold')
    
    plt.yscale('log')
    plt.ylabel('Số lượng trạng thái (log scale)')
    plt.title('Độ phức tạp không gian trạng thái')
    
    # Format y-axis to avoid scientific notation
    def format_func(value, tick_number):
        if value == 0:
            return '0'
        elif value < 1e6:
            return f'{int(value):,}'
        else:
            # Use scientific notation with appropriate formatting
            exponent = int(np.log10(value))
            mantissa = value / 10**exponent
            return f'{mantissa:.1f} × 10^{exponent}'
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
    
    plt.tight_layout()
    plt.savefig('analysis/figures/state_space_complexity.png', dpi=300, bbox_inches='tight')
    print("Generated state space complexity plot")

def generate_state_space_reduction():
    """Generate state space reduction plot"""
    plt.figure(figsize=(10, 6))
    
    # State space reduction data (approximate values from literature)
    reduction_techniques = ['No Reduction', 'Move Pruning', 'Symmetry Reduction', 'Combined']
    reduction_effectiveness = np.array([1.0, 0.6, 0.4, 0.25])  # Relative size after reduction (1.0 = no reduction)
    
    bars = plt.bar(reduction_techniques, 100 * (1 - reduction_effectiveness), color=['#3498db', '#2ecc71', '#9b59b6', '#e74c3c'])
    
    # Add percentage labels
    for i, bar in enumerate(bars):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f"{int(100 * (1 - reduction_effectiveness[i]))}%",
                 ha='center', va='bottom')
    
    plt.ylabel('Phần trăm giảm không gian tìm kiếm (%)')
    plt.title('Hiệu quả của các kỹ thuật giảm không gian trạng thái')
    plt.ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig('analysis/figures/state_space_reduction.png', dpi=300, bbox_inches='tight')
    print("Generated state space reduction plot")

def generate_combined_analysis(data):
    """Generate combined analysis dashboard"""
    plt.figure(figsize=(14, 10))
    
    # Get the data
    bfs_2x2 = data['bfs_rubik2x2']
    astar_2x2 = data['astar_rubik2x2']
    bfs_3x3 = data['bfs_rubik3x3']
    astar_3x3 = data['astar_rubik3x3']
    
    # Create a 2x2 grid
    gs = plt.GridSpec(2, 2, hspace=0.3, wspace=0.3)
    
    # Time comparison (top left)
    ax1 = plt.subplot(gs[0, 0])
    if not bfs_3x3.empty and not astar_3x3.empty:
        # Get common depths
        common_depths = sorted(list(set(bfs_3x3['depth']).intersection(set(astar_3x3['depth']))))
        
        if common_depths:
            # Filter data for common depths
            bfs_time = bfs_3x3[bfs_3x3['depth'].isin(common_depths)].sort_values('depth')
            astar_time = astar_3x3[astar_3x3['depth'].isin(common_depths)].sort_values('depth')
            
            ax1.semilogy(bfs_time['depth'], bfs_time['time_seconds'], 'o-', label='BFS', linewidth=2)
            ax1.semilogy(astar_time['depth'], astar_time['time_seconds'], 's-', label='A*', linewidth=2)
    
    ax1.grid(True, which="both", ls="-", alpha=0.2)
    ax1.set_xlabel('Độ sâu (số bước)')
    ax1.set_ylabel('Thời gian (giây)')
    ax1.set_title('So sánh thời gian')
    ax1.legend()
    
    # Memory comparison (top right)
    ax2 = plt.subplot(gs[0, 1])
    if not bfs_3x3.empty and not astar_3x3.empty:
        # Get common depths
        common_depths = sorted(list(set(bfs_3x3['depth']).intersection(set(astar_3x3['depth']))))
        
        if common_depths:
            # Filter data for common depths
            bfs_memory = bfs_3x3[bfs_3x3['depth'].isin(common_depths)].sort_values('depth')
            astar_memory = astar_3x3[astar_3x3['depth'].isin(common_depths)].sort_values('depth')
            
            ax2.semilogy(bfs_memory['depth'], bfs_memory['memory_mb'], 'o-', label='BFS', linewidth=2)
            ax2.semilogy(astar_memory['depth'], astar_memory['memory_mb'], 's-', label='A*', linewidth=2)
    
    ax2.grid(True, which="both", ls="-", alpha=0.2)
    ax2.set_xlabel('Độ sâu (số bước)')
    ax2.set_ylabel('Bộ nhớ (MB)')
    ax2.set_title('So sánh bộ nhớ')
    ax2.legend()
    
    # Success rate (bottom left)
    ax3 = plt.subplot(gs[1, 0])
    if not bfs_2x2.empty:
        ax3.plot(bfs_2x2['depth'], bfs_2x2['success_rate'], 'o-', label='BFS - 2x2', linewidth=2)
    if not astar_2x2.empty:
        ax3.plot(astar_2x2['depth'], astar_2x2['success_rate'], '^-', label='A* - 2x2', linewidth=2)
    
    ax3.grid(True, which="both", ls="-", alpha=0.2)
    ax3.set_xlabel('Độ sâu (số bước)')
    ax3.set_ylabel('Tỷ lệ thành công (%)')
    ax3.set_title('Tỷ lệ giải thành công - Rubik 2x2')
    ax3.legend()
    
    # State space reduction (bottom right)
    ax4 = plt.subplot(gs[1, 1])
    reduction_techniques = ['No Reduction', 'Move Pruning', 'Symmetry Reduction', 'Combined']
    reduction_effectiveness = np.array([1.0, 0.6, 0.4, 0.25])
    bars = ax4.bar(reduction_techniques, 100 * (1 - reduction_effectiveness), color=['#3498db', '#2ecc71', '#9b59b6', '#e74c3c'])
    ax4.set_ylabel('Giảm không gian tìm kiếm (%)')
    ax4.set_title('Kỹ thuật giảm không gian trạng thái')
    ax4.set_ylim(0, 100)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax4.get_xticklabels(), rotation=30, ha='right')
    
    plt.suptitle('Phân tích tổng hợp hiệu quả các thuật toán trên Rubik Cube', fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make room for the suptitle
    plt.savefig('analysis/figures/combined_analysis.png', dpi=300, bbox_inches='tight')
    print("Generated combined analysis dashboard")

def generate_all_visualizations():
    """Generate all visualization plots"""
    print("Loading benchmark data...")
    data = load_benchmark_data()
    
    print("Generating visualizations...")
    generate_bfs_performance_plots(data)
    generate_astar_performance_plots(data)
    generate_algorithm_time_comparison(data)
    generate_algorithm_memory_comparison(data)
    generate_success_rate_plots(data)
    generate_state_space_complexity()
    generate_state_space_reduction()
    generate_combined_analysis(data)
    
    print("All visualizations have been successfully generated in 'analysis/figures/' directory.")

if __name__ == "__main__":
    generate_all_visualizations() 