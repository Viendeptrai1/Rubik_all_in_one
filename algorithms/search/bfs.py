from ..base import SolverAlgorithm
from collections import deque
import time
import copy
import numpy as np
import threading

class BFS(SolverAlgorithm):
    @property
    def complexity(self):
        return "O(b^d)"
    
    @property
    def description(self):
        return """Breadth-First Search explores all moves at the current depth
        before moving to next depth level. Guarantees optimal solution but
        uses large amount of memory."""
    
    def solve(self):
        start_time = time.time()
        queue = deque([(self.cube, [])])
        visited = set()
        
        # Use our parallel solver if available
        if self.parallel_solver:
            return self._parallel_solve(start_time)
        
        while queue:
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []  # Quá nhiều states
                    
            current_cube, moves = queue.popleft()
            
            if self._is_solved(current_cube):
                self.time_taken = time.time() - start_time
                self.solution = moves
                return moves
                
            for move in self._get_possible_moves():
                new_cube = self._apply_move(current_cube, move)
                state = self._cube_state(new_cube)
                if state not in visited:
                    visited.add(state)
                    queue.append((new_cube, moves + [move]))
        
        return []
    
    def _parallel_solve(self, start_time):
        """BFS implementation using parallel solver"""
        queue = deque([(self.cube, [])])
        visited = set([self._cube_state(self.cube)])
        batch_size = 50
        
        # Lock for thread safety
        visited_lock = threading.Lock()
        solution_found = threading.Event()
        solution = []
        
        def process_node(cube, moves):
            """Process a single node in parallel"""
            if solution_found.is_set():
                return None
                
            if self._is_solved(cube):
                solution_found.set()
                return ("solution", moves)
                
            results = []
            new_states = set()
            
            for move in self._get_possible_moves():
                new_cube = self._apply_move(cube, move)
                new_state = self._cube_state(new_cube)
                
                # Store state for later checking against visited
                new_states.add(new_state)
                results.append((new_cube, moves + [move], new_state))
                
            return ("nodes", results, new_states)
        
        while queue and not solution_found.is_set():
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
                    
            # Get batch of nodes to process
            batch = []
            for _ in range(min(batch_size, len(queue))):
                if queue:
                    batch.append(queue.popleft())
                    
            if not batch:
                break
                
            # Submit batch for processing
            for cube, moves in batch:
                self.parallel_solver.submit(process_node, cube, moves)
                
            # Process results until all submitted tasks are done
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
                    nodes, new_states = result[1], result[2]
                    
                    with visited_lock:
                        for cube, moves, state in nodes:
                            if state not in visited:
                                visited.add(state)
                                queue.append((cube, moves))
        
        return []
    
    def parallelize(self, executor, should_cancel):
        """Use threading instead of multiprocessing to avoid pickling issues"""
        # For now, revert to single-threaded implementation as it's safer
        self.should_cancel = should_cancel
        start_time = time.time()
        solution = self.solve()
        self.time_taken = time.time() - start_time
        return solution
    
    def _process_move(self, cube, move, moves, visited):
        """Helper function to process a single move in parallel"""
        new_cube = self._apply_move(cube, move)
        new_moves = moves + [move]
        new_state = self._cube_state(new_cube)
        
        is_solved = self._is_solved(new_cube)
        
        if new_state not in visited:
            return (new_cube, new_moves, new_state, is_solved)
        
        return None
