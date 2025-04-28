import torch
import random
import time
from RubikState.rubik_chen import RubikState, MOVES_3x3, SOLVED_STATE_3x3, MOVE_NAMES
from test import (DeepCubeASolver, DEVICE, print_solution, ReplayBuffer,
                 CHECKPOINT_DIR)
import os

def load_model_for_testing(solver):
    """Load only the model weights for testing (ignore replay buffer)"""
    checkpoint_path = os.path.join(CHECKPOINT_DIR, "deepcube_checkpoint.pth")
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"No checkpoint found at {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=DEVICE)
    solver.model.load_state_dict(checkpoint['model_state_dict'])
    solver.model.eval()  # Set to evaluation mode
    return checkpoint['iteration'], checkpoint['scramble_depth']

def test_specific_scramble(solver, moves_sequence):
    """Test solver on a specific sequence of moves"""
    print(f"\nTesting scramble sequence: {moves_sequence}")
    state = SOLVED_STATE_3x3
    for move in moves_sequence:
        state = state.apply_move(move)
    
    start_time = time.time()
    solution = solver.solve(state)
    solve_time = time.time() - start_time
    
    if solution:
        print(f"Solution found in {solve_time:.2f} seconds!")
        print(f"Scramble length: {len(moves_sequence)}")
        print(f"Solution length: {len(solution)}")
        print(f"Solution: {solution}")
        
        # Verify solution
        test_state = state
        for move in solution:
            test_state = test_state.apply_move(move)
        if test_state == SOLVED_STATE_3x3:
            print("✅ Solution verified: Cube solved correctly")
        else:
            print("❌ Solution verification failed: Cube not solved")
    else:
        print("❌ Could not find solution")
    
    return solution is not None, solve_time, len(solution) if solution else None

def test_random_scrambles(solver, num_tests_per_depth, max_scramble_depth=20):
    """Test solver on random scrambles of increasing difficulty"""
    results = {}  # depth -> (success_rate, avg_time, avg_solution_length)
    
    for depth in range(1, max_scramble_depth + 1):
        print(f"\n=== Testing {num_tests_per_depth} scrambles of depth {depth} ===")
        successes = 0
        total_time = 0
        total_solution_length = 0
        
        for test in range(num_tests_per_depth):
            # Generate random scramble
            scramble = []
            state = SOLVED_STATE_3x3
            for _ in range(depth):
                move = random.choice(MOVE_NAMES)
                state = state.apply_move(move)
                scramble.append(move)
            
            print(f"\nTest {test + 1}/{num_tests_per_depth}:")
            success, solve_time, solution_length = test_specific_scramble(solver, scramble)
            
            if success:
                successes += 1
                total_time += solve_time
                total_solution_length += solution_length
        
        # Calculate statistics
        success_rate = successes / num_tests_per_depth
        avg_time = total_time / successes if successes > 0 else float('inf')
        avg_solution_length = total_solution_length / successes if successes > 0 else float('inf')
        
        results[depth] = (success_rate, avg_time, avg_solution_length)
        
        print(f"\nDepth {depth} Statistics:")
        print(f"Success Rate: {success_rate * 100:.1f}%")
        print(f"Average Solve Time: {avg_time:.2f} seconds")
        print(f"Average Solution Length: {avg_solution_length:.1f} moves")
    
    return results

def test_common_patterns(solver):
    """Test solver on common Rubik's cube patterns/algorithms"""
    patterns = {
        "Sexy Move": ["R", "U", "R'", "U'"] * 6,  # Should return to solved state
        "Sune": ["R", "U", "R'", "U", "R", "U", "U", "R'"],
        "Double Sune": ["R", "U", "R'", "U", "R", "U", "U", "R'"] * 2,
        "T Perm": ["R", "U", "R'", "U'", "R'", "F", "R", "R", "U'", "R'", "U'", "R", "U", "R'", "F'"],
        "Y Perm": ["F", "R", "U'", "R'", "U'", "R", "U", "R'", "F'", "R", "U", "R'", "U'", "R'", "F", "R", "F'"]
    }
    
    print("\n=== Testing Common Patterns ===")
    results = {}
    
    for name, sequence in patterns.items():
        print(f"\nTesting pattern: {name}")
        success, solve_time, solution_length = test_specific_scramble(solver, sequence)
        results[name] = (success, solve_time, solution_length)
    
    return results

def main():
    # Load the trained model
    solver = DeepCubeASolver(use_branched=True)
    try:
        iteration, scramble_depth = load_model_for_testing(solver)
        print(f"Model loaded successfully from iteration {iteration} (scramble depth {scramble_depth})")
        print(f"Using device: {DEVICE}")
    except FileNotFoundError as e:
        print("Error: Could not load model checkpoint!")
        print(e)
        return
    
    # 1. Test random scrambles
    print("\n=== RANDOM SCRAMBLES TEST ===")
    scramble_results = test_random_scrambles(solver, num_tests_per_depth=5, max_scramble_depth=15)
    
    # 2. Test common patterns
    print("\n=== COMMON PATTERNS TEST ===")
    pattern_results = test_common_patterns(solver)
    
    # 3. Print summary
    print("\n=== FINAL SUMMARY ===")
    print("\nRandom Scrambles Results:")
    for depth, (success_rate, avg_time, avg_length) in scramble_results.items():
        print(f"Depth {depth:2d}: {success_rate*100:5.1f}% success, {avg_time:6.2f}s avg time, {avg_length:5.1f} avg moves")
    
    print("\nCommon Patterns Results:")
    for pattern, (success, time, length) in pattern_results.items():
        status = "✅" if success else "❌"
        print(f"{pattern:12s}: {status} {time:6.2f}s, {length if length else 'N/A'} moves")

if __name__ == "__main__":
    main() 