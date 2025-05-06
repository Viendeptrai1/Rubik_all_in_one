import torch
import torch.nn as nn

# Define the actual Branched DeepCubeA architecture used in the checkpoint
class EnhancedBranchedDeepCubeA(nn.Module):
    def __init__(self):
        super(EnhancedBranchedDeepCubeA, self).__init__()
        
        # Permutation branch (cp, ep) - deeper architecture
        self.perm_fc1 = nn.Linear(20, 256)
        self.perm_fc2 = nn.Linear(256, 192)
        self.perm_fc3 = nn.Linear(192, 128)
        self.perm_fc4 = nn.Linear(128, 96)
        
        # Orientation branch (co, eo) - deeper architecture
        self.orient_fc1 = nn.Linear(20, 256)
        self.orient_fc2 = nn.Linear(256, 192)
        self.orient_fc3 = nn.Linear(192, 128)
        self.orient_fc4 = nn.Linear(128, 96)
        
        # Combined layers - more layers than the basic model
        self.combined_fc1 = nn.Linear(192, 160)  # 96+96=192 from both branches
        self.combined_fc2 = nn.Linear(160, 128)
        self.combined_fc3 = nn.Linear(128, 96)
        self.combined_fc4 = nn.Linear(96, 64)
        self.output = nn.Linear(64, 1)
        
        self.relu = nn.ReLU()
    
    def forward(self, x_perm, x_orient):
        # Process permutation branch - deeper
        p = self.relu(self.perm_fc1(x_perm))
        p = self.relu(self.perm_fc2(p))
        p = self.relu(self.perm_fc3(p))
        p = self.relu(self.perm_fc4(p))
        
        # Process orientation branch - deeper
        o = self.relu(self.orient_fc1(x_orient))
        o = self.relu(self.orient_fc2(o))
        o = self.relu(self.orient_fc3(o))
        o = self.relu(self.orient_fc4(o))
        
        # Combine branches
        combined = torch.cat((p, o), dim=1)
        combined = self.relu(self.combined_fc1(combined))
        combined = self.relu(self.combined_fc2(combined))
        combined = self.relu(self.combined_fc3(combined))
        combined = self.relu(self.combined_fc4(combined))
        return self.output(combined)

def analyze_checkpoint():
    print(f"Analyzing checkpoint: train_checkpoints/deepcube_checkpoint.pth")
    try:
        # Load the checkpoint
        checkpoint = torch.load("train_checkpoints/deepcube_checkpoint.pth", map_location=torch.device('cpu'))
        
        if 'model_state_dict' in checkpoint:
            state_dict = checkpoint['model_state_dict']
            # Get additional info from checkpoint
            print(f"\nCheckpoint info:")
            for key in checkpoint.keys():
                if key != 'model_state_dict':
                    print(f"  {key}: {checkpoint[key]}")
        else:
            state_dict = checkpoint
            print("Loaded direct state dict (no additional metadata)")
        
        # Print all keys in state dict to analyze structure
        print("\nModel state dict keys:")
        for key in state_dict.keys():
            param = state_dict[key]
            print(f"  {key}: {param.shape}")
        
        # Initialize the model with the correct architecture
        model = EnhancedBranchedDeepCubeA()
        
        # Try to load state dict
        model.load_state_dict(state_dict)
        print("\nState dict loaded successfully into EnhancedBranchedDeepCubeA model")
        
        # Count total parameters
        total_params = sum(p.numel() for p in model.parameters())
        print(f"\nTotal parameters: {total_params:,}")
        
        # Print model architecture
        print("\nModel architecture:")
        print(model)
        
        # Calculate total size
        model_size_bytes = sum(param.nelement() * param.element_size() for param in model.parameters())
        model_size_mb = model_size_bytes / (1024 * 1024)
        print(f"\nModel size: {model_size_mb:.2f} MB")
        
    except Exception as e:
        print(f"Error analyzing model: {e}")

if __name__ == "__main__":
    analyze_checkpoint() 