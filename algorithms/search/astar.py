from ..base import SolverAlgorithm
import heapq
import time
import threading
import copy
import numpy as np
from .optimizations import SearchOptimizations

class AStar(SolverAlgorithm):
    def __init__(self, cube):
        super().__init__(cube)
        # Initialize pattern databases
        self.corner_db = {}
        self.edge_db = {}
        self._initialize_pattern_dbs()
        
    @property
    def complexity(self):
        return "O(b^d)"
        
    @property
    def description(self):
        return """A* search algorithm uses heuristic function to find the most
        promising path. Guarantees optimal solution if heuristic is admissible."""
    
    def _initialize_pattern_dbs(self):
        """Initialize pattern databases for better heuristics"""
        if self.signals:
            self.signals.status.emit("Initializing pattern databases...")
        
        solved_cube = self._get_solved_cube()
        self.corner_db = SearchOptimizations.compute_corner_distance_db(solved_cube)
        self.edge_db = SearchOptimizations.compute_edge_distance_db(solved_cube)
        
    def solve(self):
        start_time = time.time()
        
        # Use an optimized priority queue implementation
        queue = [(self._heuristic(self.cube), 0, 0, self.cube, [])]  # (f, g, tiebreaker, cube, moves)
        visited = set()
        counter = 0  # Tiebreaker for equal f-scores
        
        # Optimization: Use a fast hash function for states
        def get_state_key(cube):
            return SearchOptimizations.optimized_state_key(cube)
        
        visited.add(get_state_key(self.cube))
        
        while queue:
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
            
            # Pop most promising node
            _, cost, _, current_cube, moves = heapq.heappop(queue)
            
            # Goal test
            if self._is_solved(current_cube):
                self.time_taken = time.time() - start_time
                # Optimize the final move sequence
                self.solution = SearchOptimizations.optimize_move_sequence(moves)
                return self.solution
            
            # Expand node - try each possible move
            for move in self._get_possible_moves():
                # Skip redundant moves - optimization
                if SearchOptimizations.is_move_redundant(moves, move):
                    continue
                    
                new_cube = self._apply_move(current_cube, move)
                new_state = get_state_key(new_cube)
                
                if new_state not in visited:
                    visited.add(new_state)
                    new_cost = cost + 1
                    # Use enhanced heuristic function
                    h = SearchOptimizations.advanced_heuristic(new_cube, self.corner_db, self.edge_db)
                    f = new_cost + h
                    counter += 1  # Ensure unique ordering for equal f-scores
                    new_moves = moves + [move]
                    heapq.heappush(queue, (f, new_cost, counter, new_cube, new_moves))
        
        return []
        
    def _parallel_solve(self, start_time):
        """A* implementation using parallel solver"""
        queue = [(self._heuristic(self.cube), 0, self.cube, [])]
        visited = set([self._cube_state(self.cube)])
        batch_size = 30
        
        # Lock for thread safety
        queue_lock = threading.Lock()
        visited_lock = threading.Lock()
        solution_found = threading.Event()
        solution = []
        
        def process_node(f_score, cost, cube, moves):
            """Process a single node in parallel"""
            if solution_found.is_set():
                return None
                
            if self._is_solved(cube):
                solution_found.set()
                return ("solution", moves)
                
            results = []
            
            for move in self._get_possible_moves():
                new_cube = self._apply_move(cube, move)
                new_state = self._cube_state(new_cube)
                
                with visited_lock:
                    if new_state in visited:
                        continue
                    visited.add(new_state)
                
                new_cost = cost + 1
                h = self._heuristic(new_cube)
                f = new_cost + h
                new_moves = moves + [move]
                
                results.append((f, new_cost, new_cube, new_moves))
                
            return ("nodes", results)
        
        while queue and not solution_found.is_set():
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
                    
            # Get batch of nodes to process
            batch = []
            for _ in range(min(batch_size, len(queue))):
                if queue:
                    batch.append(heapq.heappop(queue))
                    
            if not batch:
                break
                
            # Submit batch for processing
            for f, cost, cube, moves in batch:
                self.parallel_solver.submit(process_node, f, cost, cube, moves)
                
            # Process results
            results_processed = 0
            while results_processed < len(batch):
                result = self.parallel_solver.get_result(timeout=0.1)
                if result is None:
                    if solution_found.is_set():
                        break
                    continue
                    
                results_processed += 1
                
                if result[0] == "solution":
                    self.time_taken = time.time() - start_time
                    self.solution = result[1]
                    return result[1]
                    
                elif result[0] == "nodes":
                    with queue_lock:
                        for node in result[1]:
                            heapq.heappush(queue, node)
        
        return []
        
    def _heuristic(self, cube):
        """Enhanced heuristic function combining multiple pattern databases"""
        return SearchOptimizations.advanced_heuristic(cube, self.corner_db, self.edge_db)
    
    def parallelize(self, executor, should_cancel):
        """Revert to single-threaded implementation due to pickling issues"""
        self.should_cancel = should_cancel
        start_time = time.time()
        solution = self.solve()
        self.time_taken = time.time() - start_time
        return solution
    
    def _eval_move(self, cube, cost, move, moves):
        """Evaluate a single move for A* in parallel"""
        new_cube = self._apply_move(cube, move)
        state = self._cube_state(new_cube)
        is_solved = self._is_solved(new_cube)
        
        new_cost = cost + 1
        h = self._heuristic(new_cube)
        f = new_cost + h
        new_moves = moves + [move]
        
        return (f, new_cost, new_cube, new_moves, state, is_solved)
