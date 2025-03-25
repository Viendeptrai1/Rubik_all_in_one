from ..base import SolverAlgorithm
import time
import copy
import threading
import functools
from cache_manager import CacheManager
from algorithms.search.optimizations import SearchOptimizations

class KociembaAlgorithm(SolverAlgorithm):
    """
    Implementation of Herbert Kociemba's Two-Phase Algorithm for Rubik's Cube.
    
    Phase 1: Orient edges and corners, place M-slice edges in M-slice
    Phase 2: Solve the cube while maintaining the Phase 1 goals
    """
    
    # Pattern database cache shared between instances
    _pattern_database_initialized = False
    _corner_orientation_table = {}
    _edge_orientation_table = {}
    _ud_slice_table = {}
    _prune_table = {}
    
    def __init__(self, cube, max_depth_phase1=12, max_depth_phase2=10):
        super().__init__(cube)
        # Reduced max depths for faster solutions
        self.max_depth_phase1 = max_depth_phase1
        self.max_depth_phase2 = max_depth_phase2
        # Initialize database first thing
        self._ensure_patterns_initialized()
    
    @property
    def complexity(self):
        return "O(n)"  # Near constant time with pattern databases
    
    @property
    def description(self):
        return """Kociemba's Two-Phase Algorithm:
        Phase 1: Orient all cubies correctly and place M-slice edges.
        Phase 2: Solve the remaining cube while preserving Phase 1 properties.
        Uses pattern databases for efficient searching."""
        
    def _ensure_patterns_initialized(self):
        """Ensure pattern databases are initialized"""
        if not KociembaAlgorithm._pattern_database_initialized:
            self._generate_pattern_databases()
    
    def solve(self, progress_callback=None):
        # Lưu callback để cập nhật tiến trình
        if progress_callback:
            self.set_progress_callback(progress_callback)
            
        start_time = time.time()
        
        if self.signals:
            self.signals.status.emit("Starting Kociemba algorithm search...")
            
        # First try with reduced depths for quick solutions
        if self.signals:
            self.signals.status.emit("Trying fast search with reduced depth...")
        quick_max_depth_phase1 = min(8, self.max_depth_phase1)
        quick_max_depth_phase2 = min(6, self.max_depth_phase2)
        
        temp_max_depth1 = self.max_depth_phase1
        temp_max_depth2 = self.max_depth_phase2
        self.max_depth_phase1 = quick_max_depth_phase1
        self.max_depth_phase2 = quick_max_depth_phase2
        
        # Try fast solution
        solution = None
        if self.parallel_solver:
            solution = self._parallel_solve(start_time)
        else:
            # Phase 1 with optimizations
            phase1_solution = self._solve_phase1(self.cube)
            if phase1_solution:
                # Apply Phase 1 solution
                phase1_cube = self._apply_sequence(self.cube, phase1_solution)
                
                # Phase 2 with optimizations
                phase2_solution = self._solve_phase2(phase1_cube)
                if phase2_solution:
                    solution = phase1_solution + phase2_solution
        
        # If quick search failed, try full search
        if not solution:
            if self.signals:
                self.signals.status.emit("Fast search failed, trying full depth search...")
            self.max_depth_phase1 = temp_max_depth1
            self.max_depth_phase2 = temp_max_depth2
            
            if self.parallel_solver:
                solution = self._parallel_solve(start_time)
            else:
                # Similar to above but with full depth
                phase1_solution = self._solve_phase1(self.cube)
                if phase1_solution:
                    phase1_cube = self._apply_sequence(self.cube, phase1_solution)
                    
                    phase2_solution = self._solve_phase2(phase1_cube)
                    if phase2_solution:
                        solution = phase1_solution + phase2_solution
        
        # Clean up cache to free memory
        CacheManager.clear_memory_cache()
        
        self.time_taken = time.time() - start_time
        self.solution = solution if solution else []
        return self.solution
    
    def _parallel_solve(self, start_time):
        """Solve using parallel processing"""
        # Similar to sequential but with parallel IDA* searches
        solution_found = threading.Event()
        phase1_solution = []
        phase2_solution = []
        
        # Phase 1 parallel solver
        def ida_phase1_task(cube, depth, prune_value):
            if solution_found.is_set():
                return None
                
            result = self._ida_search_phase1(cube, [], depth, prune_value)
            if result:
                return ("phase1", result)
            return None
        
        # Phase 2 parallel solver
        def ida_phase2_task(cube, depth, prune_value):
            if solution_found.is_set():
                return None
                
            result = self._ida_search_phase2(cube, [], depth, prune_value)
            if result:
                solution_found.set()
                return ("phase2", result)
            return None
        
        # Run Phase 1
        max_depth = self.max_depth_phase1
        prune_threshold = self._get_phase1_prune_value(self.cube)
        
        for depth in range(1, max_depth + 1):
            tasks_submitted = 0
            prune_value = min(depth, prune_threshold)
            
            # Distribute start moves across workers
            for move in self._get_phase1_moves():
                new_cube = self._apply_move(self.cube, move)
                self.parallel_solver.submit(ida_phase1_task, new_cube, depth - 1, prune_value)
                tasks_submitted += 1
            
            # Process results
            for _ in range(tasks_submitted):
                result = self.parallel_solver.get_result(timeout=0.1)
                if result and result[0] == "phase1":
                    phase1_solution = result[1]
                    break
            
            if phase1_solution:
                break
        
        if not phase1_solution:
            self.time_taken = time.time() - start_time
            return []
        
        # Apply Phase 1 solution
        phase1_cube = copy.deepcopy(self.cube)
        for move in phase1_solution:
            phase1_cube = self._apply_move(phase1_cube, move)
        
        # Run Phase 2
        max_depth = self.max_depth_phase2
        prune_threshold = self._get_phase2_prune_value(phase1_cube)
        
        for depth in range(1, max_depth + 1):
            tasks_submitted = 0
            prune_value = min(depth, prune_threshold)
            
            # Distribute start moves across workers
            for move in self._get_phase2_moves():
                new_cube = self._apply_move(phase1_cube, move)
                self.parallel_solver.submit(ida_phase2_task, new_cube, depth - 1, prune_value)
                tasks_submitted += 1
            
            # Process results
            for _ in range(tasks_submitted):
                result = self.parallel_solver.get_result(timeout=0.1)
                if result and result[0] == "phase2":
                    phase2_solution = result[1]
                    break
            
            if phase2_solution:
                break
        
        if not phase2_solution:
            self.time_taken = time.time() - start_time
            return []
        
        # Combine solutions
        self.time_taken = time.time() - start_time
        self.solution = phase1_solution + phase2_solution
        return self.solution
    
    def _generate_pattern_databases(self):
        """Generate the pattern databases for pruning"""
        if KociembaAlgorithm._pattern_database_initialized:
            return
            
        if self.signals:
            self.signals.status.emit("Initializing pattern databases for Kociemba algorithm...")
        
        # Load from cache if available
        db_name = CacheManager.compute_db_hash(self.cube)
        db = CacheManager.load_db(f"kociemba_{db_name}")
        
        if db:
            # Use cached database
            KociembaAlgorithm._corner_orientation_table = db.get('corner_orientation', {})
            KociembaAlgorithm._edge_orientation_table = db.get('edge_orientation', {})
            KociembaAlgorithm._ud_slice_table = db.get('ud_slice', {})
            KociembaAlgorithm._prune_table = db.get('prune', {})
        else:
            # Initialize new databases
            self._init_corner_orientation_table()
            self._init_edge_orientation_table()
            self._init_ud_slice_table()
            self._init_prune_table()
            
            # Save to cache
            db = {
                'corner_orientation': KociembaAlgorithm._corner_orientation_table,
                'edge_orientation': KociembaAlgorithm._edge_orientation_table,
                'ud_slice': KociembaAlgorithm._ud_slice_table,
                'prune': KociembaAlgorithm._prune_table
            }
            CacheManager.save_db(db, f"kociemba_{db_name}")
            
        KociembaAlgorithm._pattern_database_initialized = True
    
    def _init_corner_orientation_table(self):
        """Initialize corner orientation pattern database"""
        solved_cube = self._get_solved_cube()
        
        # Add more patterns for better pruning (simplified for the example)
        state_key = SearchOptimizations.optimized_state_key(solved_cube)
        KociembaAlgorithm._corner_orientation_table[state_key] = 0
        
        # Perform 1-move patterns
        for move in self._get_possible_moves():
            new_cube = self._apply_move(solved_cube, move)
            state_key = SearchOptimizations.optimized_state_key(new_cube)
            KociembaAlgorithm._corner_orientation_table[state_key] = 1
    
    def _init_edge_orientation_table(self):
        """Initialize edge orientation pattern database"""
        solved_cube = self._get_solved_cube()
        
        # Add more patterns for better pruning (simplified for the example)
        state_key = SearchOptimizations.optimized_state_key(solved_cube)
        KociembaAlgorithm._edge_orientation_table[state_key] = 0
        
        # Perform 1-move patterns
        for move in self._get_possible_moves():
            new_cube = self._apply_move(solved_cube, move)
            state_key = SearchOptimizations.optimized_state_key(new_cube)
            KociembaAlgorithm._edge_orientation_table[state_key] = 1
    
    def _init_ud_slice_table(self):
        """Initialize UD slice pattern database"""
        solved_cube = self._get_solved_cube()
        
        # Add more patterns for better pruning (simplified for the example)
        state_key = SearchOptimizations.optimized_state_key(solved_cube)
        KociembaAlgorithm._ud_slice_table[state_key] = 0
        
        # Perform 1-move patterns
        for move in self._get_possible_moves():
            new_cube = self._apply_move(solved_cube, move)
            state_key = SearchOptimizations.optimized_state_key(new_cube)
            KociembaAlgorithm._ud_slice_table[state_key] = 1
            
    def _init_prune_table(self):
        """Initialize combined pruning table"""
        solved_cube = self._get_solved_cube()
        
        # Initialize with solved state
        state_key = SearchOptimizations.optimized_state_key(solved_cube)
        KociembaAlgorithm._prune_table[state_key] = 0
        
        # Perform BFS to populate table (simplified)
        queue = [(solved_cube, 0)]
        visited = {state_key}
        
        # Limit BFS depth for reasonable initialization time
        max_depth = 5
        
        while queue and queue[0][1] < max_depth:
            cube, depth = queue.pop(0)
            
            for move in self._get_possible_moves():
                new_cube = self._apply_move(cube, move)
                new_key = SearchOptimizations.optimized_state_key(new_cube)
                
                if new_key not in visited:
                    visited.add(new_key)
                    KociembaAlgorithm._prune_table[new_key] = depth + 1
                    queue.append((new_cube, depth + 1))
    
    def _get_corner_orientation(self, cube):
        """Get the corner orientation state as a hashable value"""
        # Extract orientation information for corners
        orientations = []
        corner_pieces = [p for p in cube.pieces if len(p.colors) == 3]
        
        # Sort by position for consistent results
        corner_pieces.sort(key=lambda p: tuple(p.position))
        
        for piece in corner_pieces:
            # Find which face has the U/D color
            ud_face = None
            for face, color in piece.colors.items():
                if color in [cube.COLORS['W'], cube.COLORS['Y']]:
                    ud_face = face
            orientations.append(ud_face)
        
        # Return a hashable representation
        return tuple(orientations)
    
    def _get_edge_orientation(self, cube):
        """Get the edge orientation state as a hashable value"""
        orientations = []
        edge_pieces = [p for p in cube.pieces if len(p.colors) == 2]
        
        # Sort by position for consistent results
        edge_pieces.sort(key=lambda p: tuple(p.position))
        
        for piece in edge_pieces:
            # Check if the U/D color is on U/D face
            has_ud = False
            for face, color in piece.colors.items():
                if color in [cube.COLORS['W'], cube.COLORS['Y']]:
                    if face in ['U', 'D']:
                        has_ud = True
            orientations.append(1 if has_ud else 0)
        
        return tuple(orientations)
    
    def _get_ud_slice(self, cube):
        """Get the UD slice state as a hashable value"""
        # Check which edges are in the M-slice
        m_slice = []
        edge_pieces = [p for p in cube.pieces if len(p.colors) == 2]
        
        for piece in edge_pieces:
            # Check if it's an M-slice edge (belongs to F-B slice)
            faces = list(piece.colors.keys())
            pos = tuple(piece.position)
            if ('F' in faces and 'B' in faces) or ('L' in faces and 'R' in faces):
                m_slice.append(pos)
        
        return tuple(sorted(m_slice))
    
    def _get_phase1_prune_value(self, cube):
        """Get enhanced pruning value for Phase 1 using pattern databases"""
        # Optimized pattern DB lookup with combined features
        state_key = SearchOptimizations.optimized_state_key(cube)
        
        # Check if we have a direct pruning value
        if state_key in KociembaAlgorithm._prune_table:
            return KociembaAlgorithm._prune_table[state_key]
        
        # Otherwise compute from individual databases
        corner_orient = self._get_corner_orientation(cube)
        edge_orient = self._get_edge_orientation(cube)
        ud_slice = self._get_ud_slice(cube)
        
        # Count misoriented corners
        corner_count = sum(1 for face in corner_orient if face not in ['U', 'D'])
        
        # Count misoriented edges
        edge_count = sum(1 for o in edge_orient if o == 0)
        
        # Count M-slice edges not in M-slice
        slice_count = 0
        solved_slice = self._get_ud_slice(self._get_solved_cube())
        for piece in solved_slice:
            if piece not in ud_slice:
                slice_count += 1
        
        # Combine for better estimate - divide to ensure admissible heuristic
        return max(corner_count // 3, edge_count // 2, slice_count // 2)
    
    def _solve_phase1(self, cube):
        """Solve Phase 1 using IDA* search"""
        max_depth = self.max_depth_phase1
        
        for depth in range(1, max_depth + 1):
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
            
            path = self._ida_search_phase1(cube, [], depth, depth)
            if path:
                return path
        
        return []
    
    def _solve_phase2(self, cube):
        """Solve Phase 2 using IDA* search"""
        max_depth = self.max_depth_phase2
        
        for depth in range(1, max_depth + 1):
            if self.update_state_count():
                if self.states_explored >= self.max_states:
                    return []
            
            path = self._ida_search_phase2(cube, [], depth, depth)
            if path:
                return path
        
        return []
    
    def _ida_search_phase1(self, cube, path, depth, prune_value):
        """IDA* search for Phase 1"""
        if depth == 0:
            # Check if we've reached Phase 1 goal
            if self._is_phase1_solved(cube):
                return path
            return None
        
        # Pruning check
        if prune_value > depth:
            return None
        
        # Try each move
        for move in self._get_phase1_moves():
            # Skip redundant moves
            if path and self._is_move_redundant(path[-1], move):
                continue
            
            new_cube = self._apply_move(cube, move)
            new_path = path + [move]
            
            # Get pruning value for new state
            new_prune = self._get_phase1_prune_value(new_cube)
            if new_prune <= depth - 1:
                result = self._ida_search_phase1(new_cube, new_path, depth - 1, new_prune)
                if result:
                    return result
        
        return None
    
    def _ida_search_phase2(self, cube, path, depth, prune_value):
        """IDA* search for Phase 2"""
        if depth == 0:
            # Check if cube is solved
            if self._is_solved(cube):
                return path
            return None
        
        # Pruning check
        if prune_value > depth:
            return None
        
        # Try each move
        for move in self._get_phase2_moves():
            # Skip redundant moves
            if path and self._is_move_redundant(path[-1], move):
                continue
            
            new_cube = self._apply_move(cube, move)
            
            # Ensure we haven't broken Phase 1 properties
            if not self._is_phase1_solved(new_cube):
                continue
            
            new_path = path + [move]
            
            # Get pruning value for new state
            new_prune = self._get_phase2_prune_value(new_cube)
            if new_prune <= depth - 1:
                result = self._ida_search_phase2(new_cube, new_path, depth - 1, new_prune)
                if result:
                    return result
        
        return None
    
    def _is_phase1_solved(self, cube):
        """Check if cube satisfies Phase 1 criteria"""
        # All corners are oriented correctly
        corner_orient = self._get_corner_orientation(cube)
        
        # All edges are oriented correctly
        edge_orient = self._get_edge_orientation(cube)
        
        # M-slice edges are in M-slice
        ud_slice = self._get_ud_slice(cube)
        solved_ud_slice = self._get_ud_slice(self._get_solved_cube())
        
        # Check conditions - simplified for this implementation
        corners_ok = all(face in ['U', 'D'] for face in corner_orient)
        edges_ok = all(o == 1 for o in edge_orient)
        slice_ok = set(ud_slice) == set(solved_ud_slice)
        
        return corners_ok and edges_ok and slice_ok
    
    def _get_phase1_moves(self):
        """Get all possible moves for Phase 1"""
        return self._get_possible_moves()  # All moves are allowed in Phase 1
    
    def _get_phase2_moves(self):
        """Get restricted moves for Phase 2 to preserve Phase 1 properties"""
        # In Phase 2, we avoid quarter turns of F, B, L, R faces
        # to preserve edge orientation
        return ['U', "U'", 'D', "D'", 'F2', 'B2', 'L2', 'R2']
    
    def _is_move_redundant(self, prev_move, move):
        """Check if a move is redundant (e.g., U followed by U')"""
        # Same face
        if prev_move[0] == move[0]:
            return True
        
        # Opposite faces, no point doing both sequentially (optimization)
        opposite_pairs = [('U', 'D'), ('L', 'R'), ('F', 'B')]
        for a, b in opposite_pairs:
            if prev_move[0] == a and move[0] == b:
                return True
            if prev_move[0] == b and move[0] == a:
                return True
        
        return False
    
    def _get_phase2_prune_value(self, cube):
        """Get pruning value for Phase 2"""
        # For simplicity, use the standard heuristic
        return self._heuristic(cube) * 10
    
    def _apply_sequence(self, cube, sequence):
        """Apply a sequence of moves more efficiently"""
        current = cube
        
        # Try to find in cache first
        state_key = SearchOptimizations.optimized_state_key(cube)
        sequence_key = (state_key, tuple(sequence))
        
        with SolverAlgorithm._cache_lock:
            if sequence_key in SolverAlgorithm._move_results_cache:
                return SolverAlgorithm._move_results_cache[sequence_key]
        
        # If not in cache, compute and cache result
        current_cube = copy.deepcopy(cube)
        for move in sequence:
            current_cube = self._apply_move(current_cube, move)
        
        # Cache result if it's a reasonable length sequence
        if len(sequence) <= 10:
            with SolverAlgorithm._cache_lock:
                if len(SolverAlgorithm._move_results_cache) < 50000:  # Limit cache size
                    SolverAlgorithm._move_results_cache[sequence_key] = current_cube
        
        return current_cube
