import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
import heapq
from collections import deque
import time
import os
import pickle
from RubikState.rubik_2x2 import Rubik2x2State, MOVES_2x2, SOLVED_STATE_2x2, MOVE_NAMES, calculate_parity, heuristic_2x2

# Constants
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 2048
REPLAY_BUFFER_SIZE = 1000000
NUM_SCRAMBLES = 30
NUM_AVI_ITERATIONS = 100000
LEARNING_RATE = 0.0001
EPSILON = 0.05
GAMMA = 0.99
W_HEUR = 1.0
MAX_NODES_EXPAND = 100000
TRAINING_SAMPLES_PER_ITER = 10000
VALIDATION_INTERVAL = 500
CHECKPOINT_INTERVAL = 250

# Training parameters
CHECKPOINT_DIR = "train_checkpoints_2x2"
CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, "deepcube_2x2_checkpoint.pth")
REPLAY_BUFFER_PATH = os.path.join(CHECKPOINT_DIR, "replay_buffer_2x2.pkl")
MODEL_PATH = os.path.join(CHECKPOINT_DIR, "deepcube_2x2_model.pth")

# Ensure checkpoint directory exists
def ensure_checkpoint_dir():
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)

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
        return torch.FloatTensor(flat_data).to(DEVICE)
    
    def encode_batch(self, states):
        batch = [self.encode(state) for state in states]
        return torch.stack(batch)

# Replay buffer for storing experience
class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = {}  # Dictionary of deques for each depth
        self.total_samples = 0
    
    def add(self, state, value, depth=None):
        # If depth not provided, use value as depth (since cost = depth)
        if depth is None:
            depth = int(value)
        
        # Initialize buffer for this depth if not exists
        if depth not in self.buffer:
            self.buffer[depth] = deque(maxlen=self.capacity // 10)  # Limit per depth
        
        self.buffer[depth].append((state, value))
        self.total_samples = sum(len(samples) for samples in self.buffer.values())
    
    def sample(self, batch_size):
        # Ensure we have enough samples
        if self.total_samples < batch_size:
            return []
        
        # Strategy: 
        # - 70% from current and difficult depths
        # - 30% from easier depths for stability
        samples = []
        depths = sorted(self.buffer.keys())
        
        if not depths:
            return []
        
        # Current depth is the highest
        current_depth = max(depths)
        
        # Calculate how many samples to take from each category
        current_samples = int(batch_size * 0.7)
        easier_samples = batch_size - current_samples
        
        # Sample from current depth (and one below if available)
        current_depths = [d for d in depths if d >= current_depth - 1]
        current_pool = []
        for d in current_depths:
            current_pool.extend(self.buffer[d])
        
        if current_pool:
            # Sample with replacement if we don't have enough
            if len(current_pool) < current_samples:
                samples.extend(random.choices(current_pool, k=current_samples))
            else:
                samples.extend(random.sample(current_pool, current_samples))
        
        # Sample from easier depths
        easier_depths = [d for d in depths if d < current_depth - 1]
        easier_pool = []
        for d in easier_depths:
            easier_pool.extend(self.buffer[d])
            
        if easier_pool and easier_samples > 0:
            # Sample with replacement if we don't have enough
            if len(easier_pool) < easier_samples:
                samples.extend(random.choices(easier_pool, k=easier_samples))
            else:
                samples.extend(random.sample(easier_pool, easier_samples))
        
        # If we still don't have enough samples, pad with what we have
        if len(samples) < batch_size:
            all_samples = []
            for depth_samples in self.buffer.values():
                all_samples.extend(depth_samples)
            
            additional_needed = batch_size - len(samples)
            if all_samples:
                samples.extend(random.choices(all_samples, k=additional_needed))
        
        return samples
    
    def __len__(self):
        return self.total_samples

# Generate a scrambled state by applying random moves
def generate_scrambled_state(num_moves):
    state = SOLVED_STATE_2x2
    moves_applied = []
    
    if num_moves == 0:
        return state, moves_applied
    
    # Ensure the scrambled state is different from the solved state
    attempt = 0
    max_attempts = 5
    
    while attempt < max_attempts:
        test_state = SOLVED_STATE_2x2
        test_moves = []
        
        for _ in range(num_moves):
            # Avoid moves that undo the previous move
            valid_moves = list(MOVE_NAMES)
            if test_moves:
                last_move = test_moves[-1]
                inverse_move = None
                
                # Determine inverse move
                if last_move.endswith("'"):
                    inverse_move = last_move[:-1]  # Remove the '
                else:
                    inverse_move = last_move + "'"
                
                if inverse_move in valid_moves:
                    valid_moves.remove(inverse_move)
                
                # Avoid repeating the same move
                if last_move in valid_moves and len(valid_moves) > 1:
                    valid_moves.remove(last_move)
            
            move = random.choice(valid_moves)
            test_state = test_state.apply_move(move)
            test_moves.append(move)
        
        # Check if the new state is different from the solved state
        if test_state != SOLVED_STATE_2x2 or num_moves <= 1:
            return test_state, test_moves
        
        attempt += 1
    
    # If after multiple attempts we still haven't generated a different state,
    # return the last generated state
    return test_state, test_moves

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

# DeepCube2x2 Solver
class DeepCube2x2Solver:
    def __init__(self):
        self.model = DeepCube2x2().to(DEVICE)
        self.optimizer = optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
        self.criterion = nn.MSELoss()
        self.encoder = StateEncoder()
        self.replay_buffer = ReplayBuffer(REPLAY_BUFFER_SIZE)
        
        # Initialize replay buffer with solved state
        self.replay_buffer.add(SOLVED_STATE_2x2, 0.0, depth=0)
    
    def predict_value(self, state):
        """Predict the value (cost-to-go) for a given state"""
        self.model.eval()
        with torch.no_grad():
            encoded = self.encoder.encode(state)
            return self.model(encoded.unsqueeze(0)).item()
    
    def get_best_move(self, state):
        """Get best move using epsilon-greedy policy"""
        # With probability epsilon, choose a random move
        if random.random() < EPSILON:
            return random.choice(MOVE_NAMES)
        
        # Otherwise, choose the move with minimum predicted cost
        best_move = None
        min_value = float('inf')
        
        for move in MOVE_NAMES:
            next_state = state.apply_move(move)
            value = self.predict_value(next_state)
            
            if value < min_value:
                min_value = value
                best_move = move
        
        return best_move
    
    def update_model(self, batch_size):
        """Update model using a batch of experiences"""
        if len(self.replay_buffer) < batch_size:
            return None
        
        self.model.train()
        batch = self.replay_buffer.sample(batch_size)
        
        if not batch:  # Empty batch
            return None
            
        states, values = zip(*batch)
        
        # Forward pass
        inputs = self.encoder.encode_batch(states)
        predictions = self.model(inputs).squeeze()
        
        # Backward pass
        target_values = torch.FloatTensor(values).to(DEVICE)
        loss = self.criterion(predictions, target_values)
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
    
    def train_avi(self, num_iterations, start_iteration=0, scramble_depth=1):
        """Train using Approximate Value Iteration (AVI) with curriculum learning"""
        print(f"Training on {DEVICE} | Batch: {BATCH_SIZE} | LR: {LEARNING_RATE}")
        
        solved_state = SOLVED_STATE_2x2
        self.replay_buffer.add(solved_state, 0.0, depth=0)
        
        # Keep track of progress
        losses = []
        val_success_rates = []
        current_depth = scramble_depth
        max_depth = 11  # Maximum scramble depth for 2x2 cube
        min_success_rate = 0.9  # Required success rate to increase depth
        
        # Track time
        start_time = time.time()
        
        # Training loop
        for iteration in range(start_iteration, start_iteration + num_iterations):
            # Generate training examples
            if iteration % 10 == 0:
                # Generate new experiences at different depths
                for _ in range(BATCH_SIZE // 4):
                    # 80% of samples from current depth, 20% from easier depths
                    if random.random() < 0.8:
                        depth = current_depth
                    else:
                        depth = random.randint(1, current_depth - 1) if current_depth > 1 else 1
                        
                    scrambled_state, _ = generate_scrambled_state(depth)
                    
                    # Add to replay buffer with cost = depth
                    self.replay_buffer.add(scrambled_state, float(depth), depth=depth)
            
            # Update model
            loss = self.update_model(BATCH_SIZE)
            if loss is not None:  # Only append if we had enough samples
                losses.append(loss)
            
            # Validation and curriculum learning
            if iteration % VALIDATION_INTERVAL == 0:
                # Evaluate at current depth
                success_rate = self.validate(current_depth, num_tests=30)
                val_success_rates.append(success_rate)
                
                elapsed_time = time.time() - start_time
                loss_str = f"{loss:.4f}" if loss is not None else "N/A"
                print(f"Iteration {iteration}, Depth: {current_depth}, Loss: {loss_str}, Success rate: {success_rate*100:.1f}%, Time: {elapsed_time/60:.1f}m")
                
                # Early stopping: if we've reached max depth with high success rate, stop training
                if current_depth >= max_depth and success_rate >= min_success_rate:
                    print(f"Early stopping: Reached depth {current_depth} with success rate {success_rate*100:.1f}%")
                    break
                
                # Curriculum learning: increase depth if success rate is high enough
                if success_rate >= min_success_rate and current_depth < max_depth:
                    current_depth += 1
                    print(f"Increasing depth to {current_depth}")
                
                # Save checkpoint
                if iteration % CHECKPOINT_INTERVAL == 0:
                    self.save_checkpoint(iteration, current_depth)
        
        # Save final model
        self.save_model()
        
        total_time = (time.time() - start_time) / 60
        print(f"Training completed in {total_time:.1f} minutes. Final depth: {current_depth}")
        
        return losses, val_success_rates
    
    def validate(self, scramble_depth, num_tests=50):
        """Validate the model by solving scrambled cubes"""
        self.model.eval()
        success_count = 0
        
        for _ in range(num_tests):
            test_state, _ = generate_scrambled_state(scramble_depth)
            solution = self.solve(test_state, max_moves=20)
            
            if solution:
                # Verify solution
                test_solved = test_state
                for move in solution:
                    test_solved = test_solved.apply_move(move)
                
                if test_solved == SOLVED_STATE_2x2:
                    success_count += 1
        
        return success_count / num_tests
    
    def solve(self, initial_state, max_moves=20):
        """Solve the cube from an initial state using A* search"""
        # A* search with heuristic from the trained model
        open_set = []
        closed_set = set()
        
        # Initial node
        initial_h = self.predict_value(initial_state)
        initial_node = Node(initial_state, g=0, h=initial_h)
        heapq.heappush(open_set, initial_node)
        
        nodes_expanded = 0
        
        while open_set and nodes_expanded < MAX_NODES_EXPAND:
            # Get node with lowest f value
            current_node = heapq.heappop(open_set)
            
            # If we reached the solved state
            if current_node.state == SOLVED_STATE_2x2:
                return current_node.get_solution_path()
            
            # Add to closed set
            state_hash = hash(current_node.state)
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            # Expand node
            nodes_expanded += 1
            
            # Try all possible moves
            for move in MOVE_NAMES:
                next_state = current_node.state.apply_move(move)
                
                # Skip if already in closed set
                if hash(next_state) in closed_set:
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
        
        return None  # No solution found
    
    def save_checkpoint(self, iteration, scramble_depth, path=CHECKPOINT_PATH, buffer_path=REPLAY_BUFFER_PATH):
        """Save checkpoint (model, optimizer, replay buffer)"""
        ensure_checkpoint_dir()
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'iteration': iteration,
            'scramble_depth': scramble_depth,
        }, path)
        
        # Save replay buffer separately
        with open(buffer_path, "wb") as f:
            pickle.dump(self.replay_buffer, f)
    
    def load_checkpoint(self, path=CHECKPOINT_PATH, buffer_path=REPLAY_BUFFER_PATH):
        """Load checkpoint"""
        if not os.path.exists(path):
            return 0, 1  # iteration, scramble_depth
        
        print("Loading checkpoint...")
        checkpoint = torch.load(path, map_location=DEVICE)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        # Load replay buffer
        try:
            if os.path.exists(buffer_path):
                with open(buffer_path, "rb") as f:
                    old_buffer = pickle.load(f)
                
                # Convert old buffer format if needed
                if not isinstance(old_buffer, ReplayBuffer) or not hasattr(old_buffer, 'buffer') or not isinstance(old_buffer.buffer, dict):
                    print("Converting old replay buffer format...")
                    new_buffer = ReplayBuffer(REPLAY_BUFFER_SIZE)
                    
                    # Handle old format
                    if hasattr(old_buffer, 'buffer'):
                        if isinstance(old_buffer.buffer, dict):
                            # Already in correct format
                            self.replay_buffer = old_buffer
                        else:
                            # Old format with deque
                            for state, value in old_buffer.buffer:
                                depth = int(value) if value > 0 else 0
                                new_buffer.add(state, value, depth)
                            self.replay_buffer = new_buffer
                    else:
                        # Unknown format, start fresh
                        self.replay_buffer = ReplayBuffer(REPLAY_BUFFER_SIZE)
                        self.replay_buffer.add(SOLVED_STATE_2x2, 0.0, depth=0)
                else:
                    # Already in correct format
                    self.replay_buffer = old_buffer
                
                print(f"Loaded {len(self.replay_buffer)} experiences across {len(self.replay_buffer.buffer)} depths")
            else:
                print("No replay buffer found, starting fresh")
                self.replay_buffer = ReplayBuffer(REPLAY_BUFFER_SIZE)
                self.replay_buffer.add(SOLVED_STATE_2x2, 0.0, depth=0)
                
        except Exception as e:
            print(f"Warning: Could not load replay buffer ({str(e)})")
            print("Starting with fresh replay buffer")
            self.replay_buffer = ReplayBuffer(REPLAY_BUFFER_SIZE)
            self.replay_buffer.add(SOLVED_STATE_2x2, 0.0, depth=0)
        
        return checkpoint['iteration'], checkpoint['scramble_depth']
    
    def save_model(self, path=MODEL_PATH):
        """Save the trained model to disk"""
        ensure_checkpoint_dir()
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path=MODEL_PATH):
        """Load a trained model from disk"""
        if not os.path.exists(path):
            print(f"Model file not found: {path}")
            return False
        
        self.model.load_state_dict(torch.load(path, map_location=DEVICE))
        return True

def print_solution(initial_state, solution_path):
    """Print the solution step by step"""
    print("\nSOLUTION PATH:")
    print("==============")
    
    state = initial_state
    print(f"Initial state:")
    print(f"CP: {state.cp}")
    print(f"CO: {state.co}")
    
    for i, move in enumerate(solution_path):
        state = state.apply_move(move)
        print(f"\nStep {i+1}: Apply move {move}")
        print(f"CP: {state.cp}")
        print(f"CO: {state.co}")
    
    print(f"\nFinal state solved: {state == SOLVED_STATE_2x2}")

def test_model(solver, max_depth=11):
    """Test the trained model on various scramble depths"""
    print("\nTesting model:")
    print("==============")
    
    for depth in range(1, max_depth):
        print(f"\nScramble depth {depth}:")
        success_count = 0
        total_moves = 0
        num_tests = 10
        
        for test in range(num_tests):
            scrambled_state, scramble_moves = generate_scrambled_state(depth)
            print(f"Test {test+1}: {scramble_moves}")
            
            solution = solver.solve(scrambled_state)
            if solution:
                # Verify solution
                test_solved = scrambled_state
                for move in solution:
                    test_solved = test_solved.apply_move(move)
                
                if test_solved == SOLVED_STATE_2x2:
                    success_count += 1
                    total_moves += len(solution)
                    print(f"  Solved in {len(solution)} moves: {solution}")
                else:
                    print("  Solution verification failed!")
            else:
                print("  No solution found!")
        
        if success_count > 0:
            avg_moves = total_moves / success_count
            print(f"Depth {depth} success rate: {success_count/num_tests*100:.1f}%, Avg moves: {avg_moves:.1f}")
        else:
            print(f"Depth {depth} success rate: 0%")

def main():
    """Main function to train and test the model"""
    print(f"DeepCube 2x2 Solver running on {DEVICE}")
    
    solver = DeepCube2x2Solver()
    
    # Check if we should load from checkpoint
    iteration, scramble_depth = solver.load_checkpoint()
    
    # Training mode
    train = True
    if train:
        print(f"Starting training from iteration {iteration}, scramble depth {scramble_depth}")
        solver.train_avi(NUM_AVI_ITERATIONS, iteration, scramble_depth)
    else:
        # Load pre-trained model if available
        if not solver.load_model():
            print("No pre-trained model found. Please train the model first.")
            return
    
    # Test the model
    test_model(solver)
    
    # Interactive mode for solving
    while True:
        print("\nEnter a sequence of moves to scramble the cube (e.g. R U' F), or 'q' to quit:")
        user_input = input().strip()
        
        if user_input.lower() == 'q':
            break
        
        # Parse moves
        moves = user_input.split()
        valid_moves = True
        
        for move in moves:
            if move not in MOVE_NAMES:
                print(f"Invalid move: {move}")
                valid_moves = False
                break
        
        if not valid_moves:
            continue
        
        # Apply scramble
        state = SOLVED_STATE_2x2
        for move in moves:
            state = state.apply_move(move)
        
        # Solve
        print("Solving...")
        solution = solver.solve(state)
        
        if solution:
            print_solution(state, solution)
            print(f"Solution found: {solution}")
        else:
            print("No solution found!")

if __name__ == "__main__":
    main()