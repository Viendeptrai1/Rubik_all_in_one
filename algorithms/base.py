from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Dict, Any, Set, Tuple
from rubik import RubikCube
import copy
import concurrent.futures
import time
import psutil
import threading
from PyQt5.QtCore import QObject, pyqtSignal
from algorithms.search.optimizations import SearchOptimizations

class ProgressMixin:
    def __init__(self):
        self._progress_callback: Optional[Callable[[int, int], bool]] = None
        self._total_steps = 100
        self._current_step = 0

    def set_progress_callback(self, callback: Callable[[int, int], bool]):
        self._progress_callback = callback

    def update_progress(self, current: int, total: int) -> bool:
        """Update progress and check if should cancel"""
        self._current_step = current
        self._total_steps = total
        if self._progress_callback:
            return self._progress_callback(current, total)
        return False

class SolverAlgorithm(ProgressMixin, ABC):
    """Base class for all solving algorithms"""
    
    # Cache các trạng thái đã tính toán để tránh lặp lại
    _is_solved_cache = {}
    _state_cache = {}
    _move_results_cache = {}
    _cache_lock = threading.RLock()
    
    def __init__(self, cube: RubikCube):
        super().__init__()
        self.cube = cube
        self.solution = []
        self.time_taken = 0
        self.states_explored = 0
        self.max_states = 1000000
        self.parallel_solver = None
        self.signals = None
        self.memory_limit = 1000 * 1024 * 1024  # 1GB limit
        self.visited_states = set()  # Sử dụng set để lưu trữ các trạng thái đã visited
        self._init_cache()
    
    def _init_cache(self):
        """Khởi tạo các bộ nhớ đệm"""
        # Giới hạn kích thước cache để tránh tràn RAM
        SolverAlgorithm._is_solved_cache = {}
        SolverAlgorithm._state_cache = {}
        SolverAlgorithm._move_results_cache = {}
    
    def set_parallel_solver(self, solver):
        """Set the parallel solver"""
        self.parallel_solver = solver
        
    def check_memory_usage(self):
        """Kiểm tra mức sử dụng bộ nhớ và giới hạn nếu cần"""
        process = psutil.Process()
        memory_used = process.memory_info().rss
        
        if memory_used > self.memory_limit:
            # Giảm kích thước cache khi bộ nhớ quá cao
            with SolverAlgorithm._cache_lock:
                cache_entries = len(SolverAlgorithm._move_results_cache)
                if cache_entries > 1000:
                    # Chỉ giữ lại 50% cache
                    keys_to_keep = list(SolverAlgorithm._move_results_cache.keys())[:cache_entries//2]
                    SolverAlgorithm._move_results_cache = {k: SolverAlgorithm._move_results_cache[k] 
                                                          for k in keys_to_keep}
            
            if self.signals:
                self.signals.status.emit(f"Reduced cache size. Memory: {memory_used / (1024*1024):.1f} MB")
            
            if memory_used > self.memory_limit * 1.5:
                if self.signals:
                    self.signals.status.emit(f"Memory limit exceeded: {memory_used / (1024*1024):.1f} MB")
                return True
                
        return False
        
    def update_state_count(self):
        """Cập nhật số states đã explore và progress"""
        self.states_explored += 1
        
        # Check memory usage periodically
        if self.states_explored % 10000 == 0 and self.check_memory_usage():
            return True
        
        # Report progress periodically
        if self._progress_callback:
            should_cancel = self._progress_callback(self.states_explored, self.max_states)
            if should_cancel:
                return True
                
            # Emit status updates periodically
            if self.states_explored % 10000 == 0 and self.signals:
                self.signals.status.emit(f"Searching... States explored: {self.states_explored}")
                
            return self.states_explored % 1000 == 0

    def _is_solved(self, cube: RubikCube) -> bool:
        """Kiểm tra xem Rubik đã được giải chưa (với cache)"""
        # Sử dụng cache để tránh tính toán lặp
        state_key = SearchOptimizations.optimized_state_key(cube)
        
        with SolverAlgorithm._cache_lock:
            if state_key in SolverAlgorithm._is_solved_cache:
                return SolverAlgorithm._is_solved_cache[state_key]
        
        # Kiểm tra từng mặt có cùng màu không
        result = True
        for face in ['F', 'B', 'L', 'R', 'U', 'D']:
            # Lấy màu đầu tiên của mặt
            first_color = None
            for piece in cube.pieces:
                if face in piece.colors:
                    if first_color is None:
                        first_color = piece.colors[face]
                    elif piece.colors[face] != first_color:
                        result = False
                        break
            if not result:
                break
                
        # Cache kết quả
        with SolverAlgorithm._cache_lock:
            SolverAlgorithm._is_solved_cache[state_key] = result
            
        return result

    def _get_solved_cube(self) -> RubikCube:
        """Tạo một Rubik đã giải"""
        return RubikCube(self.cube.size)

    def _cube_state(self, cube: RubikCube) -> int:
        """Chuyển trạng thái Rubik thành giá trị hash để lưu trong visited - dùng phiên bản tối ưu"""
        return SearchOptimizations.optimized_state_key(cube)

    def _apply_move(self, cube: RubikCube, move: str) -> RubikCube:
        """Áp dụng một bước di chuyển lên Rubik và trả về cube mới - phiên bản tối ưu có cache"""
        # Sử dụng cache để tránh deep copy không cần thiết
        cube_state = SearchOptimizations.optimized_state_key(cube)
        cache_key = (cube_state, move)
        
        with SolverAlgorithm._cache_lock:
            if cache_key in SolverAlgorithm._move_results_cache:
                return SolverAlgorithm._move_results_cache[cache_key]
        
        # Nếu không có trong cache, thực hiện thao tác và lưu vào cache
        new_cube = copy.deepcopy(cube)
        clockwise = "'" not in move
        face = move[0]
        new_cube.rotate_face(face, clockwise)
        
        # Đợi animation hoàn thành
        if new_cube.animating:
            new_cube._complete_rotation()
            
        # Lưu vào cache
        with SolverAlgorithm._cache_lock:
            if len(SolverAlgorithm._move_results_cache) < 100000:  # Giới hạn kích thước cache
                SolverAlgorithm._move_results_cache[cache_key] = new_cube
                
        return new_cube

    def _apply_sequence(self, cube: RubikCube, sequence: List[str]) -> RubikCube:
        """Áp dụng một chuỗi các bước di chuyển"""
        current = copy.deepcopy(cube)
        for move in sequence:
            current = self._apply_move(current, move)
        return current

    def _get_possible_moves(self) -> List[str]:
        """Trả về danh sách các bước di chuyển có thể"""
        moves = []
        for face in ['F', 'B', 'L', 'R', 'U', 'D']:
            moves.append(face)      # Xoay thuận
            moves.append(f"{face}'")  # Xoay ngược
        return moves

    def _count_misplaced_pieces(self, cube: RubikCube) -> int:
        """Đếm số mảnh không đúng vị trí cho heuristic"""
        solved = self._get_solved_cube()
        count = 0
        for piece, solved_piece in zip(sorted(cube.pieces, key=lambda p: tuple(p.position)), 
                                     sorted(solved.pieces, key=lambda p: tuple(p.position))):
            if piece.colors != solved_piece.colors:
                count += 1
        return count

    def _heuristic(self, cube: RubikCube) -> float:
        """Đánh giá độ tốt của trạng thái hiện tại"""
        misplaced = self._count_misplaced_pieces(cube)
        return misplaced / len(cube.pieces)  # Normalize về 0-1
        
    @abstractmethod
    def solve(self) -> List[str]:
        """Solve the cube and return list of moves"""
        pass
    
    @property
    @abstractmethod
    def complexity(self) -> str:
        """Return the time complexity of the algorithm"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return description of how the algorithm works"""
        pass

    def parallelize(self, executor: concurrent.futures.Executor, should_cancel):
        """Default implementation for parallel execution
           Subclasses should override this for algorithm-specific parallelization"""
        # For parallel processing, we need to avoid callback functions 
        # that can't be pickled. Instead, check the should_cancel flag directly.
        
        # Set a flag to indicate we're running in parallel mode
        self.parallel_mode = True
        self.should_cancel = should_cancel
        
        # Call the standard solve method
        start_time = time.time()
        solution = self.solve()
        self.time_taken = time.time() - start_time
        
        return solution
    
    def _parallel_task(self, params):
        """Helper function for parallel tasks
        Params should contain all necessary data for the task"""
        # To be implemented by subclasses
        pass
