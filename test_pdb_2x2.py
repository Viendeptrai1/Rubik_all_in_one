from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2
from RubikState.rubik_solver import a_star, bfs, ida_star, a_star_2x2  # Import explicitly from rubik_solver
import time
import random

def test_pdb_vs_regular(num_tests=3, max_depth=10):
    """
    Compare the PDB-enhanced A* with regular A* and other algorithms.
    
    Args:
        num_tests: Number of tests to run for each depth
        max_depth: Maximum scramble depth to test
    """
    print("=== COMPARING PDB-ENHANCED A* WITH OTHER ALGORITHMS ===\n")
    
    for depth in range(4, max_depth + 1, 2):  # Increment by 2 for readability
        print(f"\n--- TESTING SCRAMBLE DEPTH {depth} ---")
        
        total_times = {"PDB A*": 0, "Regular A*": 0, "BFS": 0, "IDA*": 0}
        total_nodes = {"PDB A*": 0, "Regular A*": 0, "BFS": 0, "IDA*": 0}
        total_lengths = {"PDB A*": 0, "Regular A*": 0, "BFS": 0, "IDA*": 0}
        success_count = {"PDB A*": 0, "Regular A*": 0, "BFS": 0, "IDA*": 0}
        
        for test_num in range(num_tests):
            # Generate a random scrambled cube
            scramble = []
            state = SOLVED_STATE_2x2.copy()
            
            for _ in range(depth):
                move = random.choice(list(MOVES_2x2.keys()))
                state = state.apply_move(move, MOVES_2x2)
                scramble.append(move)
            
            print(f"\nTest {test_num + 1}: Scramble: {' '.join(scramble)}")
            
            # Solve with all algorithms
            algorithms = {
                "PDB A*": a_star,      # Will use PDB if available
                "Regular A*": None,     # Will be handled specially
                "BFS": bfs,
                "IDA*": ida_star
            }
            
            for algo_name, algo_func in algorithms.items():
                # Skip Regular A* as it's handled by PDB A*
                if algo_name == "Regular A*":
                    continue
                
                # Create a fresh copy of the state
                test_state = Rubik2x2State(list(state.cp), list(state.co))
                
                # Solve with current algorithm
                start_time = time.time()
                if algo_name == "PDB A*":
                    # The integrated a_star function will automatically use PDB if available
                    path, nodes, _ = algo_func(test_state, time_limit=60)
                    elapsed = time.time() - start_time
                else:
                    path, nodes, elapsed = algo_func(test_state, time_limit=60)
                
                # Record results
                if path:
                    success_count[algo_name] += 1
                    total_times[algo_name] += elapsed
                    total_nodes[algo_name] += nodes
                    total_lengths[algo_name] += len(path)
                    
                    print(f"{algo_name}: Solved in {len(path)} moves, {nodes} nodes, {elapsed:.4f}s")
                    print(f"  Solution: {' '.join(path)}")
                    
                    # Verify solution
                    verify_state = test_state.copy()
                    for move in path:
                        verify_state = verify_state.apply_move(move, MOVES_2x2)
                    
                    if verify_state == SOLVED_STATE_2x2:
                        print("  ✓ Solution is correct")
                    else:
                        print("  ✗ Solution is INCORRECT!")
                else:
                    print(f"{algo_name}: Failed to solve in time limit. Explored {nodes} nodes in {elapsed:.4f}s")
            
            # Now run the regular A* by importing directly from the module
            # to bypass the PDB enhancement
            test_state = Rubik2x2State(list(state.cp), list(state.co))
            start_time = time.time()
            path, nodes, _ = a_star_2x2(test_state, time_limit=60)
            elapsed = time.time() - start_time
            
            if path:
                success_count["Regular A*"] += 1
                total_times["Regular A*"] += elapsed
                total_nodes["Regular A*"] += nodes
                total_lengths["Regular A*"] += len(path)
                
                print(f"Regular A*: Solved in {len(path)} moves, {nodes} nodes, {elapsed:.4f}s")
                print(f"  Solution: {' '.join(path)}")
                
                # Verify solution
                verify_state = test_state.copy()
                for move in path:
                    verify_state = verify_state.apply_move(move, MOVES_2x2)
                
                if verify_state == SOLVED_STATE_2x2:
                    print("  ✓ Solution is correct")
                else:
                    print("  ✗ Solution is INCORRECT!")
            else:
                print(f"Regular A*: Failed to solve in time limit. Explored {nodes} nodes in {elapsed:.4f}s")
        
        # Print summary for this depth
        print(f"\n=== SUMMARY FOR DEPTH {depth} ===")
        
        for algo_name in algorithms.keys():
            if success_count[algo_name] > 0:
                avg_time = total_times[algo_name] / success_count[algo_name]
                avg_nodes = total_nodes[algo_name] / success_count[algo_name]
                avg_length = total_lengths[algo_name] / success_count[algo_name]
                
                print(f"{algo_name}: {success_count[algo_name]}/{num_tests} solved")
                print(f"  Avg time: {avg_time:.4f}s")
                print(f"  Avg nodes: {avg_nodes:.1f}")
                print(f"  Avg solution length: {avg_length:.1f}")
            else:
                print(f"{algo_name}: 0/{num_tests} solved")
        
        # Calculate improvement ratios if both succeeded
        if success_count["PDB A*"] > 0 and success_count["Regular A*"] > 0:
            time_ratio = total_times["Regular A*"] / total_times["PDB A*"]
            node_ratio = total_nodes["Regular A*"] / total_nodes["PDB A*"]
            
            print(f"\nPDB A* vs Regular A*:")
            print(f"  {time_ratio:.2f}x faster")
            print(f"  {node_ratio:.2f}x fewer nodes explored")

def main():
    print("=== TESTING 2x2 RUBIK'S CUBE SOLVER WITH PATTERN DATABASE ===\n")
    
    # Run comparison tests
    test_pdb_vs_regular(num_tests=3, max_depth=10)

if __name__ == "__main__":
    main() 