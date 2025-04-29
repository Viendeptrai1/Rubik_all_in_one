import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import random
from collections import deque
import dgl
from dgl.nn import GraphConv
import time
from RubikState.rubik_2x2 import Rubik2x2State, MOVES_2x2, MOVE_NAMES, SOLVED_STATE_2x2

# Hyperparameters
BATCH_SIZE = 64
GAMMA = 0.99
EPSILON_START = 1.0
EPSILON_END = 0.1
EPSILON_DECAY = 50000
TARGET_UPDATE = 10
LEARNING_RATE = 1e-4
MEMORY_SIZE = 10000
NUM_EPISODES = 10000
MAX_STEPS = 20

# Device configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Convert Rubik state to graph representation
def state_to_graph(state):
    # Create a graph with 8 nodes (one for each corner)
    g = dgl.graph(([], []), num_nodes=8)
    
    # Node features: one-hot encoding for corner position and orientation
    # 8 positions + 3 orientations = 11 features per node
    node_features = torch.zeros(8, 11, dtype=torch.float)
    
    for i in range(8):
        # One-hot encoding for position
        pos = state.cp[i]
        node_features[i, pos] = 1.0
        
        # One-hot for orientation (0, 1, or 2)
        ori = state.co[i]
        node_features[i, 8 + ori] = 1.0
    
    # Create edges based on adjacency in the cube
    # Edges represent faces that connect corners
    # For a 2x2 cube, each corner is connected to 3 other corners through 3 faces
    # These connections represent the group structure
    src, dst = [], []
    
    # Define adjacency based on cube structure
    # Each corner is connected to 3 other corners through faces
    adjacency = {
        0: [1, 3, 4],  # URF connects to ULF, URB, DRF
        1: [0, 2, 5],  # ULF connects to URF, ULB, DLF
        2: [1, 3, 6],  # ULB connects to ULF, URB, DLB
        3: [0, 2, 7],  # URB connects to URF, ULB, DRB
        4: [0, 5, 7],  # DRF connects to URF, DLF, DRB
        5: [1, 4, 6],  # DLF connects to ULF, DRF, DLB
        6: [2, 5, 7],  # DLB connects to ULB, DLF, DRB
        7: [3, 4, 6]   # DRB connects to URB, DRF, DLB
    }
    
    for i in range(8):
        for j in adjacency[i]:
            src.append(i)
            dst.append(j)
    
    g.add_edges(src, dst)
    g.ndata['feat'] = node_features
    
    return g

# GNN model for Q-function approximation
class GNNQNetwork(nn.Module):
    def __init__(self, in_feats=11, hidden_dim=64, out_dim=len(MOVE_NAMES)):
        super(GNNQNetwork, self).__init__()
        
        # Graph convolutional layers
        self.conv1 = GraphConv(in_feats, hidden_dim)
        self.conv2 = GraphConv(hidden_dim, hidden_dim)
        
        # Output layers
        self.fc1 = nn.Linear(hidden_dim * 8, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, out_dim)
        
    def forward(self, g):
        h = g.ndata['feat']
        
        # Graph convolutions
        h = F.relu(self.conv1(g, h))
        h = F.relu(self.conv2(g, h))
        
        # Readout - concatenate all node features
        h = h.view(-1, 8 * h.size(1))
        
        # Fully connected layers
        h = F.relu(self.fc1(h))
        q_values = self.fc2(h)
        
        return q_values

# Experience replay memory
class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)
        
    def push(self, state, action, next_state, reward, done):
        self.memory.append((state, action, next_state, reward, done))
        
    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        state, action, next_state, reward, done = zip(*batch)
        return state, action, next_state, reward, done
        
    def __len__(self):
        return len(self.memory)

# Generate a scrambled cube state
def scramble_cube(num_moves=10):
    state = SOLVED_STATE_2x2
    moves_applied = []
    
    for _ in range(num_moves):
        move = random.choice(MOVE_NAMES)
        state = state.apply_move(move)
        moves_applied.append(move)
        
    return state, moves_applied

# Reward function
def compute_reward(state, next_state, done):
    if done:  # Solved the cube
        return 10.0
    
    # Calculate improvement in heuristic
    h_current = heuristic(state)
    h_next = heuristic(next_state)
    
    # Reward improvement in heuristic
    if h_next < h_current:
        return 1.0
    elif h_next > h_current:
        return -1.0
    else:
        return -0.1  # Small penalty for not making progress

# Enhanced heuristic function using group theory
def heuristic(state):
    # Count misplaced corners
    misplaced = sum(1 for i, pos in enumerate(state.cp) if pos != i)
    
    # Count misoriented corners
    misoriented = sum(1 for ori in state.co if ori != 0)
    
    # Check corner permutation parity
    perm_parity = sum(1 for i in range(8) for j in range(i+1, 8) 
                      if state.cp[i] > state.cp[j]) % 2
    
    # Check corner orientation sum (must be divisible by 3)
    orient_parity = sum(state.co) % 3 != 0
    
    # Combine metrics with weights
    return misplaced + misoriented + 2*perm_parity + 2*orient_parity

# Check if state is solved
def is_solved(state):
    return state == SOLVED_STATE_2x2

# Main training loop
def train():
    # Initialize models
    policy_net = GNNQNetwork().to(device)
    target_net = GNNQNetwork().to(device)
    target_net.load_state_dict(policy_net.state_dict())
    target_net.eval()
    
    # Initialize optimizer
    optimizer = optim.Adam(policy_net.parameters(), lr=LEARNING_RATE)
    
    # Initialize replay memory
    memory = ReplayMemory(MEMORY_SIZE)
    
    # Training stats
    steps_done = 0
    episode_rewards = []
    
    for episode in range(NUM_EPISODES):
        # Generate scrambled cube
        scramble_depth = random.randint(1, 10)
        state, scramble_moves = scramble_cube(scramble_depth)
        
        episode_reward = 0
        
        for step in range(MAX_STEPS):
            # Convert state to graph
            state_graph = state_to_graph(state)
            state_graph = state_graph.to(device)
            
            # Epsilon-greedy action selection
            epsilon = EPSILON_END + (EPSILON_START - EPSILON_END) * \
                     np.exp(-steps_done / EPSILON_DECAY)
            steps_done += 1
            
            if random.random() < epsilon:
                action_idx = random.randrange(len(MOVE_NAMES))
            else:
                with torch.no_grad():
                    q_values = policy_net(state_graph)
                    action_idx = q_values.max(0)[1].item()
            
            # Apply action
            move = MOVE_NAMES[action_idx]
            next_state = state.apply_move(move)
            
            # Check if solved
            done = is_solved(next_state)
            
            # Compute reward
            reward = compute_reward(state, next_state, done)
            episode_reward += reward
            
            # Store transition in memory
            memory.push(state, action_idx, next_state, reward, done)
            
            # Move to next state
            state = next_state
            
            # Train the network
            if len(memory) >= BATCH_SIZE:
                # Sample batch
                states, actions, next_states, rewards, dones = memory.sample(BATCH_SIZE)
                
                # Convert states and next_states to graphs
                batch_state_graphs = [state_to_graph(s).to(device) for s in states]
                batch_next_state_graphs = [state_to_graph(s).to(device) for s in next_states]
                
                # Process batch
                batch_graphs = dgl.batch(batch_state_graphs)
                batch_next_graphs = dgl.batch(batch_next_state_graphs)
                
                # Compute Q(s, a)
                state_q_values = policy_net(batch_graphs)
                state_action_values = state_q_values.gather(1, torch.tensor(actions, device=device).unsqueeze(1))
                
                # Compute V(s')
                with torch.no_grad():
                    next_state_values = target_net(batch_next_graphs).max(1)[0]
                    next_state_values[torch.tensor(dones, device=device)] = 0.0
                
                # Compute expected Q values
                expected_state_action_values = (torch.tensor(rewards, device=device) + 
                                               GAMMA * next_state_values).unsqueeze(1)
                
                # Compute loss
                loss = F.smooth_l1_loss(state_action_values, expected_state_action_values)
                
                # Optimize
                optimizer.zero_grad()
                loss.backward()
                for param in policy_net.parameters():
                    param.grad.data.clamp_(-1, 1)  # Gradient clipping
                optimizer.step()
            
            # Check if solved or max steps reached
            if done:
                print(f"Episode {episode}: Solved in {step+1} steps (scramble depth: {scramble_depth})")
                break
                
            if step == MAX_STEPS - 1:
                print(f"Episode {episode}: Failed to solve (scramble depth: {scramble_depth})")
        
        # Update target network
        if episode % TARGET_UPDATE == 0:
            target_net.load_state_dict(policy_net.state_dict())
            
        # Track rewards
        episode_rewards.append(episode_reward)
        
        # Print stats every 100 episodes
        if episode % 100 == 0:
            mean_reward = np.mean(episode_rewards[-100:])
            print(f"Episode {episode}, Average reward: {mean_reward:.2f}, Epsilon: {epsilon:.2f}")
            
            # Save model
            torch.save(policy_net.state_dict(), f"gnn_rubik_model_ep{episode}.pth")

# Test the trained model
def test(model_path, num_tests=100):
    # Load model
    model = GNNQNetwork().to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    success_count = 0
    avg_steps = 0
    
    for test_idx in range(num_tests):
        # Generate scrambled cube
        scramble_depth = random.randint(1, 10)
        state, scramble_moves = scramble_cube(scramble_depth)
        
        steps = 0
        solved = False
        
        # Try to solve
        for step in range(50):  # Increased max steps for testing
            # Convert state to graph
            state_graph = state_to_graph(state)
            state_graph = state_graph.to(device)
            
            # Get Q values
            with torch.no_grad():
                q_values = model(state_graph)
                action_idx = q_values.max(0)[1].item()
            
            # Apply move
            move = MOVE_NAMES[action_idx]
            state = state.apply_move(move)
            steps += 1
            
            # Check if solved
            if is_solved(state):
                solved = True
                break
        
        if solved:
            success_count += 1
            avg_steps += steps
            print(f"Test {test_idx}: Solved in {steps} steps (scramble depth: {scramble_depth})")
        else:
            print(f"Test {test_idx}: Failed to solve (scramble depth: {scramble_depth})")
    
    # Print results
    success_rate = success_count / num_tests * 100
    avg_steps = avg_steps / success_count if success_count > 0 else 0
    
    print(f"\nSuccess rate: {success_rate:.2f}%")
    print(f"Average steps for successful solves: {avg_steps:.2f}")

if __name__ == "__main__":
    print("Starting training...")
    train()
    
    print("\nTesting trained model...")
    test("gnn_rubik_model_ep9000.pth")
