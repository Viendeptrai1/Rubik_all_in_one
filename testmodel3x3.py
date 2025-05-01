import torch
import torch.nn as nn
import numpy as np
import random
import time
import heapq
from RubikState.rubik_chen import RubikState, MOVES_3x3, MOVE_NAMES, SOLVED_STATE_3x3

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Paths
MODEL_PATH = "train_checkpoints/deepcube_model.pth"
CHECKPOINT_PATH = "train_checkpoints/deepcube_checkpoint.pth"

# Constants
W_HEUR = 1.0  # Weight for heuristic in A*
MAX_NODES_EXPAND = 100000  # Maximum nodes to expand

# Define the networks from test.py
class DeepCubeA(nn.Module):
    def __init__(self):
        super(DeepCubeA, self).__init__()
        
        # Simple network architecture
        self.fc1 = nn.Linear(40, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

class BranchedDeepCubeA(nn.Module):
    def __init__(self):
        super(BranchedDeepCubeA, self).__init__()
        
        # Permutation branch (cp, ep)
        self.perm_fc1 = nn.Linear(20, 256)
        self.perm_fc2 = nn.Linear(256, 128)
        
        # Orientation branch (co, eo)
        self.orient_fc1 = nn.Linear(20, 256)
        self.orient_fc2 = nn.Linear(256, 128)
        
        # Combined layers
        self.combined_fc1 = nn.Linear(256, 256)
        self.combined_fc2 = nn.Linear(256, 128)
        self.output = nn.Linear(128, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x_perm, x_orient):
        # Process permutation branch
        p = self.relu(self.perm_fc1(x_perm))
        p = self.relu(self.perm_fc2(p))
        
        # Process orientation branch
        o = self.relu(self.orient_fc1(x_orient))
        o = self.relu(self.orient_fc2(o))
        
        # Combine branches
        combined = torch.cat((p, o), dim=1)
        combined = self.relu(self.combined_fc1(combined))
        combined = self.relu(self.combined_fc2(combined))
        return self.output(combined)

# State encoder - converts RubikState to tensor input for neural network
class StateEncoder:
    def __init__(self, use_branched=True):
        self.use_branched = use_branched
    
    def encode(self, state):
        # Normalize values to [0,1] range
        
        # Corner permutation (cp): Map from 0-7 to [0,1]
        cp_normalized = [val / 7.0 for val in state.cp]
        
        # Corner orientation (co): Map from 0-2 to [0,1]
        co_normalized = [val / 2.0 for val in state.co]
        
        # Edge permutation (ep): Map from 0-11 to [0,1]
        ep_normalized = [val / 11.0 for val in state.ep]
        
        # Edge orientation (eo): Map from 0-1 to [0,1] (already in range)
        eo_normalized = list(state.eo)
        
        if self.use_branched:
            # For branched network, separate permutations and orientations
            perm_data = cp_normalized + ep_normalized
            orient_data = co_normalized + eo_normalized
            
            perm_tensor = torch.FloatTensor(perm_data).to(device)
            orient_tensor = torch.FloatTensor(orient_data).to(device)
            
            return perm_tensor, orient_tensor
        else:
            # For simple network, flatten everything into one vector
            flat_data = cp_normalized + co_normalized + ep_normalized + eo_normalized
            return torch.FloatTensor(flat_data).to(device)
    
    def encode_batch(self, states):
        if self.use_branched:
            perm_batch = []
            orient_batch = []
            
            for state in states:
                perm, orient = self.encode(state)
                perm_batch.append(perm)
                orient_batch.append(orient)
            
            return torch.stack(perm_batch), torch.stack(orient_batch)
        else:
            batch = [self.encode(state) for state in states]
            return torch.stack(batch)

# Node for A* search
class Node:
    def __init__(self, state, parent=None, move=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.move = move  # Move that led to this state from parent
        self.g = g  # Cost from start to current node
        self.h = h  # Heuristic estimate to goal
        self.f = g + W_HEUR * h  # f(n) = g(n) + w*h(n)
    
    def __lt__(self, other):
        return self.f < other.f
    
    def get_solution_path(self):
        path = []
        current = self
        while current.parent is not None:
            path.append(current.move)
            current = current.parent
        return path[::-1]  # Reverse to get path from start to current

# DeepCubeA Solver class
class DeepCubeASolver:
    def __init__(self, use_branched=True):
        self.use_branched = use_branched
        
        if use_branched:
            self.model = BranchedDeepCubeA().to(device)
        else:
            self.model = DeepCubeA().to(device)
        
        self.encoder = StateEncoder(use_branched=use_branched)
    
    def load_model(self, path=MODEL_PATH):
        print(f"Loading model from {path}...")
        try:
            checkpoint = torch.load(path, map_location=device)
            
            # Check if it's a checkpoint or just model state
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
                self.use_branched = checkpoint.get('use_branched', self.use_branched)
                print(f"Model loaded successfully (branched: {self.use_branched})")
                return True
            else:
                # Try loading as direct state_dict
                self.model.load_state_dict(checkpoint)
                print("Model loaded successfully (direct state_dict)")
                return True
                
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_value(self, state):
        """Predict the value (cost-to-go) for a given state"""
        self.model.eval()
        with torch.no_grad():
            encoded = self.encoder.encode(state)
            if self.use_branched:
                return self.model(encoded[0].unsqueeze(0), encoded[1].unsqueeze(0)).item()
            else:
                return self.model(encoded.unsqueeze(0)).item()
    
    def solve(self, initial_state, max_moves=50, timeout=120):
        """Solve the cube using A* search with time limit"""
        print("Starting A* search...")
        start_time = time.time()
        
        # A* search
        open_set = []
        closed_set = set()
        
        # Initial node
        initial_h = self.predict_value(initial_state)
        initial_node = Node(initial_state, g=0, h=initial_h)
        heapq.heappush(open_set, initial_node)
        
        nodes_expanded = 0
        
        while open_set and nodes_expanded < MAX_NODES_EXPAND:
            # Check timeout
            current_time = time.time()
            if current_time - start_time > timeout:
                print(f"Timeout after {timeout} seconds. Expanded {nodes_expanded} nodes.")
                return None
            
            # Get node with lowest f value
            current_node = heapq.heappop(open_set)
            
            # If we reached the solved state
            if current_node.state == SOLVED_STATE_3x3:
                solution_path = current_node.get_solution_path()
                elapsed_time = time.time() - start_time
                print(f"Solution found! {len(solution_path)} moves, expanded {nodes_expanded} nodes in {elapsed_time:.2f} seconds")
                return solution_path
            
            # Add to closed set
            state_hash = hash(current_node.state)
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            # Expand node
            nodes_expanded += 1
            if nodes_expanded % 1000 == 0:
                print(f"Expanded {nodes_expanded} nodes, queue size: {len(open_set)}")
            
            # Try all possible moves
            for move in MOVE_NAMES:
                next_state = current_node.state.apply_move(move)
                
                # Skip if already in closed set
                if hash(next_state) in closed_set:
                    continue
                
                # Skip if move undoes previous move (optimization)
                if current_node.parent and is_opposite_move(current_node.move, move):
                    continue
                
                # Calculate g, h, and f values
                g = current_node.g + 1
                if g > max_moves:  # Limit search depth
                    continue
                    
                h = self.predict_value(next_state)
                
                # Create new node
                new_node = Node(next_state, parent=current_node, move=move, g=g, h=h)
                
                # Add to open set
                heapq.heappush(open_set, new_node)
        
        elapsed_time = time.time() - start_time
        print(f"Failed to find solution within {MAX_NODES_EXPAND} node expansions in {elapsed_time:.2f} seconds")
        return None

# Utility functions
def is_opposite_move(move1, move2):
    """Check if two moves are opposites (e.g., R and R')"""
    if move1 is None or move2 is None:
        return False
        
    if len(move1) == 1 and len(move2) == 2 and move2[0] == move1:
        return True  # e.g., R and R'
    
    if len(move1) == 2 and len(move2) == 1 and move1[0] == move2:
        return True  # e.g., R' and R
    
    return False

def scramble_cube(num_moves):
    """Generate a scrambled cube state"""
    state = SOLVED_STATE_3x3
    moves_applied = []
    
    for _ in range(num_moves):
        # Avoid moves that undo the previous move
        valid_moves = list(MOVE_NAMES)
        if moves_applied:
            last_move = moves_applied[-1]
            for move in valid_moves[:]:
                if is_opposite_move(last_move, move):
                    valid_moves.remove(move)
        
        move = random.choice(valid_moves)
        state = state.apply_move(move)
        moves_applied.append(move)
    
    return state, moves_applied

def verify_solution(state, solution):
    """Verify if a solution correctly solves the scrambled state"""
    if solution is None:
        return False
    
    current_state = state
    for move in solution:
        current_state = current_state.apply_move(move)
    
    return current_state == SOLVED_STATE_3x3

def run_test(solver, scramble_depth, timeout=120):
    """Run a single test and return results"""
    # Generate scrambled state
    state, scramble_moves = scramble_cube(scramble_depth)
    
    print(f"\nScramble Depth: {scramble_depth}")
    print(f"Scramble Sequence: {' '.join(scramble_moves)}")
    
    # Solve the cube
    start_time = time.time()
    solution = solver.solve(state, max_moves=scramble_depth*2, timeout=timeout)
    solve_time = time.time() - start_time
    
    # Check solution
    if solution:
        is_valid = verify_solution(state, solution)
        print(f"✓ Solution found: {len(solution)} moves in {solve_time:.2f}s")
        print(f"Solution: {' '.join(solution)}")
        print(f"Valid solution: {'✓' if is_valid else '✗'}")
        return {
            'success': True,
            'moves': len(solution),
            'time': solve_time,
            'valid': is_valid
        }
    else:
        print(f"✗ No solution found after {solve_time:.2f}s")
        return {
            'success': False,
            'time': solve_time
        }

if __name__ == "__main__":
    print("DeepCubeA Model Tester for Rubik's Cube 3x3")
    print("===========================================")
    
    # Initialize solver with branched network
    # Based on checkpoint structure in test.py, the model should be branched
    solver = DeepCubeASolver(use_branched=True)
    
    # Load model
    if not solver.load_model():
        # Try again with checkpoint path
        if not solver.load_model(CHECKPOINT_PATH):
            print("Failed to load model. Exiting.")
            exit()
    
    # Testing options
    print("\nTest Options:")
    print("1. Run quick tests (depths 1-5)")
    print("2. Run medium tests (depths 5-10)")
    print("3. Run challenging tests (depths 10-15)")
    print("4. Custom test")
    
    choice = input("Enter your choice (1-4): ")
    
    if choice == "1":
        # Quick tests
        depths = [1, 2, 3, 4, 5]
        results = []
        
        for depth in depths:
            print(f"\n--- Testing Depth {depth} ---")
            result = run_test(solver, depth)
            results.append(result)
        
        # Print summary
        print("\n=== Test Summary ===")
        success_count = sum(1 for r in results if r['success'])
        success_rate = success_count / len(depths) * 100
        
        if success_count > 0:
            avg_moves = sum(r['moves'] for r in results if r['success']) / success_count
            avg_time = sum(r['time'] for r in results if r['success']) / success_count
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Average moves: {avg_moves:.1f}")
            print(f"Average time: {avg_time:.2f}s")
        else:
            print("No successful solutions")
    
    elif choice == "2":
        # Medium tests
        depths = [5, 6, 7, 8, 9, 10]
        results = []
        
        for depth in depths:
            print(f"\n--- Testing Depth {depth} ---")
            result = run_test(solver, depth)
            results.append(result)
        
        # Print summary
        print("\n=== Test Summary ===")
        success_count = sum(1 for r in results if r['success'])
        success_rate = success_count / len(depths) * 100
        
        if success_count > 0:
            avg_moves = sum(r['moves'] for r in results if r['success']) / success_count
            avg_time = sum(r['time'] for r in results if r['success']) / success_count
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Average moves: {avg_moves:.1f}")
            print(f"Average time: {avg_time:.2f}s")
        else:
            print("No successful solutions")
    
    elif choice == "3":
        # Challenging tests
        depths = [10, 11, 12, 13, 14, 15]
        timeout = 180  # Increase timeout for harder problems
        results = []
        
        for depth in depths:
            print(f"\n--- Testing Depth {depth} ---")
            result = run_test(solver, depth, timeout)
            results.append(result)
        
        # Print summary
        print("\n=== Test Summary ===")
        success_count = sum(1 for r in results if r['success'])
        success_rate = success_count / len(depths) * 100
        
        if success_count > 0:
            avg_moves = sum(r['moves'] for r in results if r['success']) / success_count
            avg_time = sum(r['time'] for r in results if r['success']) / success_count
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Average moves: {avg_moves:.1f}")
            print(f"Average time: {avg_time:.2f}s")
        else:
            print("No successful solutions")
    
    elif choice == "4":
        # Custom test
        depth = int(input("Enter scramble depth: "))
        timeout = int(input("Enter timeout in seconds (default 120): ") or "120")
        
        result = run_test(solver, depth, timeout)
        
        if result['success']:
            print(f"\nSolution found with {result['moves']} moves in {result['time']:.2f}s")
            print(f"Valid solution: {'✓' if result['valid'] else '✗'}")
        else:
            print(f"\nNo solution found after {result['time']:.2f}s")
    
    else:
        print("Invalid choice. Exiting.")
