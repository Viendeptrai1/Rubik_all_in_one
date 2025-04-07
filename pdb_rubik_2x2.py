from RubikState.rubik_2x2 import Rubik2x2State, SOLVED_STATE_2x2, MOVES_2x2
import time
import pickle
import os
from collections import deque
import heapq
import random

class PatternDatabase:
    """
    Pattern Database for 2x2 Rubik's Cube.
    Precomputes and stores the minimum number of moves required to solve different subproblems.
    """
    def __init__(self, filename=None):
        # Corner permutation database (CP)
        self.cp_database = {}
        
        # Corner orientation database (CO)
        self.co_database = {}
        
        self.filename = filename
        
        # Load from file if available
        if filename and os.path.exists(filename):
            self.load()
    
    def generate_corner_permutation_database(self, max_depth=8):
        """
        Generate database for corner permutation (CP).
        Ignores the orientation (CO).
        """
        print("Generating corner permutation database...")
        start_time = time.time()
        
        # Start with solved state
        start_state = SOLVED_STATE_2x2.copy()
        
        # Create a new state with only permutation info (set all orientations to 0)
        perm_state = Rubik2x2State(cp=start_state.cp, co=[0] * 8)
        
        # BFS to generate database
        queue = deque([(perm_state, [])])  # (state, moves)
        visited = {perm_state: 0}  # State -> distance
        
        while queue:
            state, path = queue.popleft()
            dist = len(path)
            
            if dist >= max_depth:
                continue
            
            # Try all moves
            for move in MOVES_2x2:
                new_state = state.apply_move(move, MOVES_2x2)
                
                # Create a new state with only permutation info 
                perm_new_state = Rubik2x2State(cp=new_state.cp, co=[0] * 8)
                
                if perm_new_state not in visited:
                    queue.append((perm_new_state, path + [move]))
                    visited[perm_new_state] = dist + 1
                    
                    # Store in database - use the CP tuple as key
                    self.cp_database[tuple(perm_new_state.cp)] = dist + 1
        
        print(f"Corner permutation database generated with {len(self.cp_database)} entries")
        print(f"Time: {time.time() - start_time:.2f} seconds")
    
    def generate_corner_orientation_database(self, max_depth=8):
        """
        Generate database for corner orientation (CO).
        Ignores the permutation (CP).
        """
        print("Generating corner orientation database...")
        start_time = time.time()
        
        # Start with solved state
        start_state = SOLVED_STATE_2x2.copy()
        
        # Create a new state with only orientation info (set all permutations to identity)
        orient_state = Rubik2x2State(cp=list(range(8)), co=start_state.co)
        
        # BFS to generate database
        queue = deque([(orient_state, [])])  # (state, moves)
        visited = {orient_state: 0}  # State -> distance
        
        while queue:
            state, path = queue.popleft()
            dist = len(path)
            
            if dist >= max_depth:
                continue
            
            # Try all moves
            for move in MOVES_2x2:
                new_state = state.apply_move(move, MOVES_2x2)
                
                # Create a new state with only orientation info
                orient_new_state = Rubik2x2State(cp=list(range(8)), co=new_state.co)
                
                if orient_new_state not in visited:
                    queue.append((orient_new_state, path + [move]))
                    visited[orient_new_state] = dist + 1
                    
                    # Store in database - use the CO tuple as key
                    self.co_database[tuple(orient_new_state.co)] = dist + 1
        
        print(f"Corner orientation database generated with {len(self.co_database)} entries")
        print(f"Time: {time.time() - start_time:.2f} seconds")
    
    def save(self, filename=None):
        """Save the pattern database to a file."""
        if filename is None:
            filename = self.filename
        
        if filename is None:
            filename = "rubik_2x2_pdb.pkl"
            
        with open(filename, "wb") as f:
            pickle.dump({
                "cp_database": self.cp_database,
                "co_database": self.co_database
            }, f)
        
        print(f"Pattern database saved to {filename}")
    
    def load(self, filename=None):
        """Load the pattern database from a file."""
        if filename is None:
            filename = self.filename
            
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
                self.cp_database = data["cp_database"]
                self.co_database = data["co_database"]
            
            print(f"Pattern database loaded from {filename}")
            print(f"CP database: {len(self.cp_database)} entries")
            print(f"CO database: {len(self.co_database)} entries")
            return True
        except:
            print(f"Error loading pattern database from {filename}")
            return False
    
    def get_heuristic(self, state):
        """
        Get the heuristic value for a state.
        Returns the maximum of the permutation and orientation heuristics.
        """
        cp_value = self.cp_database.get(tuple(state.cp), 0)
        co_value = self.co_database.get(tuple(state.co), 0)
        
        # Return the maximum since both subproblems must be solved
        return max(cp_value, co_value)

def pdb_heuristic_2x2(state, pdb):
    """Heuristic function using the pattern database."""
    return pdb.get_heuristic(state)

def a_star_pdb_2x2(start_state, goal_state=None, moves_dict=None, time_limit=30, pdb=None):
    """
    A* algorithm for 2x2 Rubik's Cube using Pattern Database heuristic.
    """
    if goal_state is None:
        goal_state = SOLVED_STATE_2x2
    
    if moves_dict is None:
        moves_dict = MOVES_2x2
    
    if pdb is None:
        raise ValueError("Pattern database is required for A* PDB algorithm")
    
    start_time = time.time()
    nodes_explored = 0
    
    # Priority queue for A*: (f_value, state_hash, state, path)
    # f_value = g_value (path length) + h_value (heuristic)
    h_value = pdb_heuristic_2x2(start_state, pdb)
    frontier = [(h_value, hash(start_state), start_state, [])]
    
    # Dictionary to track visited states and their shortest paths
    visited = {start_state: (0, [])}  # state -> (g_value, path)
    
    while frontier and time.time() - start_time < time_limit:
        f_value, _, state, path = heapq.heappop(frontier)
        nodes_explored += 1
        
        g_value = len(path)
        
        # Check if we reached the goal
        if state == goal_state:
            end_time = time.time()
            return path, nodes_explored, end_time - start_time
        
        # Try all possible moves
        for move in moves_dict:
            new_state = state.apply_move(move, moves_dict)
            new_g_value = g_value + 1
            new_path = path + [move]
            
            # Skip if we've seen this state with a shorter or equal path
            if new_state in visited and visited[new_state][0] <= new_g_value:
                continue
            
            # Update visited and add to frontier
            visited[new_state] = (new_g_value, new_path)
            h_value = pdb_heuristic_2x2(new_state, pdb)
            heapq.heappush(frontier, (new_g_value + h_value, hash(new_state), new_state, new_path))
    
    end_time = time.time()
    return None, nodes_explored, end_time - start_time

def test_pdb_effectiveness(scramble_depths=None, num_tests=5):
    """
    Test the effectiveness of the pattern database by comparing it with
    regular A* algorithm on scrambled cubes of different depths.
    """
    if scramble_depths is None:
        scramble_depths = [4, 6, 8, 10]
    
    # Create or load pattern database
    pdb_filename = "rubik_2x2_pdb.pkl"
    pdb = PatternDatabase(pdb_filename)
    
    if not os.path.exists(pdb_filename):
        print("Pattern database not found. Generating...")
        pdb.generate_corner_permutation_database()
        pdb.generate_corner_orientation_database()
        pdb.save()
    
    # Regular A* heuristic (from the existing code)
    from RubikState.rubik_solver import a_star_2x2
    
    print("\n===== TESTING PDB EFFECTIVENESS =====")
    print(f"Running {num_tests} tests for each scramble depth: {scramble_depths}")
    
    for depth in scramble_depths:
        print(f"\n--- Testing scramble depth {depth} ---")
        
        total_pdb_nodes = 0
        total_pdb_time = 0
        total_reg_nodes = 0
        total_reg_time = 0
        total_pdb_path_length = 0
        total_reg_path_length = 0
        success_pdb = 0
        success_reg = 0
        
        for test in range(num_tests):
            # Generate a scrambled cube
            state = SOLVED_STATE_2x2.copy()
            scramble = []
            
            for _ in range(depth):
                move = random.choice(list(MOVES_2x2.keys()))
                state = state.apply_move(move, MOVES_2x2)
                scramble.append(move)
            
            print(f"\nTest {test+1}: Scramble: {' '.join(scramble)}")
            
            # Solve with PDB A*
            pdb_path, pdb_nodes, pdb_time = a_star_pdb_2x2(state, time_limit=60, pdb=pdb)
            
            if pdb_path:
                success_pdb += 1
                total_pdb_nodes += pdb_nodes
                total_pdb_time += pdb_time
                total_pdb_path_length += len(pdb_path)
                print(f"PDB A*: Solved in {len(pdb_path)} moves, {pdb_nodes} nodes, {pdb_time:.4f}s")
                print(f"Solution: {' '.join(pdb_path)}")
                
                # Verify solution
                test_state = state.copy()
                for move in pdb_path:
                    test_state = test_state.apply_move(move, MOVES_2x2)
                
                if test_state == SOLVED_STATE_2x2:
                    print("✓ Solution is correct")
                else:
                    print("✗ Solution is incorrect!")
            else:
                print(f"PDB A*: Failed to solve in time limit. Explored {pdb_nodes} nodes in {pdb_time:.4f}s")
            
            # Solve with regular A*
            reg_path, reg_nodes, reg_time = a_star_2x2(state, time_limit=60)
            
            if reg_path:
                success_reg += 1
                total_reg_nodes += reg_nodes
                total_reg_time += reg_time
                total_reg_path_length += len(reg_path)
                print(f"Regular A*: Solved in {len(reg_path)} moves, {reg_nodes} nodes, {reg_time:.4f}s")
                print(f"Solution: {' '.join(reg_path)}")
                
                # Verify solution
                test_state = state.copy()
                for move in reg_path:
                    test_state = test_state.apply_move(move, MOVES_2x2)
                
                if test_state == SOLVED_STATE_2x2:
                    print("✓ Solution is correct")
                else:
                    print("✗ Solution is incorrect!")
            else:
                print(f"Regular A*: Failed to solve in time limit. Explored {reg_nodes} nodes in {reg_time:.4f}s")
        
        # Print summary for this depth
        print(f"\n--- Summary for depth {depth} ---")
        
        if success_pdb > 0:
            avg_pdb_nodes = total_pdb_nodes / success_pdb
            avg_pdb_time = total_pdb_time / success_pdb
            avg_pdb_length = total_pdb_path_length / success_pdb
            print(f"PDB A*: {success_pdb}/{num_tests} solved. Avg nodes: {avg_pdb_nodes:.1f}, Avg time: {avg_pdb_time:.4f}s, Avg length: {avg_pdb_length:.1f}")
        else:
            print(f"PDB A*: 0/{num_tests} solved.")
            
        if success_reg > 0:
            avg_reg_nodes = total_reg_nodes / success_reg
            avg_reg_time = total_reg_time / success_reg
            avg_reg_length = total_reg_path_length / success_reg
            print(f"Regular A*: {success_reg}/{num_tests} solved. Avg nodes: {avg_reg_nodes:.1f}, Avg time: {avg_reg_time:.4f}s, Avg length: {avg_reg_length:.1f}")
        else:
            print(f"Regular A*: 0/{num_tests} solved.")
            
        if success_pdb > 0 and success_reg > 0:
            print(f"Improvement: {avg_reg_nodes/avg_pdb_nodes:.2f}x fewer nodes, {avg_reg_time/avg_pdb_time:.2f}x faster")

def main():
    """Main function to test the pattern database."""
    # Create pattern database
    pdb = PatternDatabase("rubik_2x2_pdb.pkl")
    
    # Generate database if it doesn't exist
    if not os.path.exists("rubik_2x2_pdb.pkl"):
        print("Generating pattern database...")
        pdb.generate_corner_permutation_database()
        pdb.generate_corner_orientation_database()
        pdb.save()
    else:
        pdb.load()
    
    # Test the effectiveness of the pattern database
    test_pdb_effectiveness(scramble_depths=[4, 6, 8, 10, 12], num_tests=3)

if __name__ == "__main__":
    main() 