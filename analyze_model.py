import torch
import torch.nn as nn
import os

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

def analyze_model(model_path):
    print(f"Analyzing model: {model_path}")
    try:
        # Load the model
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        
        # Check if it's a checkpoint or just model state
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            use_branched = checkpoint.get('use_branched', True)
            print(f"Model loaded from checkpoint (use_branched: {use_branched})")
        else:
            state_dict = checkpoint
            
            # Determine model type from state dict keys
            has_branched_keys = any('perm' in key or 'orient' in key for key in state_dict.keys())
            use_branched = has_branched_keys
            print(f"Model loaded directly (detected branched: {use_branched})")
        
        # Print all keys in state dict to analyze structure
        print("\nModel state dict keys:")
        for key in state_dict.keys():
            param = state_dict[key]
            print(f"  {key}: {param.shape}")
        
        # Initialize the appropriate model type
        if use_branched:
            model = BranchedDeepCubeA()
            print("\nModel is a BranchedDeepCubeA network")
        else:
            model = DeepCubeA()
            print("\nModel is a DeepCubeA network")
        
        # Try to load state dict to check compatibility
        model.load_state_dict(state_dict)
        print("State dict loaded successfully into model")
        
        # Count total parameters
        total_params = sum(p.numel() for p in model.parameters())
        print(f"\nTotal parameters: {total_params:,}")
        
        # Print model architecture
        print("\nModel architecture:")
        print(model)
    
    except Exception as e:
        print(f"Error analyzing model: {e}")

# List available models
print("Available model files:")
for file in os.listdir("train_checkpoints"):
    if file.endswith(".pth"):
        print(f"  {file}")

# Analyze main model
print("\n" + "="*50)
analyze_model("train_checkpoints/deepcube_model.pth")

# Analyze checkpoint as well
print("\n" + "="*50)
analyze_model("train_checkpoints/deepcube_checkpoint.pth") 