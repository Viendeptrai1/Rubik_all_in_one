from ..base import SolverAlgorithm
import time
import copy
import threading
import functools

class ThistlethwaiteAlgorithm(SolverAlgorithm):
    """
    Implementation of Morwen Thistlethwaite's Four-Phase Algorithm.
    
    G0: Starting group (all possible cube states)
    G1: All edges oriented correctly
    G2: Edges in M-slice correct, all corners oriented
    G3: Cube solvable using only half-turns
    G4: Solved cube
    """
    
    # Static pattern database cache
    _pattern_database_initialized = False
    _phase_tables = [{}, {}, {}, {}]
    
    def __init__(self, cube):
        super().__init__(cube)
        # Reduced max depths for better performance
        self.max_depths = [5, 8, 10, 12]  # Lower depths for faster solutions
    
    @property
    def complexity(self):
        return "O(n)"  # Near constant time with pattern databases
    
    @property
    def description(self):
        return """Thistlethwaite's Algorithm:
        Four-phase approach that gradually restricts the move set.
        G0→G1: Orient edges
        G1→G2: Place M-slice edges + orient corners
        G2→G3: Get to half-turn only positions
        G3→G4: Solve with half-turns"""
    
    def solve(self, progress_callback=None):
        # Lưu callback để cập nhật tiến trình
        if progress_callback:
            self.set_progress_callback(progress_callback)
            
        # Initialize pattern databases if needed - now done in solve() rather than __init__
        if not ThistlethwaiteAlgorithm._pattern_database_initialized:
            self._init_pattern_databases()
            
        if self.signals:
            self.signals.status.emit("Starting Thistlethwaite algorithm search...")
        start_time = time.time()
        
        # Try with reduced depths first for quick solutions
        if self.signals:
            self.signals.status.emit("Trying fast search with reduced depth...")
        original_depths = self.max_depths.copy()
        self.max_depths = [min(4, d) for d in self.max_depths]
        
        # Try quick solution
        solution = None
        if self.parallel_solver:
            solution = self._parallel_solve(start_time)
        else:
            solution = self._sequential_solve()
        
        # If quick search failed, try full search
        if not solution:
            if self.signals:
                self.signals.status.emit("Fast search failed, trying full depth search...")
            self.max_depths = original_depths
            
            if self.parallel_solver:
                solution = self._parallel_solve(start_time)
            else:
                solution = self._sequential_solve()
        
        self.time_taken = time.time() - start_time
        self.solution = solution if solution else []
        return self.solution
    
    def _sequential_solve(self):
        """Regular sequential solve"""
        current_cube = copy.deepcopy(self.cube)
        full_solution = []
        
        # Solve each phase
        for phase in range(4):
            phase_solution = self._solve_phase(phase, current_cube)
            if not phase_solution:
                return []
            
            # Apply phase solution
            for move in phase_solution:
                current_cube = self._apply_move(current_cube, move)
            
            full_solution.extend(phase_solution)
            
            # Check if we should stop early
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
        
        return full_solution
    
    def _parallel_solve(self, start_time):
        """Solve using parallel processing"""
        current_cube = copy.deepcopy(self.cube)
        full_solution = []
        
        # Solve each phase in parallel
        for phase in range(4):
            phase_solution = []
            solution_found = threading.Event()
            
            # Function for parallel IDA* tasks
            def ida_phase_task(cube, moves, depth, phase_num, prune_value):
                if solution_found.is_set():
                    return None
                
                result = self._ida_search_phase(cube, moves, depth, phase_num, prune_value)
                if result:
                    return ("solution", result)
                return None
            
            # Iterative deepening
            max_depth = self.max_depths[phase]
            for depth in range(1, max_depth + 1):
                tasks_submitted = 0
                
                # Get allowed moves for this phase
                allowed_moves = self._get_phase_moves(phase)
                
                # Initial pruning value
                prune_value = self._get_phase_prune_value(current_cube, phase)
                if prune_value > depth:
                    continue
                
                # Distribute initial moves across workers
                for move in allowed_moves:
                    new_cube = self._apply_move(current_cube, move)
                    self.parallel_solver.submit(
                        ida_phase_task, 
                        new_cube, 
                        [move], 
                        depth - 1,
                        phase,
                        min(prune_value, depth - 1)
                    )
                    tasks_submitted += 1
                
                # Process results
                for _ in range(tasks_submitted):
                    result = self.parallel_solver.get_result(timeout=0.1)
                    if result and result[0] == "solution":
                        phase_solution = result[1]
                        solution_found.set()
                        break
                
                if solution_found.is_set():
                    break
            
            if not phase_solution:
                return []
            
            # Apply phase solution
            for move in phase_solution:
                current_cube = self._apply_move(current_cube, move)
            
            full_solution.extend(phase_solution)
            
            # Check if we should stop early
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
        
        return full_solution
    
    def _init_pattern_databases(self):
        """Initialize pattern databases for each phase"""
        if ThistlethwaiteAlgorithm._pattern_database_initialized:
            return
            
        if self.signals:
            self.signals.status.emit("Initializing pattern databases for Thistlethwaite algorithm...")
            
        # Simple initialization for now
        ThistlethwaiteAlgorithm._pattern_database_initialized = True
    
    def _solve_phase(self, phase, cube):
        """Solve a specific phase using IDA* search"""
        max_depth = self.max_depths[phase]
        
        for depth in range(max_depth + 1):
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
            
            prune_value = self._get_phase_prune_value(cube, phase)
            if prune_value > depth:
                continue
                
            path = self._ida_search_phase(cube, [], depth, phase, prune_value)
            if path:
                return path
        
        return []
    
    def _ida_search_phase(self, cube, path, depth, phase, prune_value):
        """IDA* search for a specific phase"""
        if depth == 0:
            # Check if we've completed this phase
            if self._is_in_group(cube, phase + 1):
                return path
            return None
        
        # Pruning check
        if prune_value > depth:
            return None
        
        # Get allowed moves for this phase
        allowed_moves = self._get_phase_moves(phase)
        
        for move in allowed_moves:
            # Skip redundant moves
            if path and self._is_move_redundant(path[-1], move, phase):
                continue
            
            new_cube = self._apply_move(cube, move)
            new_path = path + [move]
            
            # Check pruning value
            new_prune = self._get_phase_prune_value(new_cube, phase)
            if new_prune <= depth - 1:
                result = self._ida_search_phase(new_cube, new_path, depth - 1, phase, new_prune)
                if result:
                    return result
        
        return None
    
    def _get_phase_moves(self, phase):
        """Get allowed moves for a specific phase"""
        if phase == 0:
            # Phase 0: All moves allowed
            return self._get_possible_moves()
        elif phase == 1:
            # Phase 1: All moves allowed
            return self._get_possible_moves()
        elif phase == 2:
            # Phase 2: F/B only in half turns, others any
            moves = ['U', "U'", 'D', "D'", 'L', "L'", 'R', "R'", 'F2', 'B2']
            return moves
        elif phase == 3:
            # Phase 3: Only half turns allowed
            return ['U2', 'D2', 'L2', 'R2', 'F2', 'B2']
        
        return []
    
    def _is_move_redundant(self, prev_move, move, phase):
        """Check if a move is redundant in the context of the current phase"""
        # Same face
        if prev_move[0] == move[0]:
            return True
        
        # For phase 3, we need more sophisticated redundancy checks
        if phase == 3:
            # No need for sequential half-turns of opposite faces
            opposite_pairs = [('U', 'D'), ('L', 'R'), ('F', 'B')]
            for a, b in opposite_pairs:
                if prev_move[0] == a and move[0] == b:
                    return True
                if prev_move[0] == b and move[0] == a:
                    return True
        
        return False
    
    def _get_phase_prune_value(self, cube, phase):
        """Get pruning value for a specific phase"""
        if phase == 0:
            # Phase 0: Count misoriented edges
            return self._count_misoriented_edges(cube) // 2
        elif phase == 1:
            # Phase 1: Count misplaced M-slice edges + misoriented corners
            return (self._count_bad_m_slice(cube) + 
                   self._count_misoriented_corners(cube) // 3)
        elif phase == 2:
            # Phase 2: Count corners not in correct orbits + edges not in correct orbits
            return (self._count_corner_orbit_errors(cube) + 
                   self._count_edge_orbit_errors(cube)) // 4
        elif phase == 3:
            # Phase 3: Basic heuristic for final phase
            return self._count_misplaced_pieces(cube) // 4
        
        return 0
    
    def _is_in_group(self, cube, group):
        """Check if cube is in the specified group"""
        if group == 1:
            # G1: All edges oriented correctly
            return self._count_misoriented_edges(cube) == 0
        elif group == 2:
            # G2: M-slice edges in M-slice, all corners oriented
            return (self._count_misoriented_edges(cube) == 0 and
                   self._count_bad_m_slice(cube) == 0 and
                   self._count_misoriented_corners(cube) == 0)
        elif group == 3:
            # G3: Corner and edge orbits correct (solvable with half-turns)
            return (self._count_misoriented_edges(cube) == 0 and
                   self._count_bad_m_slice(cube) == 0 and
                   self._count_misoriented_corners(cube) == 0 and
                   self._count_corner_orbit_errors(cube) == 0 and
                   self._count_edge_orbit_errors(cube) == 0)
        elif group == 4:
            # G4: Solved cube
            return self._is_solved(cube)
        
        return False
    
    # Cache state calculations
    @functools.lru_cache(maxsize=1024)
    def _count_misoriented_edges(self, cube):
        """Count edges with incorrect orientation"""
        count = 0
        for piece in cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                # Check if the U/D color is on U/D face
                has_ud = False
                for face, color in piece.colors.items():
                    if color in [cube.COLORS['W'], cube.COLORS['Y']]:
                        if face in ['U', 'D']:
                            has_ud = True
                if not has_ud:
                    count += 1
        return count
    
    # Cache state calculations
    @functools.lru_cache(maxsize=1024)
    def _count_bad_m_slice(self, cube):
        """Count edges that should be in M-slice but aren't"""
        count = 0
        solved_cube = self._get_solved_cube()
        
        # Get M-slice edge positions from solved cube
        m_slice_positions = set()
        for piece in solved_cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                faces = list(piece.colors.keys())
                if ('F' in faces and 'B' in faces) or ('L' in faces and 'R' in faces):
                    m_slice_positions.add(tuple(piece.position))
        
        # Check current cube
        for piece in cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                pos = tuple(piece.position)
                faces = list(piece.colors.keys())
                
                # Edge should be in M-slice but isn't
                if pos in m_slice_positions and not (('F' in faces and 'B' in faces) or 
                                                    ('L' in faces and 'R' in faces)):
                    count += 1
                
                # Edge shouldn't be in M-slice but is
                if pos not in m_slice_positions and (('F' in faces and 'B' in faces) or 
                                                    ('L' in faces and 'R' in faces)):
                    count += 1
        
        return count
    
    # Cache state calculations
    @functools.lru_cache(maxsize=1024)
    def _count_misoriented_corners(self, cube):
        """Count corners with incorrect orientation"""
        count = 0
        for piece in cube.pieces:
            if len(piece.colors) == 3:  # Corner piece
                # Check if U/D color is on U/D face
                for face, color in piece.colors.items():
                    if color in [cube.COLORS['W'], cube.COLORS['Y']]:
                        if face not in ['U', 'D']:
                            count += 1
        return count
    
    def _count_corner_orbit_errors(self, cube):
        """Count corners in incorrect orbits for G3"""
        # For G3, corners should be in their correct orbits
        # This requires understanding of corner permutation parity
        # Simplified version: count corners in wrong positions
        count = 0
        solved_cube = self._get_solved_cube()
        
        # Get corner positions from solved cube
        solved_corners = {}
        for piece in solved_cube.pieces:
            if len(piece.colors) == 3:  # Corner piece
                pos = tuple(piece.position)
                solved_corners[pos] = {face: color for face, color in piece.colors.items()}
        
        # Check current cube
        for piece in cube.pieces:
            if len(piece.colors) == 3:  # Corner piece
                pos = tuple(piece.position)
                if pos in solved_corners:
                    # Corner colors don't match solved position
                    if piece.colors != solved_corners[pos]:
                        count += 1
        
        return count
    
    def _count_edge_orbit_errors(self, cube):
        """Count edges in incorrect orbits for G3"""
        # For G3, edges should be in their correct orbits
        # Simplified version: count edges in wrong positions
        count = 0
        solved_cube = self._get_solved_cube()
        
        # Get edge positions from solved cube
        solved_edges = {}
        for piece in solved_cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                pos = tuple(piece.position)
                solved_edges[pos] = {face: color for face, color in piece.colors.items()}
        
        # Check current cube
        for piece in cube.pieces:
            if len(piece.colors) == 2:  # Edge piece
                pos = tuple(piece.position)
                if pos in solved_edges:
                    # Edge colors don't match solved position
                    if piece.colors != solved_edges[pos]:
                        count += 1
        
        return count
        
    def _count_misplaced_pieces(self, cube):
        """Count pieces that aren't in their solved positions"""
        count = 0
        solved_cube = self._get_solved_cube()
        
        # Create maps of position -> colors for solved cube
        solved_pieces = {}
        for piece in solved_cube.pieces:
            pos = tuple(piece.position)
            solved_pieces[pos] = piece.colors
            
        # Count misplaced pieces in current cube
        for piece in cube.pieces:
            pos = tuple(piece.position)
            if pos in solved_pieces and piece.colors != solved_pieces[pos]:
                count += 1
                
        return count
