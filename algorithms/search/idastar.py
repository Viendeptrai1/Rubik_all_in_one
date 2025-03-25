from ..base import SolverAlgorithm
import time
from .optimizations import SearchOptimizations

class IDAStar(SolverAlgorithm):
    def __init__(self, cube):
        super().__init__(cube)
        # Initialize pattern databases
        self.corner_db = {}
        self.edge_db = {}
        self._initialize_pattern_dbs()
        # Transposition table to avoid repeated work
        self.transposition_table = {}
        
    @property
    def complexity(self):
        return "O(b^d)"
        
    @property
    def description(self):
        return """IDA* combines iterative deepening with A*'s heuristic
        to find optimal solution while using less memory than A*."""
    
    def _initialize_pattern_dbs(self):
        """Initialize pattern databases for better heuristics"""
        if self.signals:
            self.signals.status.emit("Initializing pattern databases...")
        
        solved_cube = self._get_solved_cube()
        self.corner_db = SearchOptimizations.compute_corner_distance_db(solved_cube)
        self.edge_db = SearchOptimizations.compute_edge_distance_db(solved_cube)
        
    def solve(self, progress_callback=None):
        # Lưu callback để cập nhật tiến trình
        if progress_callback:
            self.set_progress_callback(progress_callback)
            
        start_time = time.time()
        
        # Optimization: Get initial heuristic value
        initial_h = SearchOptimizations.advanced_heuristic(self.cube, self.corner_db, self.edge_db)
        threshold = initial_h
        
        # Clear transposition table for new search
        self.transposition_table = {}
        
        # Iterative deepening loop
        while True:
            if self.signals:
                self.signals.status.emit(f"IDA* iteration with threshold {threshold}")
                
            solution = []
            visited = set()
            result = self._search(self.cube, 0, threshold, solution, visited)
            
            if result == True:
                self.time_taken = time.time() - start_time
                # Optimize the final move sequence
                self.solution = SearchOptimizations.optimize_move_sequence(solution)
                return self.solution
                
            if result == float('inf'):
                return None
                
            # Update threshold for next iteration
            threshold = result
            
    def _search(self, cube, g, threshold, solution, visited):
        if self.update_state_count():
            if self.states_explored >= self.max_states:
                return float('inf')
        
        # Use enhanced heuristic
        h = SearchOptimizations.advanced_heuristic(cube, self.corner_db, self.edge_db)
        f = g + h
        
        if f > threshold:
            return f
            
        if self._is_solved(cube):
            return True
            
        # Optimization: Use transposition table to avoid duplicated work
        state_key = SearchOptimizations.optimized_state_key(cube)
        
        if state_key in self.transposition_table and self.transposition_table[state_key] <= g:
            return float('inf')  # Already visited with lower or equal cost
            
        self.transposition_table[state_key] = g
        
        minimum = float('inf')
        
        # Get possible moves
        possible_moves = self._get_possible_moves()
        
        # Optimization: Order moves by heuristic value (most promising first)
        move_values = []
        for move in possible_moves:
            if solution and SearchOptimizations.is_move_redundant(solution, move):
                continue
                
            new_cube = self._apply_move(cube, move)
            move_h = SearchOptimizations.advanced_heuristic(new_cube, self.corner_db, self.edge_db)
            move_values.append((move_h, move))
        
        # Sort by heuristic value (most promising first)
        move_values.sort()
        
        for _, move in move_values:
            new_cube = self._apply_move(cube, move)
            solution.append(move)
            
            result = self._search(new_cube, g + 1, threshold, solution, visited)
            if result == True:
                return True
                
            if result < minimum:
                minimum = result
                
            solution.pop()
            
        return minimum
