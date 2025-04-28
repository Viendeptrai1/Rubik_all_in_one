import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import pickle
import time
from .rubik_chen import RubikState, MOVES_3x3, SOLVED_STATE_3x3

# Constants
DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
CHECKPOINT_DIR = "train_checkpoints"
MODEL_PATH = os.path.join(CHECKPOINT_DIR, "deepcube_model.pth")

class DeepCubeA(nn.Module):
    def __init__(self, use_branched=True):
        super(DeepCubeA, self).__init__()
        self.use_branched = use_branched
        
        if use_branched:
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
        else:
            # Simple network
            self.fc1 = nn.Linear(40, 512)
            self.fc2 = nn.Linear(512, 256)
            self.fc3 = nn.Linear(256, 128)
            self.fc4 = nn.Linear(128, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x_perm=None, x_orient=None):
        if self.use_branched:
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
        else:
            x = self.relu(self.fc1(x))
            x = self.relu(self.fc2(x))
            x = self.relu(self.fc3(x))
            return self.fc4(x)

class StateEncoder:
    def __init__(self, use_branched=True):
        self.use_branched = use_branched
    
    def encode(self, state):
        # Normalize values to [0,1] range
        cp_normalized = [val / 7.0 for val in state.cp]
        co_normalized = [val / 2.0 for val in state.co]
        ep_normalized = [val / 11.0 for val in state.ep]
        eo_normalized = list(state.eo)  # Already in [0,1]
        
        if self.use_branched:
            # Split into permutation and orientation
            perm_data = cp_normalized + ep_normalized
            orient_data = co_normalized + eo_normalized
            
            perm_tensor = torch.FloatTensor(perm_data).to(DEVICE)
            orient_tensor = torch.FloatTensor(orient_data).to(DEVICE)
            
            return perm_tensor, orient_tensor
        else:
            # Flatten everything into one vector
            flat_data = cp_normalized + co_normalized + ep_normalized + eo_normalized
            return torch.FloatTensor(flat_data).to(DEVICE)

class DeepCubeSolver:
    def __init__(self, model_path=MODEL_PATH):
        self.model = DeepCubeA(use_branched=True).to(DEVICE)
        self.encoder = StateEncoder(use_branched=True)
        self.load_model(model_path)
        self.model.eval()  # Set to evaluation mode
    
    def load_model(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"No model found at {path}")
        checkpoint = torch.load(path, map_location=DEVICE)
        self.model.load_state_dict(checkpoint['model_state_dict'])
    
    def predict_value(self, state):
        """Predict the cost-to-go for a given state"""
        with torch.no_grad():
            encoded = self.encoder.encode(state)
            if self.model.use_branched:
                return self.model(encoded[0].unsqueeze(0), encoded[1].unsqueeze(0)).item()
            else:
                return self.model(encoded.unsqueeze(0)).item()
    
    def solve(self, state, max_steps=50, max_nodes=100000, w_heur=0.8):
        """Solve using A* with the learned heuristic"""
        from heapq import heappush, heappop
        
        class Node:
            def __init__(self, state, parent=None, move=None, g=0, h=0):
                self.state = state
                self.parent = parent
                self.move = move
                self.g = g
                self.h = h
                self.f = g + w_heur * h
            
            def __lt__(self, other):
                return self.f < other.f
            
            def get_path(self):
                path = []
                current = self
                while current.parent:
                    path.append(current.move)
                    current = current.parent
                return path[::-1]
        
        # Statistics for the search
        stats = {
            'nodes_expanded': 0,
            'max_depth': 0,
            'solution_length': 0,
            'memory_used': 0,
            'effective_branching': 0,
            'pruning_ratio': 0
        }
        
        start_time = time.time()
        
        # Initialize search
        initial_h = self.predict_value(state)
        start_node = Node(state, g=0, h=initial_h)
        open_set = [start_node]
        closed_set = set()
        
        while open_set and stats['nodes_expanded'] < max_nodes:
            current = heappop(open_set)
            
            # Check if solved
            if current.state == SOLVED_STATE_3x3:
                path = current.get_path()
                stats['solution_length'] = len(path)
                stats['time_taken'] = time.time() - start_time
                return path, stats['nodes_expanded'], stats['time_taken'], stats
            
            # Add to closed set
            state_hash = hash(current.state)
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            # Expand node
            stats['nodes_expanded'] += 1
            stats['max_depth'] = max(stats['max_depth'], current.g)
            stats['memory_used'] = len(closed_set)
            
            # Try all possible moves
            for move in MOVES_3x3:
                next_state = current.state.apply_move(move)
                if hash(next_state) in closed_set:
                    continue
                
                g = current.g + 1
                if g > max_steps:
                    continue
                
                h = self.predict_value(next_state)
                new_node = Node(next_state, parent=current, move=move, g=g, h=h)
                heappush(open_set, new_node)
        
        # Calculate final statistics
        if stats['nodes_expanded'] > 0:
            stats['effective_branching'] = len(open_set) / stats['nodes_expanded']
            stats['pruning_ratio'] = (1 - len(closed_set) / (18 ** stats['max_depth'])) * 100
        
        stats['time_taken'] = time.time() - start_time
        return None, stats['nodes_expanded'], stats['time_taken'], stats 