import os
import pickle
import time
from collections import deque
import numpy as np
import sys
from RubikState.rubik_2x2 import Rubik2x2State, MOVES_2x2, SOLVED_STATE_2x2, MOVE_NAMES

# Constants
PDB_DIR = "pattern_database_2x2"
CHECKPOINT_PATH = os.path.join(PDB_DIR, "pdb_checkpoint.pkl")
FULL_PDB_PATH = os.path.join(PDB_DIR, "full_pdb.pkl")
BATCH_SIZE = 100000  # Number of states to process before saving a checkpoint
MAX_DEPTH = 6  # Maximum depth to explore (should be enough for 2x2 cube)
MEMORY_CHECK_INTERVAL = 10000  # How often to check memory usage

def ensure_pdb_dir():
    """Ensure the pattern database directory exists"""
    if not os.path.exists(PDB_DIR):
        os.makedirs(PDB_DIR)

class PatternDatabase:
    """Pattern Database for 2x2 Rubik's Cube"""
    def __init__(self):
        self.pdb = {}  # Dictionary mapping state hash to distance from solved
        self.max_depth_reached = 0
        self.states_explored = 0
        self.last_checkpoint_size = 0
        
    def __len__(self):
        return len(self.pdb)
    
    def get_distance(self, state):
        """Get distance from solved state"""
        state_hash = hash(state)
        return self.pdb.get(state_hash, -1)  # Return -1 if state not in database
    
    def add_state(self, state, distance):
        """Add a state to the database"""
        state_hash = hash(state)
        if state_hash not in self.pdb:
            self.pdb[state_hash] = distance
            self.states_explored += 1
            return True
        return False
    
    def save_checkpoint(self, queue=None):
        """Save the current database state as a checkpoint"""
        ensure_pdb_dir()
        checkpoint_data = {
            'pdb': self.pdb,
            'max_depth_reached': self.max_depth_reached,
            'states_explored': self.states_explored,
            'queue': list(queue) if queue is not None else None
        }
        
        # Save to a temporary file first to prevent corruption if interrupted
        temp_path = CHECKPOINT_PATH + ".tmp"
        with open(temp_path, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Rename to the actual checkpoint file
        os.replace(temp_path, CHECKPOINT_PATH)
        
        self.last_checkpoint_size = len(self)
        return len(self)
    
    def load_checkpoint(self):
        """Load the pattern database from a checkpoint"""
        if not os.path.exists(CHECKPOINT_PATH):
            return None  # No checkpoint exists
        
        try:
            with open(CHECKPOINT_PATH, 'rb') as f:
                checkpoint_data = pickle.load(f)
            
            self.pdb = checkpoint_data['pdb']
            self.max_depth_reached = checkpoint_data['max_depth_reached']
            self.states_explored = checkpoint_data['states_explored']
            self.last_checkpoint_size = len(self)
            
            # Return the saved queue to resume BFS
            return checkpoint_data.get('queue')
        except Exception as e:
            print(f"Error loading checkpoint: {str(e)}")
            return None
    
    def save_full_database(self):
        """Save the complete pattern database"""
        ensure_pdb_dir()
        data = {
            'pdb': self.pdb,
            'max_depth_reached': self.max_depth_reached,
            'states_explored': self.states_explored
        }
        
        # Save to a temporary file first
        temp_path = FULL_PDB_PATH + ".tmp"
        with open(temp_path, 'wb') as f:
            pickle.dump(data, f)
        
        # Rename to the actual file
        os.replace(temp_path, FULL_PDB_PATH)
        
    def load_full_database(self):
        """Load the complete pattern database"""
        if not os.path.exists(FULL_PDB_PATH):
            return False
        
        try:
            with open(FULL_PDB_PATH, 'rb') as f:
                data = pickle.load(f)
            
            self.pdb = data['pdb']
            self.max_depth_reached = data['max_depth_reached']
            self.states_explored = data['states_explored']
            return True
        except Exception as e:
            print(f"Error loading full database: {str(e)}")
            return False

def check_memory_usage():
    """Check current memory usage and return percentage used"""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return memory_info.rss / (psutil.virtual_memory().total)
    except ImportError:
        # If psutil is not available, use a simple heuristic based on objects count
        return 0.0  # Default to not triggering memory saving

def generate_pattern_database(resume=True, max_memory_percent=0.7):
    """Generate the pattern database using BFS, with memory management"""
    print("Initializing Pattern Database generation...")
    start_time = time.time()
    
    pdb = PatternDatabase()
    queue = deque()
    
    # Try to load from checkpoint if resume is True
    if resume:
        saved_queue = pdb.load_checkpoint()
        if saved_queue is not None:
            queue = deque(saved_queue)
            print(f"Resumed from checkpoint with {len(pdb)} states explored")
            print(f"Maximum depth reached so far: {pdb.max_depth_reached}")
        else:
            print("No checkpoint found, starting fresh")
    
    # If queue is empty (no checkpoint or empty checkpoint), initialize with solved state
    if not queue:
        solved_state = SOLVED_STATE_2x2
        pdb.add_state(solved_state, 0)
        queue.append((solved_state, 0))  # (state, distance)
    
    # Record initial size
    initial_size = len(pdb)
    
    try:
        # BFS loop
        while queue and pdb.max_depth_reached < MAX_DEPTH:
            current_state, distance = queue.popleft()
            
            # Skip if we've already found a shorter path
            if pdb.get_distance(current_state) < distance:
                continue
            
            # Update max depth reached
            if distance > pdb.max_depth_reached:
                pdb.max_depth_reached = distance
                print(f"Reached depth {distance}, states explored: {pdb.states_explored}, database size: {len(pdb)}")
                # Save a checkpoint when we reach a new depth
                pdb.save_checkpoint(queue)
            
            # Try all possible moves
            for move in MOVE_NAMES:
                next_state = current_state.apply_move(move)
                
                # Add to database and queue if it's a new state
                if pdb.add_state(next_state, distance + 1):
                    queue.append((next_state, distance + 1))
            
            # Check if we should save a checkpoint
            if pdb.states_explored % BATCH_SIZE == 0:
                print(f"Processed {pdb.states_explored} states, database size: {len(pdb)}")
                pdb.save_checkpoint(queue)
            
            # Check memory usage periodically
            if pdb.states_explored % MEMORY_CHECK_INTERVAL == 0:
                memory_percent = check_memory_usage()
                if memory_percent > max_memory_percent:
                    print(f"Memory usage high ({memory_percent:.1%}), saving checkpoint and exiting")
                    pdb.save_checkpoint(queue)
                    print("Run the script again to continue from the checkpoint")
                    return pdb
    
    except KeyboardInterrupt:
        print("\nInterrupted by user, saving checkpoint...")
        pdb.save_checkpoint(queue)
        print("You can resume later by running with resume=True")
        return pdb
    
    # Save the final complete database
    elapsed_time = time.time() - start_time
    print(f"\nCompleted PDB generation in {elapsed_time:.1f} seconds")
    print(f"Final database size: {len(pdb)} states")
    print(f"New states added in this run: {len(pdb) - initial_size}")
    print(f"Maximum depth reached: {pdb.max_depth_reached}")
    
    pdb.save_full_database()
    print(f"Full database saved to {FULL_PDB_PATH}")
    
    return pdb

def look_up_distance(pdb, state):
    """Look up the distance to solve a specific state"""
    distance = pdb.get_distance(state)
    if distance >= 0:
        return distance
    return "Not found in database"

def test_pdb_solver(pdb, scramble_depth=5, num_tests=10):
    """Test the pattern database on random scrambles"""
    print(f"\nTesting PDB on {num_tests} random scrambles with depth {scramble_depth}")
    
    success_count = 0
    
    for i in range(num_tests):
        # Generate a scrambled state
        scrambled_state = SOLVED_STATE_2x2
        moves_applied = []
        
        for _ in range(scramble_depth):
            # Avoid moves that undo the previous move
            valid_moves = list(MOVE_NAMES)
            if moves_applied:
                last_move = moves_applied[-1]
                inverse_move = None
                
                # Determine inverse move
                if last_move.endswith("'"):
                    inverse_move = last_move[:-1]
                else:
                    inverse_move = last_move + "'"
                
                if inverse_move in valid_moves:
                    valid_moves.remove(inverse_move)
                
                # Avoid repeating the same move
                if last_move in valid_moves and len(valid_moves) > 1:
                    valid_moves.remove(last_move)
            
            move = valid_moves[np.random.randint(len(valid_moves))]
            scrambled_state = scrambled_state.apply_move(move)
            moves_applied.append(move)
        
        distance = pdb.get_distance(scrambled_state)
        
        print(f"Test {i+1}: Scramble {moves_applied}")
        if distance >= 0:
            print(f"  PDB distance: {distance}")
            if distance <= len(moves_applied):
                success_count += 1
            else:
                print("  Warning: PDB distance is greater than scramble depth!")
        else:
            print("  State not found in database!")
    
    print(f"Success rate: {success_count/num_tests*100:.1f}%")

def main():
    """Main function to generate and test the pattern database"""
    print("2x2 Rubik's Cube Pattern Database Generator")
    print("===========================================")
    
    # Check if full database already exists
    pdb = PatternDatabase()
    if os.path.exists(FULL_PDB_PATH):
        print(f"Found existing pattern database at {FULL_PDB_PATH}")
        load_choice = input("Do you want to load it? (y/n): ").strip().lower()
        if load_choice == 'y':
            if pdb.load_full_database():
                print(f"Loaded database with {len(pdb)} states, max depth: {pdb.max_depth_reached}")
                # Test the loaded database
                test_pdb_solver(pdb)
                return
            else:
                print("Failed to load database, generating new one...")
    
    # If no existing database or user chose not to load it
    print("\nGenerating new pattern database...")
    try:
        pdb = generate_pattern_database()
        
        # Test the generated database
        if len(pdb) > 0:
            test_pdb_solver(pdb)
    except Exception as e:
        print(f"Error during PDB generation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 