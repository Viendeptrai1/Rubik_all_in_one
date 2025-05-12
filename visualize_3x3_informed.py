import matplotlib.pyplot as plt
import numpy as np
import time
import os
import seaborn as sns
from RubikState.rubik_solver_3x3 import a_star_search_3x3, greedy_best_first_search_3x3, ida_star_search_3x3, hill_climbing_max_search_3x3, hill_climbing_random_search_3x3
from RubikState.rubik_chen import RubikState, SOLVED_STATE_3x3, MOVE_NAMES

def generate_scrambled_states(depths, num_samples=3):
    """Generate scrambled states for each depth"""
    scrambled_states = {}
    for depth in depths:
        states = []
        for _ in range(num_samples):
            state = SOLVED_STATE_3x3
            moves_applied = []
            
            for _ in range(depth):
                # Avoid moves that undo the previous move
                valid_moves = list(MOVE_NAMES)
                if moves_applied:
                    last_move = moves_applied[-1]
                    if last_move.endswith("'"):
                        opposite = last_move[:-1]  # Remove the '
                    else:
                        opposite = last_move + "'"
                    
                    if opposite in valid_moves:
                        valid_moves.remove(opposite)
                
                move = np.random.choice(valid_moves)
                state = state.apply_move(move)
                moves_applied.append(move)
                
            states.append((state, moves_applied))
        scrambled_states[depth] = states
    return scrambled_states

def run_algorithms(scrambled_states, depths, time_limit=30):
    """Run informed search algorithms on scrambled states"""
    algorithms = {
        "A*": a_star_search_3x3,
        "Greedy Best-First": greedy_best_first_search_3x3,
        "IDA*": ida_star_search_3x3,
        "Hill Climbing (Max)": hill_climbing_max_search_3x3,
        "Hill Climbing (Random)": hill_climbing_random_search_3x3
    }
    
    results = {}
    
    for alg_name, alg_func in algorithms.items():
        print(f"Running {alg_name}...")
        results[alg_name] = {
            'success_rate': [],
            'solution_length': [],
            'time_taken': [],
            'nodes_explored': []
        }
        
        for depth in depths:
            print(f"  Depth {depth}...")
            successes = 0
            total_length = 0
            total_time = 0
            total_nodes = 0
            
            for state, _ in scrambled_states[depth]:
                solution, nodes, time_taken, stats = alg_func(state, time_limit=time_limit, return_stats=True)
                
                if solution is not None:
                    successes += 1
                    total_length += len(solution)
                    total_time += time_taken
                    total_nodes += nodes
            
            # Calculate averages
            success_rate = successes / len(scrambled_states[depth]) * 100
            avg_length = total_length / successes if successes > 0 else 0
            avg_time = total_time / successes if successes > 0 else 0
            avg_nodes = total_nodes / successes if successes > 0 else 0
            
            # Store results
            results[alg_name]['success_rate'].append(success_rate)
            results[alg_name]['solution_length'].append(avg_length)
            results[alg_name]['time_taken'].append(avg_time)
            results[alg_name]['nodes_explored'].append(avg_nodes)
            
            print(f"    Success rate: {success_rate:.1f}%, Avg length: {avg_length:.1f}, "
                  f"Avg time: {avg_time:.3f}s, Avg nodes: {avg_nodes:.1f}")
    
    return results

def create_visualizations(results, depths):
    """Create visualization charts for informed search results"""
    sns.set(style="whitegrid")
    colors = sns.color_palette("husl", len(results))
    
    plt.figure(figsize=(20, 15))
    
    # 1. Success Rate
    plt.subplot(2, 2, 1)
    for i, (alg, data) in enumerate(results.items()):
        plt.plot(depths, data['success_rate'], marker='o', linewidth=2, 
                 label=alg, color=colors[i])
    plt.title('Success Rate by Scramble Depth', fontsize=16)
    plt.xlabel('Scramble Depth', fontsize=14)
    plt.ylabel('Success Rate (%)', fontsize=14)
    plt.ylim(0, 105)
    plt.xticks(depths)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # 2. Solution Length
    plt.subplot(2, 2, 2)
    for i, (alg, data) in enumerate(results.items()):
        plt.plot(depths, data['solution_length'], marker='o', linewidth=2, 
                 label=alg, color=colors[i])
    plt.title('Average Solution Length by Scramble Depth', fontsize=16)
    plt.xlabel('Scramble Depth', fontsize=14)
    plt.ylabel('Solution Length (moves)', fontsize=14)
    plt.xticks(depths)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # 3. Time Taken
    plt.subplot(2, 2, 3)
    for i, (alg, data) in enumerate(results.items()):
        plt.plot(depths, data['time_taken'], marker='o', linewidth=2, 
                 label=alg, color=colors[i])
    plt.title('Average Solution Time by Scramble Depth', fontsize=16)
    plt.xlabel('Scramble Depth', fontsize=14)
    plt.ylabel('Time (seconds)', fontsize=14)
    plt.xticks(depths)
    plt.legend(fontsize=12)
    plt.grid(True)
    
    # 4. Nodes Explored
    plt.subplot(2, 2, 4)
    for i, (alg, data) in enumerate(results.items()):
        plt.plot(depths, data['nodes_explored'], marker='o', linewidth=2, 
                 label=alg, color=colors[i])
    plt.title('Average Nodes Explored by Scramble Depth', fontsize=16)
    plt.xlabel('Scramble Depth', fontsize=14)
    plt.ylabel('Number of Nodes', fontsize=14)
    plt.xticks(depths)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.yscale('log')
    
    plt.tight_layout()
    
    # Create directory if it doesn't exist
    os.makedirs('visualizations', exist_ok=True)
    
    # Save the figure
    plt.savefig('visualizations/3x3_informed_search.png', dpi=300)
    print(f"Visualization saved to 'visualizations/3x3_informed_search.png'")
    
    return plt

if __name__ == "__main__":
    print("Rubik's Cube 3x3 - Informed Search Algorithms Visualization")
    print("==========================================================")
    
    # Define depths to test
    depths = [1, 2, 3, 4]
    
    # Generate scrambled states
    print("Generating scrambled states...")
    scrambled_states = generate_scrambled_states(depths)
    
    # Run algorithms
    print("\nRunning algorithms...")
    results = run_algorithms(scrambled_states, depths)
    
    # Create visualizations
    print("\nCreating visualizations...")
    plt = create_visualizations(results, depths)
    
    # Show plot
    plt.show()
    
    print("\nDone!") 