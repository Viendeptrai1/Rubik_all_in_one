import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import random
import heapq
from collections import deque
import time
from RubikState.rubik_chen import RubikState, MOVES_3x3, SOLVED_STATE_3x3, MOVE_NAMES
import os
import pickle

# Constants - Optimized for CPU
DEVICE = torch.device("cpu")  # Force CPU usage
BATCH_SIZE = 2048  # Increased batch size for better learning
REPLAY_BUFFER_SIZE = 5000000  # 5M buffer size
NUM_SCRAMBLES = 50
NUM_AVI_ITERATIONS = 50000
LEARNING_RATE = 0.0005  # Decreased from 0.001 to 0.0005 for more stable learning
EPSILON = 0.05
GAMMA = 0.99
W_HEUR = 1.0  # Changed from 3 to 1.0 for optimal A* heuristic utilization
MAX_NODES_EXPAND = 100000
TRAINING_SAMPLES_PER_ITER = 20000
VALIDATION_INTERVAL = 1000
CHECKPOINT_INTERVAL = 500

# LR Scheduler parameters
USE_LR_SCHEDULER = True
LR_SCHEDULER_PATIENCE = 5
LR_SCHEDULER_FACTOR = 0.5
MIN_LR = 0.00001

# Advanced training parameters
MIN_SCRAMBLE_DEPTH = 1
MAX_SCRAMBLE_DEPTH = 10     # Changed from 30 to 10 (focus on training up to depth 10)
DEPTH_INCREASE_INTERVAL = 2000
CURRICULUM_LEARNING = True
USE_DATA_AUGMENTATION = False  # Disabled for speed
VALIDATION_SCRAMBLES = [3, 5, 8, 10]  # Modified validation depths

# Performance optimization for M2
NUM_WORKERS = 7  # Enabled multiprocessing on CPU
PIN_MEMORY = False  # Disable for CPU usage

# Adaptive training parameters
BASE_ITERS_PER_DEPTH = 1000  # Increased from 700 to 1000 for more thorough training at each depth
ITERS_INCREMENT = 300       # Increased to 300 for more iterations as depth increases
MIN_SUCCESS_RATE = 0.95     # Slightly reduced from 0.98 to 0.95 to avoid excessive training
VALIDATION_SIZE = 50        # Increased from 30 to 50 for more reliable validation

# PER parameters
USE_PRIORITIZED_REPLAY = True
PER_ALPHA = 0.6  # Priority exponent
PER_BETA = 0.4   # Initial importance sampling weight
PER_BETA_INCREMENT = 0.001  # Beta increment per sampling

# Training parameters
CHECKPOINT_DIR = "train_checkpoints"
CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, "deepcube_checkpoint.pth")
REPLAY_BUFFER_PATH = os.path.join(CHECKPOINT_DIR, "replay_buffer.pkl")
MODEL_PATH = os.path.join(CHECKPOINT_DIR, "deepcube_model.pth")

# Experience replay parameters
BEST_STATES_PER_DEPTH = 2000  # Increased from 1000 to 2000
PREV_DEPTH_RATIO = 0.3  # 30% samples from previous depths
CURRICULUM_RATIO = 0.7  # 70% of previous samples from recent depths

# Ensure checkpoint directory exists
def ensure_checkpoint_dir():
    if not os.path.exists(CHECKPOINT_DIR):
        os.makedirs(CHECKPOINT_DIR)

# Save checkpoint (model, optimizer, replay buffer, iteration, scramble_depth)
def save_checkpoint(solver, iteration, scramble_depth, path=CHECKPOINT_PATH, buffer_path=REPLAY_BUFFER_PATH):
    ensure_checkpoint_dir()
    torch.save({
        'model_state_dict': solver.model.state_dict(),
        'optimizer_state_dict': solver.optimizer.state_dict(),
        'use_branched': solver.use_branched,
        'iteration': iteration,
        'scramble_depth': scramble_depth,
    }, path)
    # Save replay buffer separately (pickle)
    with open(buffer_path, "wb") as f:
        pickle.dump(solver.replay_buffer, f)

# Keep old ReplayBuffer for backward compatibility
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, value):
        self.buffer.append((state, value))
    
    def sample(self, batch_size):
        if batch_size > len(self.buffer):
            batch_size = len(self.buffer)
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)

# Load checkpoint (returns iteration, scramble_depth)
def load_checkpoint(solver, path=CHECKPOINT_PATH, buffer_path=REPLAY_BUFFER_PATH):
    if not os.path.exists(path) or not os.path.exists(buffer_path):
        return 0, 1  # iteration, scramble_depth
    
    print("Loading checkpoint...")
    checkpoint = torch.load(path, map_location=DEVICE)
    solver.model.load_state_dict(checkpoint['model_state_dict'])
    solver.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    solver.use_branched = checkpoint['use_branched']
    
    # Try to load replay buffer
    try:
        print("Loading replay buffer...")
        with open(buffer_path, "rb") as f:
            old_buffer = pickle.load(f)
            
        # Convert old ReplayBuffer to SmartReplayBuffer
        if isinstance(old_buffer, ReplayBuffer):
            print("Converting old replay buffer format to new format...")
            new_buffer = SmartReplayBuffer(REPLAY_BUFFER_SIZE)
            
            # Add all states from old buffer to depth 1 initially
            for state, value in old_buffer.buffer:
                new_buffer.add(state, value, 1, 0.0)
            
            solver.replay_buffer = new_buffer
        else:
            solver.replay_buffer = old_buffer
            
        print(f"Loaded {len(solver.replay_buffer)} experiences")
        
    except Exception as e:
        print(f"Warning: Could not load replay buffer ({str(e)})")
        print("Starting with fresh replay buffer")
        solver.replay_buffer = SmartReplayBuffer(REPLAY_BUFFER_SIZE)
        solver.replay_buffer.add(SOLVED_STATE_3x3, 0.0, 1, 0.0)
    
    return checkpoint['iteration'], checkpoint['scramble_depth']

# Define the DeepCubeA network
class DeepCubeA(nn.Module):
    def __init__(self):
        super(DeepCubeA, self).__init__()
        
        # Define network architecture
        # Simple version: flatten all inputs into a single vector
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

# Branched version of the network
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
    def __init__(self, use_branched=False):
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
            
            perm_tensor = torch.FloatTensor(perm_data).to(DEVICE)
            orient_tensor = torch.FloatTensor(orient_data).to(DEVICE)
            
            return perm_tensor, orient_tensor
        else:
            # For simple network, flatten everything into one vector
            flat_data = cp_normalized + co_normalized + ep_normalized + eo_normalized
            return torch.FloatTensor(flat_data).to(DEVICE)
    
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

# Replay buffer for storing experience with Prioritized Experience Replay
class SmartReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = {}  # Dictionary of deques for each depth
        self.depth_losses = {}  # Track average loss for each depth
        self.min_losses = {}  # Track minimum loss for each depth
        
        # PER attributes
        self.use_per = USE_PRIORITIZED_REPLAY
        self.priorities = {}  # Dictionary of priorities for each depth
        self.alpha = PER_ALPHA
        self.beta = PER_BETA
        self.beta_increment = PER_BETA_INCREMENT
        self.max_priority = 1.0
    
    def add(self, state, value, depth, loss=None):
        if depth not in self.buffer:
            self.buffer[depth] = deque(maxlen=self.capacity)
            self.depth_losses[depth] = []
            if self.use_per:
                self.priorities[depth] = []
        
        self.buffer[depth].append((state, value))
        
        if self.use_per:
            # Add max priority for new experience
            self.priorities[depth].append(self.max_priority)
            # Keep priorities length same as buffer length
            if len(self.priorities[depth]) > len(self.buffer[depth]):
                self.priorities[depth].pop(0)
        
        if loss is not None:
            self.depth_losses[depth].append(loss)
            # Keep only recent losses to track improvement
            if len(self.depth_losses[depth]) > 100:
                self.depth_losses[depth].pop(0)
            
            # Update minimum loss for this depth
            current_avg_loss = np.mean(self.depth_losses[depth])
            self.min_losses[depth] = min(self.min_losses.get(depth, float('inf')), current_avg_loss)
    
    def get_depth_mastery(self, depth):
        """Calculate how well we've mastered this depth (0 to 1)"""
        if depth not in self.depth_losses or not self.depth_losses[depth]:
            return 0.0
        
        current_avg_loss = np.mean(self.depth_losses[depth])
        min_loss = self.min_losses.get(depth, current_avg_loss)
        
        # Consider a depth mastered if average loss is below 0.01
        MASTERY_THRESHOLD = 0.01
        if current_avg_loss < MASTERY_THRESHOLD:
            return 1.0
        
        # Otherwise, return a value between 0 and 1
        return max(0, 1 - (current_avg_loss / max(0.1, min_loss)))
    
    def sample_smart(self, batch_size, current_depth):
        """Smart sampling based on depth mastery and priorities if PER is enabled"""
        batch = []
        weights = None  # For importance sampling weights
        indices_map = None  # To track which indices were sampled
        
        # Calculate mastery levels for all previous depths
        mastery_levels = {d: self.get_depth_mastery(d) for d in range(1, current_depth + 1)}
        
        if current_depth == 1:
            if self.use_per and self.priorities.get(1, []):
                # Sample using priorities
                probs = np.array(self.priorities[1]) ** self.alpha
                probs /= probs.sum()
                
                indices = np.random.choice(
                    len(self.buffer[1]), 
                    min(batch_size, len(self.buffer[1])), 
                    replace=False, 
                    p=probs
                )
                
                batch = [self.buffer[1][i] for i in indices]
                
                # Calculate importance sampling weights
                weights = (len(self.buffer[1]) * probs[indices]) ** (-self.beta)
                weights /= weights.max()  # Normalize weights
                
                # Update beta
                self.beta = min(1.0, self.beta + self.beta_increment)
                
                # Store indices for priority updates
                indices_map = {i: idx for i, idx in enumerate(indices)}
            else:
                # Regular sampling
                current_states = list(self.buffer[current_depth])
                batch = random.sample(current_states, min(batch_size, len(current_states)))
            
            return batch, mastery_levels, weights, indices_map
        
        # Depth distribution similar to before but with PER within each depth
        depth_allocation = {}
        
        # Mastered depths (mastery > 0.99)
        mastered_depths = [d for d, m in mastery_levels.items() if m > 0.99]
        partially_mastered = [d for d, m in mastery_levels.items() if 0 < m <= 0.99]
        
        # 30% from mastered depths
        if mastered_depths:
            samples_per_depth = int(batch_size * 0.3) // len(mastered_depths)
            for depth in mastered_depths:
                depth_allocation[depth] = samples_per_depth
        
        # 30% from partially mastered depths
        if partially_mastered:
            weights_list = [mastery_levels[d] for d in partially_mastered]
            total_weight = sum(weights_list)
            partial_samples = int(batch_size * 0.3)
            
            for i, depth in enumerate(partially_mastered):
                if total_weight > 0:
                    depth_allocation[depth] = int(partial_samples * (weights_list[i] / total_weight))
                else:
                    depth_allocation[depth] = partial_samples // len(partially_mastered)
        
        # 20% from all previous depths
        all_prev_depths = list(range(1, current_depth))
        if all_prev_depths:
            prev_samples = int(batch_size * 0.2)
            samples_per_depth = prev_samples // len(all_prev_depths)
            for depth in all_prev_depths:
                depth_allocation[depth] = depth_allocation.get(depth, 0) + samples_per_depth
        
        # 20% from current depth
        depth_allocation[current_depth] = int(batch_size * 0.2)
        
        # Sample from each depth with prioritization if PER is enabled
        all_weights = []
        all_indices_map = {}
        samples_so_far = 0
        
        for depth, num_samples in depth_allocation.items():
            if depth not in self.buffer or not self.buffer[depth]:
                continue
                
            if self.use_per and depth in self.priorities and self.priorities[depth]:
                # Use PER for this depth
                probs = np.array(self.priorities[depth]) ** self.alpha
                probs /= probs.sum()
                
                indices = np.random.choice(
                    len(self.buffer[depth]), 
                    min(num_samples, len(self.buffer[depth])), 
                    replace=False, 
                    p=probs
                )
                
                depth_batch = [self.buffer[depth][i] for i in indices]
                batch.extend(depth_batch)
                
                # Calculate importance sampling weights
                depth_weights = (len(self.buffer[depth]) * probs[indices]) ** (-self.beta)
                all_weights.extend(depth_weights)
                
                # Store indices for priority updates
                for i, idx in enumerate(indices):
                    all_indices_map[samples_so_far + i] = (depth, idx)
                
                samples_so_far += len(depth_batch)
            else:
                # Regular sampling for this depth
                depth_batch = random.sample(
                    list(self.buffer[depth]), 
                    min(num_samples, len(self.buffer[depth]))
                )
                batch.extend(depth_batch)
                samples_so_far += len(depth_batch)
        
        # Fill remaining slots if needed
        while len(batch) < batch_size:
            depth = random.randint(1, current_depth)
            if depth in self.buffer and self.buffer[depth]:
                batch.append(random.choice(self.buffer[depth]))
        
        # Update beta for next time
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        # Normalize weights if we have them
        if all_weights:
            weights = np.array(all_weights)
            weights /= weights.max()  # Normalize weights
        
        return batch[:batch_size], mastery_levels, weights, all_indices_map
    
    def update_priorities(self, indices_map, losses):
        """Update priorities based on TD errors/losses"""
        if not self.use_per or indices_map is None:
            return
            
        for i, loss in enumerate(losses):
            if i in indices_map:
                if isinstance(indices_map[i], tuple):
                    # For multi-depth sampling
                    depth, idx = indices_map[i]
                    self.priorities[depth][idx] = min(loss + 1e-5, self.max_priority)  # Add small constant to avoid zero priority
                    self.max_priority = max(self.max_priority, self.priorities[depth][idx])
                else:
                    # For single depth sampling
                    self.priorities[1][indices_map[i]] = min(loss + 1e-5, self.max_priority)
                    self.max_priority = max(self.max_priority, self.priorities[1][indices_map[i]])
    
    def __len__(self):
        return sum(len(buffer) for buffer in self.buffer.values())

# Generate a scrambled state by applying random moves
def generate_scrambled_state(num_moves):
    state = SOLVED_STATE_3x3
    moves_applied = []
    
    if num_moves == 0:
        return state, moves_applied
    
    # Đảm bảo scramble tạo ra trạng thái khác với solved state
    attempt = 0
    max_attempts = 5  # Giới hạn số lần thử
    
    while attempt < max_attempts:
        test_state = SOLVED_STATE_3x3
        test_moves = []
        
        for _ in range(num_moves):
            # Tránh chọn những bước di chuyển triệt tiêu bước trước đó
            # Ví dụ: nếu trước đó là R, thì đừng chọn R'
            valid_moves = list(MOVE_NAMES)
            if test_moves:
                last_move = test_moves[-1]
                inverse_move = None
                
                # Xác định bước di chuyển nghịch đảo
                if last_move.endswith("'"):
                    inverse_move = last_move[:-1]  # Bỏ dấu '
                else:
                    inverse_move = last_move + "'"
                
                if inverse_move in valid_moves:
                    valid_moves.remove(inverse_move)
                
                # Tránh lặp lại cùng một bước di chuyển (như R R R)
                if last_move in valid_moves and len(valid_moves) > 1:
                    valid_moves.remove(last_move)
            
            move = random.choice(valid_moves)
            test_state = test_state.apply_move(move)
            test_moves.append(move)
        
        # Kiểm tra xem trạng thái mới có khác với trạng thái đã giải không
        if test_state != SOLVED_STATE_3x3 or num_moves <= 1:
            return test_state, test_moves
        
        attempt += 1
    
    # Nếu sau nhiều lần thử vẫn không tạo được trạng thái khác, 
    # thì trả về trạng thái cuối cùng
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

# Approximate Value Iteration (AVI) implementation
class DeepCubeASolver:
    def __init__(self, use_branched=False):
        self.use_branched = use_branched
        
        if use_branched:
            self.model = BranchedDeepCubeA().to(DEVICE)
        else:
            self.model = DeepCubeA().to(DEVICE)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=LEARNING_RATE)
        
        # Add LR scheduler
        self.use_lr_scheduler = USE_LR_SCHEDULER
        if self.use_lr_scheduler:
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, 
                mode='min', 
                factor=LR_SCHEDULER_FACTOR,
                patience=LR_SCHEDULER_PATIENCE,
                min_lr=MIN_LR,
                verbose=True
            )
        
        self.criterion = nn.MSELoss(reduction='none')  # Changed to 'none' for PER
        self.encoder = StateEncoder(use_branched=use_branched)
        self.replay_buffer = SmartReplayBuffer(REPLAY_BUFFER_SIZE)
        
        # Initialize replay buffer with solved state
        self.replay_buffer.add(SOLVED_STATE_3x3, 0.0, 1, 0.0)
    
    def predict_value(self, state):
        """Predict the value (cost-to-go) for a given state"""
        self.model.eval()
        with torch.no_grad():
            encoded = self.encoder.encode(state)
            if self.use_branched:
                return self.model(encoded[0].unsqueeze(0), encoded[1].unsqueeze(0)).item()
            else:
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
            return
        
        self.model.train()
        batch, mastery_levels, weights, indices_map = self.replay_buffer.sample_smart(batch_size, 1)
        states, values = zip(*batch)
        
        # Forward pass
        if self.use_branched:
            perm_batch, orient_batch = self.encoder.encode_batch(states)
            predictions = self.model(perm_batch, orient_batch).squeeze()
        else:
            inputs = self.encoder.encode_batch(states)
            predictions = self.model(inputs).squeeze()
        
        # Backward pass with importance sampling weights if PER is used
        target_values = torch.FloatTensor(values).to(DEVICE)
        
        # Element-wise loss for each sample
        element_losses = self.criterion(predictions, target_values)
        
        if weights is not None:
            # Apply importance sampling weights for PER
            weights_tensor = torch.FloatTensor(weights).to(DEVICE)
            # Ensure weights and losses have same size
            if len(weights_tensor) != len(element_losses):
                # Resize weights or truncate losses to match
                min_size = min(len(weights_tensor), len(element_losses))
                weights_tensor = weights_tensor[:min_size]
                element_losses = element_losses[:min_size]
            loss = (element_losses * weights_tensor).mean()
        else:
            loss = element_losses.mean()
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update priorities in the replay buffer if using PER
        if USE_PRIORITIZED_REPLAY and indices_map:
            sample_losses = element_losses.detach().cpu().numpy()
            self.replay_buffer.update_priorities(indices_map, sample_losses)
        
        return loss.item()

    def train_avi(self, num_iterations, start_iteration=0, start_scramble_depth=1):
        """Enhanced training with mastery-based experience replay and LR scheduling"""
        print(f"Training on {DEVICE} | Batch: {BATCH_SIZE} | LR: {LEARNING_RATE}")
        
        self.model = self.model.to(DEVICE)
        if hasattr(torch.backends, 'mps'):
            torch.backends.mps.enable_fallback_implementations = True
        
        solved_state = SOLVED_STATE_3x3
        self.replay_buffer.add(solved_state, 0.0, 1, 0.0)
        current_depth = start_scramble_depth
        
        metrics = {'losses': [], 'success_rates': [], 'depth_history': [], 'mastery_levels': {}}
        
        training_start_time = time.time()
        total_iterations = 0
        best_loss = float('inf')
        last_print_time = time.time()
        last_mastery_time = time.time()
        print_interval = 5  # Print every 5 seconds
        mastery_interval = 30  # Print mastery every 30 seconds
        
        while current_depth <= MAX_SCRAMBLE_DEPTH:
            required_iters = BASE_ITERS_PER_DEPTH + (current_depth - 1) * ITERS_INCREMENT
            print(f"\nDepth {current_depth}: {required_iters} iters")
            
            depth_start_time = time.time()
            depth_losses = []
            depth_epoch_losses = []  # For LR scheduler
            
            for iteration in range(required_iters):
                # Training step
                batch, mastery_levels, weights, indices_map = self.replay_buffer.sample_smart(BATCH_SIZE, current_depth)
                states, values = zip(*batch)
                
                # Print mastery levels periodically
                current_time = time.time()
                if current_time - last_mastery_time >= mastery_interval:
                    print("\nMastery:", end=" ")
                    for d, m in mastery_levels.items():
                        if m > 0.5:  # Only show significant mastery
                            print(f"D{d}:{m*100:.1f}%", end=" ")
                    print()
                    
                    # Also print current learning rate
                    for param_group in self.optimizer.param_groups:
                        print(f"Current LR: {param_group['lr']:.7f}")
                    
                    last_mastery_time = current_time
                
                self.optimizer.zero_grad()
                
                if self.use_branched:
                    perm_batch, orient_batch = self.encoder.encode_batch(states)
                    predictions = self.model(perm_batch, orient_batch).squeeze()
                else:
                    inputs = self.encoder.encode_batch(states)
                    predictions = self.model(inputs).squeeze()
                
                target_values = torch.FloatTensor(values).to(DEVICE)
                
                # Element-wise loss for each sample
                element_losses = self.criterion(predictions, target_values)
                
                if weights is not None:
                    # Apply importance sampling weights for PER
                    weights_tensor = torch.FloatTensor(weights).to(DEVICE)
                    # Ensure weights and losses have same size
                    if len(weights_tensor) != len(element_losses):
                        # Resize weights or truncate losses to match
                        min_size = min(len(weights_tensor), len(element_losses))
                        weights_tensor = weights_tensor[:min_size]
                        element_losses = element_losses[:min_size]
                    loss = (element_losses * weights_tensor).mean()
                else:
                    loss = element_losses.mean()
                
                loss.backward()
                self.optimizer.step()
                
                # Update priorities in replay buffer if using PER
                if USE_PRIORITIZED_REPLAY and indices_map:
                    sample_losses = element_losses.detach().cpu().numpy()
                    self.replay_buffer.update_priorities(indices_map, sample_losses)
                
                current_loss = loss.item()
                depth_losses.append(current_loss)
                depth_epoch_losses.append(current_loss)
                
                # Generate new experiences less frequently
                if iteration % 20 == 0:
                    new_states = []
                    new_values = []
                    for _ in range(BATCH_SIZE // 4):  # Reduced number of new experiences
                        scrambled_state = solved_state
                        for _ in range(current_depth):
                            move = random.choice(MOVE_NAMES)
                            scrambled_state = scrambled_state.apply_move(move)
                        new_states.append(scrambled_state)
                        new_values.append(float(current_depth))
                    
                    if self.use_branched:
                        perm_batch, orient_batch = self.encoder.encode_batch(new_states)
                        new_predictions = self.model(perm_batch, orient_batch).squeeze()
                    else:
                        inputs = self.encoder.encode_batch(new_states)
                        new_predictions = self.model(inputs).squeeze()
                    
                    for state, value, pred in zip(new_states, new_values, new_predictions):
                        state_loss = abs(value - pred.item())
                        self.replay_buffer.add(state, value, current_depth, state_loss)
                
                if current_loss < best_loss:
                    best_loss = current_loss
                
                # Apply LR scheduler every 100 iterations
                if self.use_lr_scheduler and iteration % 100 == 99:
                    avg_epoch_loss = np.mean(depth_epoch_losses)
                    self.scheduler.step(avg_epoch_loss)
                    depth_epoch_losses = []  # Reset for next epoch
                
                # Print progress less frequently (time-based)
                current_time = time.time()
                if current_time - last_print_time >= print_interval:
                    avg_loss = np.mean(depth_losses[-20:])
                    elapsed = current_time - depth_start_time
                    remaining = (elapsed / (iteration + 1)) * (required_iters - iteration - 1)
                    total_elapsed = current_time - training_start_time
                    
                    print(f"D{current_depth} {iteration+1}/{required_iters} | "
                          f"Loss: {avg_loss:.4f} | "
                          f"Time: {total_elapsed/3600:.1f}h | "
                          f"ETA: {remaining/60:.1f}m")
                    last_print_time = current_time
                
                # Save checkpoint
                if total_iterations % CHECKPOINT_INTERVAL == 0:
                    save_checkpoint(self, total_iterations, current_depth)
                
                total_iterations += 1
            
            # Validation phase
            print(f"\nValidating depth {current_depth}...")
            success_count = 0
            total_moves = 0
            validation_times = []
            
            for _ in range(VALIDATION_SIZE):
                test_state, _ = generate_scrambled_state(current_depth)
                solve_start = time.time()
                solution = self.solve(test_state, max_moves=current_depth * 2)
                solve_time = time.time() - solve_start
                validation_times.append(solve_time)
                
                if solution:
                    success_count += 1
                    total_moves += len(solution)
            
            success_rate = success_count / VALIDATION_SIZE
            avg_moves = total_moves / success_count if success_count > 0 else float('inf')
            avg_solve_time = np.mean(validation_times)
            
            print(f"Success: {success_rate*100:.1f}% | Moves: {avg_moves:.1f} | Time: {avg_solve_time:.2f}s")
            
            metrics['success_rates'].append(success_rate)
            metrics['depth_history'].append(current_depth)
            metrics['mastery_levels'][current_depth] = self.replay_buffer.get_depth_mastery(current_depth)
            
            if success_rate >= MIN_SUCCESS_RATE:
                print(f"✓ Increasing to depth {current_depth + 1}")
                current_depth += 1
            else:
                print(f"× Retrying depth {current_depth}")
                required_iters = int(required_iters * 0.5)
        
        save_checkpoint(self, total_iterations, current_depth)
        self.save_model(MODEL_PATH)
        print(f"\nTraining completed in {(time.time() - training_start_time)/3600:.1f}h")

    def rotate_state(self, state):
        """Helper method for data augmentation - rotates the cube state"""
        # Apply Y rotation (rotate entire cube around Y axis)
        moves = ["U", "R", "F", "D", "L", "B"]
        rotated_state = state
        for move in moves:
            rotated_state = rotated_state.apply_move(move)
        return rotated_state

    def solve(self, initial_state, max_moves=50):
        """Solve the cube from an initial state using batch-weighted A* search"""
        print("Starting A* search...")
        start_time = time.time()
        
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
    
    def save_model(self, path):
        """Save the trained model to disk"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'use_branched': self.use_branched
        }, path)
    
    def load_model(self, path):
        """Load a trained model from disk"""
        checkpoint = torch.load(path)
        
        # Ensure model architecture matches
        if checkpoint['use_branched'] != self.use_branched:
            print("Error: Model architecture mismatch. Cannot load model.")
            return False
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return True

# Visualization helpers
def print_solution(initial_state, solution_path):
    """Print the solution step by step"""
    print("\nSOLUTION PATH:")
    print("==============")
    
    state = initial_state
    print(f"Initial state:")
    print(state)
    
    for i, move in enumerate(solution_path):
        state = state.apply_move(move)
        print(f"\nStep {i+1}: Apply move {move}")
        print(state)
    
    print(f"\nFinal state solved: {state == SOLVED_STATE_3x3}")

def test_solver():
    """Test the DeepCubeA solver on a scrambled cube"""
    # Use simple network (not branched) for testing
    solver = DeepCubeASolver(use_branched=False)
    
    # Train for a few iterations (in practice, this would be much more)
    solver.train_avi(num_iterations=10)  # Just a few iterations for testing
    
    # Generate a scrambled cube with 5 moves
    scrambled_state, moves = generate_scrambled_state(5)
    print(f"Generated scrambled state with moves: {moves}")
    
    # Try to solve it
    solution = solver.solve(scrambled_state)
    
    if solution:
        print_solution(scrambled_state, solution)
    else:
        print("Could not find solution")

def main():
    """Enhanced main function with better testing"""
    print(f"Starting DeepCubeA training on {DEVICE}")
    
    # Initialize solver with branched network
    solver = DeepCubeASolver(use_branched=True)
    
    # Load checkpoint if exists
    start_iter, start_depth = load_checkpoint(solver)
    print(f"Resuming from iteration {start_iter}, scramble_depth {start_depth}")
    
    # Train with enhanced parameters
    metrics = solver.train_avi(
        num_iterations=NUM_AVI_ITERATIONS,
        start_iteration=start_iter,
        start_scramble_depth=start_depth
    )
    
    # Save final model
    solver.save_model(MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    
    # Comprehensive testing
    print("\nComprehensive Testing:")
    test_depths = [3, 5, 8, 10]  # Modified test depths to match our focus
    
    for depth in test_depths:
        print(f"\nTesting {depth}-move scrambles:")
        success_count = 0
        total_moves = 0
        total_time = 0
        num_tests = 5  # Increased from 10 to 20 for more thorough testing
        
        for test in range(num_tests):
            scrambled_state, moves = generate_scrambled_state(depth)
            print(f"Test {test + 1}/{num_tests}:")
            print(f"Scramble sequence: {moves}")
            
            start_time = time.time()
            solution = solver.solve(scrambled_state)
            solve_time = time.time() - start_time
            
            if solution:
                success_count += 1
                total_moves += len(solution)
                total_time += solve_time
                print(f"Solution found: {len(solution)} moves in {solve_time:.2f}s")
                
                # Verify solution
                test_state = scrambled_state
                for move in solution:
                    test_state = test_state.apply_move(move)
                if test_state == SOLVED_STATE_3x3:
                    print("✓ Solution verified correct")
                else:
                    print("✗ Solution verification failed")
            else:
                print("× No solution found")
        
        # Print statistics
        if success_count > 0:
            print(f"\nDepth {depth} Statistics:")
            print(f"Success rate: {success_count/num_tests*100:.1f}%")
            print(f"Average moves: {total_moves/success_count:.1f}")
            print(f"Average time: {total_time/success_count:.2f}s")
        else:
            print(f"\nDepth {depth}: No successful solutions")

if __name__ == "__main__":
    main()
