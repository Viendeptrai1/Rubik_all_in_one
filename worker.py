from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from typing import Any
import time
import traceback
import threading

class WorkerSignals(QObject):
    progress = pyqtSignal(int, int)
    status = pyqtSignal(str)
    finished = pyqtSignal(object, float)  # Thay đổi từ list sang object để hỗ trợ nhiều kiểu dữ liệu trả về
    error = pyqtSignal(str)
    metrics = pyqtSignal(dict)  # New signal for reporting performance metrics

class SolverWorker(QRunnable):
    def __init__(self, algorithm):
        super().__init__()
        self.algorithm = algorithm
        self.callable_func = None  # Thêm biến để lưu hàm callable
        self.is_cancelled = False
        self.signals = WorkerSignals()
        self.parallel_solver = None
        self.metrics_timer = None
        
        # Only set signals if algorithm is provided
        if self.algorithm is not None:
            self.algorithm.signals = self.signals
    
    def set_algorithm(self, algorithm):
        """Set or update the algorithm after initialization"""
        self.algorithm = algorithm
        self.callable_func = None  # Reset callable function khi set algorithm
        if self.algorithm is not None:
            self.algorithm.signals = self.signals
    
    def set_callable(self, func):
        """Set a custom callable function to run instead of an algorithm"""
        self.callable_func = func
        self.algorithm = None  # Reset algorithm khi set callable
    
    def progress_callback(self, current, total):
        self.signals.progress.emit(current, total)
        return self.is_cancelled
    
    def start_metrics_reporting(self):
        """Start periodic reporting of performance metrics"""
        if not self.parallel_solver:
            return
            
        # Emit initial metrics
        metrics = self.parallel_solver.get_metrics()
        self.signals.metrics.emit(metrics)
        
        # Schedule next update if not cancelled
        if not self.is_cancelled:
            self.metrics_timer = threading.Timer(2.0, self.start_metrics_reporting)
            self.metrics_timer.daemon = True
            self.metrics_timer.start()
    
    def run(self):
        """Run the solver in a background thread"""
        solution = None
        start_time = time.time()
        
        try:
            self.signals.status.emit("Starting solving process...")
            
            # Báo cáo tiến trình ban đầu
            self.signals.progress.emit(0, 100)
            
            # Chạy thuật toán hoặc hàm tùy chỉnh
            if self.algorithm is not None:
                # Sử dụng thuật toán
                solution = self.algorithm.solve(self.progress_callback)
            elif self.callable_func is not None:
                # Sử dụng hàm tùy chỉnh
                solution = self.callable_func()
                # Báo cáo tiến trình hoàn thành
                self.signals.progress.emit(100, 100)
            else:
                raise ValueError("No algorithm or callable function provided")
            
            # Kiểm tra nếu đã hủy
            if self.is_cancelled:
                return
            
            # Kiểm tra kết quả
            if solution is None:
                self.signals.status.emit("No solution found!")
            else:
                self.signals.status.emit("Solution found!")
                
        except Exception as e:
            # Bắt và xử lý ngoại lệ
            trace = traceback.format_exc()
            error_msg = f"{str(e)}\n{trace}"
            print(f"Error in SolverWorker: {error_msg}")
            self.signals.error.emit(str(e))
            return
        finally:
            # Dừng báo cáo metrics
            if self.metrics_timer:
                self.metrics_timer.cancel()
            
            # Dừng parallel solver nếu có
            if self.parallel_solver:
                self.parallel_solver.stop()
        
        # Tính thời gian thực hiện
        elapsed_time = time.time() - start_time
        
        # Emit tín hiệu hoàn thành
        self.signals.finished.emit(solution, elapsed_time)
    
    def cancel(self):
        """Cancel the running solver"""
        self.is_cancelled = True
        
        # Dừng timer báo cáo metrics
        if self.metrics_timer:
            self.metrics_timer.cancel()
        
        # Dừng parallel solver nếu có
        if self.parallel_solver:
            self.parallel_solver.stop()
