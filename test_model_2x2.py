import torch
import torch.nn as nn
import numpy as np
import random
import time
import heapq
from RubikState.rubik_2x2 import Rubik2x2State, MOVES_2x2, MOVE_NAMES, SOLVED_STATE_2x2, calculate_parity, heuristic_2x2

# Device configuration
device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Paths
MODEL_PATH = "train_checkpoints_2x2/deepcube_2x2_model.pth"
CHECKPOINT_PATH = "train_checkpoints_2x2/deepcube_2x2_checkpoint.pth"

# Constants
W_HEUR = 1  # Weight for heuristic in A*
MAX_NODES_EXPAND = 100000  # Maximum nodes to expand

# Define the DeepCube2x2 network
class DeepCube2x2(nn.Module):
    def __init__(self):
        super(DeepCube2x2, self).__init__()
        
        # Input size: 8 corners with position (8) and orientation (8)
        # Total: 16 features
        self.fc1 = nn.Linear(16, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

# State encoder - converts Rubik2x2State to tensor input for neural network
class StateEncoder:
    def __init__(self):
        pass
    
    def encode(self, state):
        # Normalize values to [0,1] range
        # Corner permutation (cp): Map from 0-7 to [0,1]
        cp_normalized = [val / 7.0 for val in state.cp]
        
        # Corner orientation (co): Map from 0-2 to [0,1]
        co_normalized = [val / 2.0 for val in state.co]
        
        # Combine into a single vector
        flat_data = cp_normalized + co_normalized
        return torch.FloatTensor(flat_data).to(device)
    
    def encode_batch(self, states):
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

# DeepCube2x2 Solver class
class DeepCube2x2Solver:
    def __init__(self):
        self.model = DeepCube2x2().to(device)
        self.encoder = StateEncoder()
    
    def load_model(self, path=MODEL_PATH):
        print(f"Loading model from {path}...")
        try:
            checkpoint = torch.load(path, map_location=device)
            
            # Check if it's a checkpoint or just model state
            if 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
                print("Model loaded successfully (from checkpoint)")
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
            return self.model(encoded.unsqueeze(0)).item()
    
    def solve(self, initial_state, max_moves=20, timeout=120):
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
            if current_node.state == SOLVED_STATE_2x2:
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
                
                # Create and add the new node
                new_node = Node(next_state, parent=current_node, move=move, g=g, h=h)
                heapq.heappush(open_set, new_node)
        
        print(f"Search exhausted after expanding {nodes_expanded} nodes.")
        return None

def is_opposite_move(move1, move2):
    """Check if move2 is the opposite of move1 (undoes move1)"""
    # For prime moves
    if move1 == move2 + "'" or move1 + "'" == move2:
        return True
    return False

def scramble_cube(num_moves):
    """Generate a scrambled state by applying random moves"""
    state = SOLVED_STATE_2x2
    moves_applied = []
    
    for _ in range(num_moves):
        # Avoid moves that undo the previous move
        valid_moves = list(MOVE_NAMES)
        if moves_applied:
            last_move = moves_applied[-1]
            # Remove opposite move
            for move in valid_moves[:]:
                if is_opposite_move(last_move, move):
                    valid_moves.remove(move)
                    break
        
        move = random.choice(valid_moves)
        state = state.apply_move(move)
        moves_applied.append(move)
    
    return state, moves_applied

def verify_solution(state, solution):
    """Verify that applying the solution to the state results in a solved cube"""
    result = state
    for move in solution:
        result = result.apply_move(move)
    
    return result == SOLVED_STATE_2x2

def run_test(solver, scramble_depth, timeout=120):
    """Run a test with a scrambled cube at the given depth"""
    # Generate scrambled state
    scrambled_state, moves = scramble_cube(scramble_depth)
    print(f"Testing with {scramble_depth} random moves:")
    print(f"Scramble sequence: {' '.join(moves)}")
    
    # Solve
    solution = solver.solve(scrambled_state, max_moves=scramble_depth*2, timeout=timeout)
    
    # Verify solution
    if solution is not None:
        is_valid = verify_solution(scrambled_state, solution)
        print(f"Solution is valid: {is_valid}")
        print(f"Solution length: {len(solution)}")
        print(f"Solution: {' '.join(solution)}")
        return True
    else:
        print("No solution found within the time limit.")
        return False

def main():
    # Create and load the solver
    solver = DeepCube2x2Solver()
    if not solver.load_model():
        print("Failed to load model. Exiting.")
        return
    
    print("DeepCube 2x2 Solver loaded successfully!")
    
    # Run tests for different scramble depths
    success_count = 0
    test_depths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    
    for depth in test_depths:
        print(f"\n{'='*50}")
        print(f"TESTING DEPTH {depth}")
        print(f"{'='*50}")
        if run_test(solver, depth):
            success_count += 1
        print()
    
    print(f"Success rate: {success_count}/{len(test_depths)} ({success_count/len(test_depths)*100:.1f}%)")

if __name__ == "__main__":
    main() 