import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
import matplotlib

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

# Sample data (in a real scenario, you would load this from actual benchmarks)
# These are mock data for illustration purposes

# 1. BFS Performance Data
bfs_depth = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
bfs_time_2x2 = np.array([0.01, 0.05, 0.2, 0.8, 3.2, 12.8, 51.2, 204.8, 819.2])
bfs_time_3x3 = np.array([0.02, 0.1, 0.5, 2.5, 12.5, 62.5, 312.5, 1562.5, 7812.5])
bfs_memory_2x2 = np.array([1, 8, 64, 512, 4096, 32768, 262144, 2097152, 16777216]) / 1024  # Convert to MB
bfs_memory_3x3 = np.array([2, 32, 512, 8192, 131072, 2097152, 33554432, 536870912, 8589934592]) / 1024  # Convert to MB

# 2. A* Performance Data
astar_depth = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
astar_time_2x2 = np.array([0.01, 0.03, 0.1, 0.3, 0.9, 2.7, 8.1, 24.3, 72.9, 218.7, 656.1, 1968.3])
astar_time_3x3 = np.array([0.02, 0.08, 0.32, 1.28, 5.12, 20.48, 81.92, 327.68, 1310.72, 5242.88, float('nan'), float('nan')])
astar_memory_2x2 = np.array([1, 6, 36, 216, 1296, 7776, 46656, 279936, 1679616, 10077696, 60466176, 362797056]) / 1024  # Convert to MB
astar_memory_3x3 = np.array([2, 20, 200, 2000, 20000, 200000, 2000000, 20000000, 200000000, 2000000000, float('nan'), float('nan')]) / 1024  # Convert to MB

# 3. Algorithm Comparison Data
depths = np.array([1, 2, 3, 4, 5, 6, 7, 8])
bfs_time_comparison = np.array([0.01, 0.08, 0.5, 3.0, 18.0, 108.0, 648.0, 3888.0])
astar_time_comparison = np.array([0.01, 0.05, 0.25, 1.25, 6.25, 31.25, 156.25, 781.25])
bfs_memory_comparison = np.array([1, 18, 324, 5832, 104976, 1889568, 34012224, 612220032]) / 1024  # Convert to MB
astar_memory_comparison = np.array([1, 10, 100, 1000, 10000, 100000, 1000000, 10000000]) / 1024  # Convert to MB

# 4. Success Rate Data
success_depths = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
bfs_2x2_success = np.array([100, 100, 100, 100, 100, 100, 95, 75, 30, 5, 0, 0])
bfs_3x3_success = np.array([100, 100, 100, 100, 95, 80, 40, 10, 0, 0, 0, 0])
astar_2x2_success = np.array([100, 100, 100, 100, 100, 100, 100, 95, 85, 60, 25, 5])
astar_3x3_success = np.array([100, 100, 100, 100, 100, 95, 85, 65, 35, 10, 0, 0])

# 5. State Space Data
cube_types = ['2x2', '3x3']
states = [3.6e6, 4.3e19]  # 3.6 million for 2x2, 4.3 × 10^19 for 3x3
gods_number = [11, 20]  # 11 for 2x2, 20 for 3x3

# 6. State Space Reduction Data
reduction_techniques = ['No Reduction', 'Move Pruning', 'Symmetry Reduction', 'Combined']
reduction_effectiveness = np.array([1.0, 0.6, 0.4, 0.25])  # Relative size after reduction (1.0 = no reduction)


# Function to generate and save plots
def generate_plots():
    """Generate all visualization plots and save them to files."""
    
    # 1. BFS Performance Plot
    plt.figure(figsize=(12, 8))
    
    # Create log-scale plot for time
    plt.subplot(2, 1, 1)
    plt.semilogy(bfs_depth, bfs_time_2x2, 'o-', label='Rubik 2x2', linewidth=2)
    plt.semilogy(bfs_depth, bfs_time_3x3, 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Thời gian tìm kiếm (giây)')
    plt.title('Hiệu suất thời gian của thuật toán BFS')
    plt.legend()
    
    # Create log-scale plot for memory
    plt.subplot(2, 1, 2)
    plt.semilogy(bfs_depth, bfs_memory_2x2, 'o-', label='Rubik 2x2', linewidth=2)
    plt.semilogy(bfs_depth, bfs_memory_3x3, 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Bộ nhớ sử dụng (MB)')
    plt.title('Sử dụng bộ nhớ của thuật toán BFS')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/bfs_performance.png', dpi=300, bbox_inches='tight')
    
    # 2. A* Performance Plot
    plt.figure(figsize=(12, 8))
    
    # Create log-scale plot for time
    plt.subplot(2, 1, 1)
    plt.semilogy(astar_depth, astar_time_2x2, 'o-', label='Rubik 2x2', linewidth=2)
    plt.semilogy(astar_depth, astar_time_3x3, 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Thời gian tìm kiếm (giây)')
    plt.title('Hiệu suất thời gian của thuật toán A*')
    plt.legend()
    
    # Create log-scale plot for memory
    plt.subplot(2, 1, 2)
    plt.semilogy(astar_depth, astar_memory_2x2, 'o-', label='Rubik 2x2', linewidth=2)
    plt.semilogy(astar_depth, astar_memory_3x3, 's-', label='Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Bộ nhớ sử dụng (MB)')
    plt.title('Sử dụng bộ nhớ của thuật toán A*')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/astar_performance.png', dpi=300, bbox_inches='tight')
    
    # 3. Algorithm Time Comparison
    plt.figure(figsize=(10, 6))
    
    plt.semilogy(depths, bfs_time_comparison, 'o-', label='BFS', linewidth=2)
    plt.semilogy(depths, astar_time_comparison, 's-', label='A*', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Thời gian tìm kiếm (giây)')
    plt.title('So sánh thời gian thực thi giữa các thuật toán (Rubik 3x3)')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/algorithm_time_comparison.png', dpi=300, bbox_inches='tight')
    
    # 4. Algorithm Memory Comparison
    plt.figure(figsize=(10, 6))
    
    plt.semilogy(depths, bfs_memory_comparison, 'o-', label='BFS', linewidth=2)
    plt.semilogy(depths, astar_memory_comparison, 's-', label='A*', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Bộ nhớ sử dụng (MB)')
    plt.title('So sánh sử dụng bộ nhớ giữa các thuật toán (Rubik 3x3)')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/algorithm_memory_comparison.png', dpi=300, bbox_inches='tight')
    
    # 5. Success Rate by Depth
    plt.figure(figsize=(10, 6))
    
    plt.plot(success_depths, bfs_2x2_success, 'o-', label='BFS - Rubik 2x2', linewidth=2)
    plt.plot(success_depths, bfs_3x3_success, 's-', label='BFS - Rubik 3x3', linewidth=2)
    plt.plot(success_depths, astar_2x2_success, '^-', label='A* - Rubik 2x2', linewidth=2)
    plt.plot(success_depths, astar_3x3_success, 'D-', label='A* - Rubik 3x3', linewidth=2)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.xlabel('Độ sâu của lời giải (số bước)')
    plt.ylabel('Tỷ lệ thành công (%)')
    plt.title('Tỷ lệ thành công theo độ sâu')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/figures/success_rate_by_depth.png', dpi=300, bbox_inches='tight')
    
    # 6. State Space Complexity
    plt.figure(figsize=(10, 6))
    
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
    
    # 7. State Space Reduction
    plt.figure(figsize=(10, 6))
    
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
    
    # Additional combined comparison
    plt.figure(figsize=(14, 10))
    
    # Create a 2x2 grid
    gs = plt.GridSpec(2, 2, hspace=0.3, wspace=0.3)
    
    # Time comparison (top left)
    ax1 = plt.subplot(gs[0, 0])
    ax1.semilogy(depths, bfs_time_comparison, 'o-', label='BFS', linewidth=2)
    ax1.semilogy(depths, astar_time_comparison, 's-', label='A*', linewidth=2)
    ax1.grid(True, which="both", ls="-", alpha=0.2)
    ax1.set_xlabel('Độ sâu (số bước)')
    ax1.set_ylabel('Thời gian (giây)')
    ax1.set_title('So sánh thời gian')
    ax1.legend()
    
    # Memory comparison (top right)
    ax2 = plt.subplot(gs[0, 1])
    ax2.semilogy(depths, bfs_memory_comparison, 'o-', label='BFS', linewidth=2)
    ax2.semilogy(depths, astar_memory_comparison, 's-', label='A*', linewidth=2)
    ax2.grid(True, which="both", ls="-", alpha=0.2)
    ax2.set_xlabel('Độ sâu (số bước)')
    ax2.set_ylabel('Bộ nhớ (MB)')
    ax2.set_title('So sánh bộ nhớ')
    ax2.legend()
    
    # Success rate (bottom left)
    ax3 = plt.subplot(gs[1, 0])
    ax3.plot(success_depths, bfs_2x2_success, 'o-', label='BFS - 2x2', linewidth=2)
    ax3.plot(success_depths, astar_2x2_success, '^-', label='A* - 2x2', linewidth=2)
    ax3.grid(True, which="both", ls="-", alpha=0.2)
    ax3.set_xlabel('Độ sâu (số bước)')
    ax3.set_ylabel('Tỷ lệ thành công (%)')
    ax3.set_title('Tỷ lệ giải thành công - Rubik 2x2')
    ax3.legend()
    
    # State space reduction (bottom right)
    ax4 = plt.subplot(gs[1, 1])
    bars = ax4.bar(reduction_techniques, 100 * (1 - reduction_effectiveness), color=['#3498db', '#2ecc71', '#9b59b6', '#e74c3c'])
    ax4.set_ylabel('Giảm không gian tìm kiếm (%)')
    ax4.set_title('Kỹ thuật giảm không gian trạng thái')
    ax4.set_ylim(0, 100)
    
    plt.suptitle('Phân tích tổng hợp hiệu quả các thuật toán trên Rubik Cube', fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust layout to make room for the suptitle
    plt.savefig('analysis/figures/combined_analysis.png', dpi=300, bbox_inches='tight')
    
    print("All visualizations have been successfully generated in 'analysis/figures/' directory.")


if __name__ == "__main__":
    generate_plots() 