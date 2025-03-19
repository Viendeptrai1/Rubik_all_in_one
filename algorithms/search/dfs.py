from ..base import SolverAlgorithm
import time

class DFS(SolverAlgorithm):
    @property
    def complexity(self):
        return "O(b^m)"
    
    @property
    def description(self):
        return """Depth-First Search explores as far as possible along each branch
        before backtracking. Uses less memory than BFS but may not find
        optimal solution."""
    
    def solve(self, max_depth=20):
        start_time = time.time()
        self.visited = set()
        solution = self._dfs(self.cube, [], 0, max_depth)
        self.time_taken = time.time() - start_time
        return solution
    
    def _dfs(self, cube, moves, depth, max_depth):
        if self.update_state_count():
            if self.states_explored >= self.max_states:
                return None
                
        if depth > max_depth:
            return None
            
        if self._is_solved(cube):
            self.solution = moves
            return moves
            
        for move in self._get_possible_moves():
            new_cube = self._apply_move(cube, move)
            state = self._cube_state(new_cube)
            
            if state not in self.visited:
                self.visited.add(state)
                result = self._dfs(new_cube, moves + [move], depth + 1, max_depth)
                if result:
                    return result
                    
        return None
