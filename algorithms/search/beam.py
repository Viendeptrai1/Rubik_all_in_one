from ..base import SolverAlgorithm
import heapq
import time

class BeamSearch(SolverAlgorithm):
    def __init__(self, cube, beam_width=100):
        super().__init__(cube)
        self.beam_width = beam_width

    @property
    def complexity(self):
        return f"O(b*w), w={self.beam_width}"

    @property
    def description(self):
        return """Beam Search is like BFS but only keeps the best w states at each level.
        Not guaranteed to find optimal solution but uses less memory."""

    def solve(self):
        start_time = time.time()
        beam = [(self._heuristic(self.cube), self.cube, [])]
        
        while beam:
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
                    
            new_beam = []
            for _, current_cube, moves in beam:
                if self._is_solved(current_cube):
                    self.time_taken = time.time() - start_time
                    self.solution = moves
                    return moves

                for move in self._get_possible_moves():
                    new_cube = self._apply_move(current_cube, move)
                    h = self._heuristic(new_cube)
                    new_beam.append((h, new_cube, moves + [move]))

            beam = heapq.nsmallest(self.beam_width, new_beam)
            if not beam:
                break

        return []
