from ..base import SolverAlgorithm
from collections import deque
import time
import heapq
from .optimizations import SearchOptimizations

class BidirectionalSearch(SolverAlgorithm):
    @property
    def complexity(self):
        return "O(b^(d/2))"

    @property
    def description(self):
        return """Bidirectional Search explores from both initial state and goal state,
        meeting in the middle to find solution faster than unidirectional search."""

    def solve(self):
        start_time = time.time()
        
        # Use priority queues instead of regular queues to prioritize promising states
        start_queue = [(0, 0, self.cube, [])]  # (h, tiebreaker, cube, moves)
        goal_queue = [(0, 0, self._get_solved_cube(), [])]
        
        start_counter = 0  # For tiebreaking
        goal_counter = 0
        
        # Use optimized state representation
        start_visited = {SearchOptimizations.optimized_state_key(self.cube): []}
        goal_visited = {SearchOptimizations.optimized_state_key(self._get_solved_cube()): []}
        
        # Use a hash table for fast lookups of inversion moves
        invert_move = {
            'F': 'F\'', 'F\'': 'F', 'F2': 'F2',
            'B': 'B\'', 'B\'': 'B', 'B2': 'B2',
            'L': 'L\'', 'L\'': 'L', 'L2': 'L2',
            'R': 'R\'', 'R\'': 'R', 'R2': 'R2',
            'U': 'U\'', 'U\'': 'U', 'U2': 'U2',
            'D': 'D\'', 'D\'': 'D', 'D2': 'D2'
        }

        while start_queue and goal_queue:
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
                    
            # Expand from start (frontier with lowest heuristic first)
            _, _, current, moves = heapq.heappop(start_queue)
            current_state = SearchOptimizations.optimized_state_key(current)
            
            if current_state in goal_visited:
                self.time_taken = time.time() - start_time
                # Get solution by joining paths
                forward_path = moves
                backward_path = goal_visited[current_state]
                
                # Need to invert and reverse the backward path
                backward_path = [invert_move[move] for move in reversed(backward_path)]
                
                combined_solution = forward_path + backward_path
                # Optimize solution
                self.solution = SearchOptimizations.optimize_move_sequence(combined_solution)
                return self.solution

            # Expand forward from start state
            for move in self._get_possible_moves():
                # Skip redundant moves
                if moves and SearchOptimizations.is_move_redundant(moves, move):
                    continue
                    
                new_cube = self._apply_move(current, move)
                new_state = SearchOptimizations.optimized_state_key(new_cube)
                
                if new_state not in start_visited:
                    new_moves = moves + [move]
                    start_visited[new_state] = new_moves
                    
                    # Calculate heuristic for prioritization
                    h = self._heuristic(new_cube) * 2  # Encourage meeting in the middle
                    start_counter += 1
                    heapq.heappush(start_queue, (h, start_counter, new_cube, new_moves))

            # Expand from goal (frontier with lowest heuristic first)
            _, _, current, moves = heapq.heappop(goal_queue)
            current_state = SearchOptimizations.optimized_state_key(current)
            
            if current_state in start_visited:
                self.time_taken = time.time() - start_time
                
                # Get solution by joining paths
                forward_path = start_visited[current_state]
                backward_path = moves
                
                # Need to invert and reverse the backward path
                backward_path = [invert_move[move] for move in reversed(backward_path)]
                
                combined_solution = forward_path + backward_path
                # Optimize solution
                self.solution = SearchOptimizations.optimize_move_sequence(combined_solution)
                return self.solution

            # Expand backward from goal state
            for move in self._get_possible_moves():
                # Skip redundant moves
                if moves and SearchOptimizations.is_move_redundant(moves, move):
                    continue
                    
                new_cube = self._apply_move(current, move)
                new_state = SearchOptimizations.optimized_state_key(new_cube)
                
                if new_state not in goal_visited:
                    new_moves = moves + [move]
                    goal_visited[new_state] = new_moves
                    
                    # Calculate heuristic for prioritization
                    h = self._heuristic(new_cube) * 2  # Encourage meeting in the middle
                    goal_counter += 1
                    heapq.heappush(goal_queue, (h, goal_counter, new_cube, new_moves))

        return []
    
    def _invert_move_sequence(self, moves):
        """Invert a sequence of moves (reverse order and invert each move)"""
        invert_move = {
            'F': 'F\'', 'F\'': 'F', 'F2': 'F2',
            'B': 'B\'', 'B\'': 'B', 'B2': 'B2',
            'L': 'L\'', 'L\'': 'L', 'L2': 'L2',
            'R': 'R\'', 'R\'': 'R', 'R2': 'R2',
            'U': 'U\'', 'U\'': 'U', 'U2': 'U2',
            'D': 'D\'', 'D\'': 'D', 'D2': 'D2'
        }
        
        return [invert_move[move] for move in reversed(moves)]
