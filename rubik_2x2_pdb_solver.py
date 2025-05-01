import heapq
import time
from RubikState.rubik_2x2 import Rubik2x2State, MOVES_2x2, SOLVED_STATE_2x2, MOVE_NAMES
from rubik_2x2_pdb import PatternDatabase, FULL_PDB_PATH
from rubik_2x2_ai import generate_scrambled_state

# Node for A* search
class Node:
    def __init__(self, state, parent=None, move=None, g=0, h=0):
        self.state = state
        self.parent = parent
        self.move = move  # Move that led to this state from parent
        self.g = g  # Cost from start to current node
        self.h = h  # Heuristic estimate to goal (from pattern database)
        self.f = g + h  # f(n) = g(n) + h(n)
    
    def __lt__(self, other):
        # Prioritize lower f values, then lower h values
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f
    
    def get_solution_path(self):
        """Get the sequence of moves from start to this node"""
        path = []
        current = self
        while current.parent is not None:
            path.append(current.move)
            current = current.parent
        return path[::-1]  # Reverse to get path from start to current

class PDBSolver:
    def __init__(self, pdb=None):
        """Initialize solver with pattern database"""
        if pdb is None:
            self.pdb = PatternDatabase()
            # Try to load the full database
            if not self.pdb.load_full_database():
                print("Warning: Could not load pattern database, solving will be less efficient")
        else:
            self.pdb = pdb
        
        self.max_search_nodes = 1000000  # Limit search to prevent excessive memory use
        self.nodes_expanded = 0  # Biến đếm số nút đã duyệt
        self.stats = {}  # Thêm dict statistics để lưu các thông số
    
    def solve(self, initial_state, time_limit=30):
        """Solve the cube using A* search with pattern database heuristic"""
        start_time = time.time()
        
        # Reset số nút đã duyệt và thống kê
        self.nodes_expanded = 0
        self.stats = {
            'memory_used': 0,
            'effective_branching': 0,
            'pruning_ratio': 0,
            'algorithm': 'PDB 2x2'
        }
        
        # A* search
        open_set = []
        closed_set = set()
        
        # Use PDB for heuristic
        initial_h = self.pdb.get_distance(initial_state)
        if initial_h < 0:  # State not in database
            print("Warning: Initial state not found in pattern database")
            initial_h = 0  # Fallback to a simpler heuristic
        
        initial_node = Node(initial_state, g=0, h=initial_h)
        heapq.heappush(open_set, initial_node)
        
        max_memory_used = 1  # Ban đầu có 1 node trong open_set
        states_generated = 0  # Tổng số trạng thái được tạo ra
        states_pruned = 0  # Số trạng thái bị cắt tỉa
        
        while open_set and self.nodes_expanded < self.max_search_nodes:
            # Check time limit
            if time.time() - start_time > time_limit:
                print(f"Time limit reached after expanding {self.nodes_expanded} nodes")
                
                # Cập nhật stats trước khi thoát
                self.stats['memory_used'] = max_memory_used
                if states_generated > 0:
                    self.stats['pruning_ratio'] = (states_pruned / states_generated) * 100
                if self.nodes_expanded > 0:
                    self.stats['effective_branching'] = states_generated / self.nodes_expanded
                
                return None
            
            # Get node with lowest f value
            current_node = heapq.heappop(open_set)
            
            # If we reached the solved state
            if current_node.state == SOLVED_STATE_2x2:
                solution = current_node.get_solution_path()
                elapsed_time = time.time() - start_time
                
                # Cập nhật stats
                self.stats['memory_used'] = max_memory_used
                if states_generated > 0:
                    self.stats['pruning_ratio'] = (states_pruned / states_generated) * 100
                if self.nodes_expanded > 0:
                    self.stats['effective_branching'] = states_generated / self.nodes_expanded
                self.stats['solution_time'] = elapsed_time
                
                print(f"Found solution of length {len(solution)} after expanding {self.nodes_expanded} nodes in {elapsed_time:.3f} seconds")
                return solution
            
            # Add to closed set
            state_hash = hash(current_node.state)
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)
            
            # Expand node
            self.nodes_expanded += 1
            
            # Try all possible moves
            for move in MOVE_NAMES:
                next_state = current_node.state.apply_move(move)
                states_generated += 1
                
                # Skip if already in closed set
                if hash(next_state) in closed_set:
                    states_pruned += 1
                    continue
                
                # Calculate g, h, and f values
                g = current_node.g + 1
                
                # Get h value from pattern database
                h = self.pdb.get_distance(next_state)
                if h < 0:  # State not in database
                    h = 0  # Fallback
                
                # Create new node
                new_node = Node(next_state, parent=current_node, move=move, g=g, h=h)
                
                # Add to open set
                heapq.heappush(open_set, new_node)
            
            # Track maximum memory usage (max size of open_set + closed_set)
            current_memory = len(open_set) + len(closed_set)
            max_memory_used = max(max_memory_used, current_memory)
        
        # Cập nhật stats trước khi thoát
        self.stats['memory_used'] = max_memory_used
        if states_generated > 0:
            self.stats['pruning_ratio'] = (states_pruned / states_generated) * 100
        if self.nodes_expanded > 0:
            self.stats['effective_branching'] = states_generated / self.nodes_expanded
        
        print(f"Failed to find solution after expanding {self.nodes_expanded} nodes")
        return None

def verify_solution(initial_state, solution):
    """Verify that a solution correctly solves the cube"""
    state = initial_state
    for move in solution:
        state = state.apply_move(move)
    return state == SOLVED_STATE_2x2

def print_solution(initial_state, solution):
    """Print the solution step by step"""
    if not solution:
        print("No solution to print")
        return
        
    print("\nSOLUTION:")
    print(f"Length: {len(solution)} moves")
    print(f"Moves: {solution}")
    
    state = initial_state
    for i, move in enumerate(solution):
        state = state.apply_move(move)
        if i < 5 or i >= len(solution) - 5:  # Print first 5 and last 5 steps
            print(f"Step {i+1}: Apply {move}")
            if i == 4 and len(solution) > 10:
                print("...")

def batch_test(solver, depth, num_tests=10):
    """Test the solver on multiple scrambles of the same depth"""
    print(f"\nBatch testing {num_tests} scrambles at depth {depth}")
    print("=" * 40)
    
    successes = 0
    total_moves = 0
    total_time = 0
    total_nodes = 0
    min_moves = float('inf')
    max_moves = 0
    
    for i in range(num_tests):
        print(f"\nTest {i+1}/{num_tests}:")
        
        # Generate scramble
        scrambled_state, moves = generate_scrambled_state(depth)
        print(f"Scramble: {moves}")
        
        # Track solving time
        start_time = time.time()
        
        # Solve
        solution = solver.solve(scrambled_state)
        solve_time = time.time() - start_time
        
        if solution:
            is_valid = verify_solution(scrambled_state, solution)
            moves_count = len(solution)
            
            print(f"Solution found: {len(solution)} moves in {solve_time:.3f} seconds")
            print(f"Solution valid: {is_valid}")
            
            if is_valid:
                successes += 1
                total_moves += moves_count
                total_time += solve_time
                min_moves = min(min_moves, moves_count)
                max_moves = max(max_moves, moves_count)
        else:
            print("No solution found")
    
    # Print statistics
    print("\nBatch Test Results:")
    print("=" * 40)
    print(f"Success rate: {successes}/{num_tests} ({successes/num_tests*100:.1f}%)")
    
    if successes > 0:
        print(f"Average solution length: {total_moves/successes:.2f} moves")
        print(f"Min solution length: {min_moves} moves")
        print(f"Max solution length: {max_moves} moves")
        print(f"Average solve time: {total_time/successes:.3f} seconds")
    
    return successes, total_moves, total_time

def main():
    """Main function to test the PDB solver"""
    print("2x2 Rubik's Cube Pattern Database Solver")
    print("========================================")
    
    # Initialize the solver with pattern database
    pdb = PatternDatabase()
    if pdb.load_full_database():
        print(f"Loaded pattern database with {len(pdb)} states, max depth: {pdb.max_depth_reached}")
    else:
        print("Could not load pattern database, solving will be less efficient")
    
    solver = PDBSolver(pdb)
    
    # Interactive mode
    while True:
        print("\nOptions:")
        print("1. Solve a random scramble")
        print("2. Solve a custom scramble")
        print("3. Batch test multiple scrambles")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            depth = int(input("Enter scramble depth (1-11): ").strip())
            depth = max(1, min(11, depth))  # Clamp between 1 and 11
            
            scrambled_state, moves = generate_scrambled_state(depth)
            print(f"Generated scramble: {moves}")
            
            solution = solver.solve(scrambled_state)
            if solution:
                is_valid = verify_solution(scrambled_state, solution)
                print(f"Solution valid: {is_valid}")
                print_solution(scrambled_state, solution)
            else:
                print("No solution found within the constraints")
        
        elif choice == '2':
            print("Enter sequence of moves to scramble the cube (e.g. R U' F):")
            move_input = input().strip()
            moves = move_input.split()
            
            # Validate moves
            valid_moves = True
            for move in moves:
                if move not in MOVE_NAMES:
                    print(f"Invalid move: {move}")
                    valid_moves = False
                    break
            
            if valid_moves:
                # Apply scramble
                scrambled_state = SOLVED_STATE_2x2
                for move in moves:
                    scrambled_state = scrambled_state.apply_move(move)
                
                print("Solving...")
                solution = solver.solve(scrambled_state)
                if solution:
                    is_valid = verify_solution(scrambled_state, solution)
                    print(f"Solution valid: {is_valid}")
                    print_solution(scrambled_state, solution)
                else:
                    print("No solution found within the constraints")
        
        elif choice == '3':
            depth = int(input("Enter scramble depth (1-11): ").strip())
            depth = max(1, min(11, depth))  # Clamp between 1 and 11
            
            num_tests = int(input("Enter number of tests to run: ").strip())
            num_tests = max(1, min(100, num_tests))  # Limit to reasonable range
            
            batch_test(solver, depth, num_tests)
            
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice, please try again")

if __name__ == "__main__":
    main() 