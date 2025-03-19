from PyQt5.QtCore import QRunnable, QObject, pyqtSignal
from typing import Any
import time
import traceback
import threading

class WorkerSignals(QObject):
    progress = pyqtSignal(int, int)
    status = pyqtSignal(str)
    finished = pyqtSignal(list, float)
    error = pyqtSignal(str)
    metrics = pyqtSignal(dict)  # New signal for reporting performance metrics

class SolverWorker(QRunnable):
    def __init__(self, algorithm):
        super().__init__()
        self.algorithm = algorithm
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
        if self.algorithm is not None:
            self.algorithm.signals = self.signals
    
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
        try:
            if self.algorithm is None:
                self.signals.error.emit("No algorithm provided")
                return
                
            # Report initialization
            self.signals.status.emit(f"Initializing {self.algorithm.__class__.__name__}...")
            
            # Set progress callback
            self.algorithm.set_progress_callback(self.progress_callback)
            
            # Set timeout for advanced algorithms
            timeout = False
            max_time = 60  # 60 seconds timeout
            start_time = time.time()
            
            # Create parallel solver with optimized settings if supported
            if hasattr(self.algorithm, 'set_parallel_solver'):
                from parallel_solver import ParallelSolver
                self.parallel_solver = ParallelSolver()
                self.algorithm.set_parallel_solver(self.parallel_solver)
                
                # Start metrics reporting
                self.start_metrics_reporting()
            
            # Start algorithm with timeout monitoring
            solution = None
            
            # Import here to avoid circular imports
            from algorithms.advanced import KociembaAlgorithm, ThistlethwaiteAlgorithm
            
            # Run the algorithm with timeout monitoring
            if isinstance(self.algorithm, (KociembaAlgorithm, ThistlethwaiteAlgorithm)):
                # Advanced algorithms get timeout monitoring
                import threading
                timeout_event = threading.Event()
                
                def check_timeout():
                    time.time_slept = 0
                    while time_time_slept < max_time and not timeout_event.is_set():
                        time.sleep(1.0)
                        time_time_slept += 1
                        
                        # Report progress periodically
                        if self.parallel_solver and time_time_slept % 5 == 0:
                            metrics = self.parallel_solver.get_metrics()
                            self.signals.status.emit(
                                f"Running for {time_time_slept}s... "
                                f"Tasks: {metrics['tasks_completed']}/{metrics['tasks_submitted']} "
                                f"({metrics['tasks_per_second']:.2f}/s)"
                            )
                    
                    if not timeout_event.is_set():
                        timeout_event.set()
                        self.signals.status.emit(f"Algorithm taking too long, stopping...")
                        self.is_cancelled = True
                
                timer_thread = threading.Thread(target=check_timeout)
                timer_thread.daemon = True
                timer_thread.start()
                
                try:
                    solution = self.algorithm.solve()
                finally:
                    timeout_event.set()  # Stop the timer thread
            else:
                # Regular algorithms
                solution = self.algorithm.solve()
                
            solve_time = time.time() - start_time
            
            if self.parallel_solver:
                # Get final metrics
                final_metrics = self.parallel_solver.get_metrics()
                self.signals.metrics.emit(final_metrics)
                
                # Stop the parallel solver
                self.parallel_solver.stop()
            
            # Cancel metrics timer if it exists
            if self.metrics_timer and self.metrics_timer.is_alive():
                self.metrics_timer.cancel()
            
            if self.is_cancelled:
                self.signals.error.emit("Solving cancelled by user or timeout")
            elif solution:
                self.signals.status.emit("Solution found!")
                self.signals.finished.emit(solution, solve_time)
            else:
                self.signals.error.emit("No solution found!")
                
        except Exception as e:
            import traceback
            error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_detail)  # Log to console
            self.signals.error.emit(error_detail)
            
        finally:
            if self.parallel_solver:
                self.parallel_solver.stop()
            if self.metrics_timer and self.metrics_timer.is_alive():
                self.metrics_timer.cancel()

    def cancel(self):
        self.is_cancelled = True
        if self.parallel_solver:
            self.parallel_solver.stop()
