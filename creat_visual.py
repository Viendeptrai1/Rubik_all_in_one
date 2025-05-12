import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import os
import time
from testmodel3x3 import DeepCubeASolver, scramble_cube, verify_solution

def run_tests_and_visualize():
    # Set up plot style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set(font_scale=1.2)
    
    # Create figure for results
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Load solver
    solver = DeepCubeASolver(use_branched=True)
    
    if not solver.load_model():
        print("Failed to load model. Exiting.")
        return None
    
    print("Model loaded successfully")
    
    # Test parameters - up to depth 10 as requested
    test_depths = [1, 3, 5, 7, 10]
    num_tests = 5
    timeout = 120  # 2 minutes timeout per test
    
    # Results storage
    success_rates = []
    avg_moves = []
    avg_times = []
    
    # Run tests at each depth
    for depth in test_depths:
        print(f"\nTesting {depth}-move scrambles:")
        success_count = 0
        total_moves = 0
        total_time = 0
        
        for test in range(num_tests):
            scrambled_state, moves_applied = scramble_cube(depth)
            print(f"Test {test + 1}/{num_tests}: {len(moves_applied)} moves")
            print(f"Scramble sequence: {' '.join(moves_applied)}")
            
            start_time = time.time()
            solution = solver.solve(scrambled_state, max_moves=depth*2, timeout=timeout)
            solve_time = time.time() - start_time
            
            if solution:
                is_valid = verify_solution(scrambled_state, solution)
                if is_valid:
                    success_count += 1
                    total_moves += len(solution)
                    total_time += solve_time
                    print(f"✓ Solution found: {len(solution)} moves in {solve_time:.2f}s")
                else:
                    print("× Invalid solution found")
            else:
                print("× No solution found")
        
        # Calculate metrics
        success_rate = success_count/num_tests*100
        moves_avg = total_moves/success_count if success_count > 0 else 0
        time_avg = total_time/success_count if success_count > 0 else 0
        
        success_rates.append(success_rate)
        avg_moves.append(moves_avg)
        avg_times.append(time_avg)
        
        print(f"Depth {depth} - Success: {success_rate:.1f}%, Moves: {moves_avg:.1f}, Time: {time_avg:.2f}s")
    
    # Plot 1: Success rates at different depths
    axes[0, 0].bar(test_depths, success_rates, color='royalblue')
    axes[0, 0].set_title('Success Rate by Scramble Depth')
    axes[0, 0].set_xlabel('Scramble Depth')
    axes[0, 0].set_ylabel('Success Rate (%)')
    axes[0, 0].set_ylim(0, 105)
    
    # Plot 2: Average moves at different depths
    axes[0, 1].plot(test_depths, avg_moves, 'o-', color='forestgreen', linewidth=2)
    axes[0, 1].set_title('Average Solution Length by Scramble Depth')
    axes[0, 1].set_xlabel('Scramble Depth')
    axes[0, 1].set_ylabel('Number of Moves')
    
    # Plot 3: Average solution time at different depths
    axes[1, 0].plot(test_depths, avg_times, 'o-', color='firebrick', linewidth=2)
    axes[1, 0].set_title('Average Solution Time by Scramble Depth')
    axes[1, 0].set_xlabel('Scramble Depth')
    axes[1, 0].set_ylabel('Time (seconds)')
    
    # Plot 4: Comparison of optimal vs actual solution length
    optimal_estimate = [depth * 1.1 for depth in test_depths]  # Estimation of optimal solution length
    width = 0.35
    x = np.arange(len(test_depths))
    axes[1, 1].bar(x - width/2, optimal_estimate, width, label='Estimated Optimal', color='lightgreen')
    axes[1, 1].bar(x + width/2, avg_moves, width, label='Actual Solution', color='darkgreen')
    axes[1, 1].set_title('Optimal vs Actual Solution Length')
    axes[1, 1].set_xlabel('Scramble Depth')
    axes[1, 1].set_ylabel('Number of Moves')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(test_depths)
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('rubik_solver_results.png', dpi=300)
    plt.show()
    
    return {
        'depths': test_depths,
        'success_rates': success_rates,
        'avg_moves': avg_moves,
        'avg_times': avg_times
    }

if __name__ == "__main__":
    run_tests_and_visualize()