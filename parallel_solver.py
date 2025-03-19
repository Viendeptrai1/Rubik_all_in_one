import threading
import queue
import time
import numpy as np
import traceback
from PyQt5.QtCore import QObject, pyqtSignal
from thread_manager import ThreadManager
from perf_counter import PerfCounter

class WorkerThread(threading.Thread):
    def __init__(self, task_queue, result_queue, should_stop, index):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.should_stop = should_stop
        self.daemon = True
        self.index = index  # Thread index for debugging

    def run(self):
        while not self.should_stop.is_set():
            try:
                # Get task with timeout to check should_stop regularly
                task_item = self.task_queue.get(timeout=0.1)
                
                if task_item is None:  # Sentinel value to stop
                    break
                    
                # Support both single tasks and batch tasks
                if isinstance(task_item, list):
                    # Batch processing mode - process multiple tasks at once
                    results = []
                    for task, args, kwargs in task_item:
                        try:
                            PerfCounter.start(f"worker_{self.index}_task")
                            result = task(*args, **kwargs)
                            PerfCounter.stop(f"worker_{self.index}_task")
                            results.append(result)
                        except Exception as e:
                            error_msg = f"Task error: {str(e)}\n{traceback.format_exc()}"
                            results.append((False, error_msg))
                    
                    self.result_queue.put(("batch", results))
                    self.task_queue.task_done()
                else:
                    # Standard single task format
                    task, args, kwargs = task_item
                    if task is None:  # Sentinel value
                        break
                    
                    # Execute task
                    PerfCounter.start(f"worker_{self.index}_task")
                    result = task(*args, **kwargs)
                    PerfCounter.stop(f"worker_{self.index}_task")
                    self.result_queue.put(result)
                    self.task_queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                # Improved error handling
                error_msg = f"Worker {self.index} error: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)  # Log to console
                self.result_queue.put((False, error_msg))
                self.task_queue.task_done()

class ParallelSolver:
    """Manages multiple worker threads for parallel solving"""
    
    def __init__(self, num_threads=None):
        if num_threads is None:
            num_threads = ThreadManager.NUM_CORES
        self.num_threads = num_threads
        
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.should_stop = threading.Event()
        self.workers = []
        self.tasks_submitted = 0
        self.tasks_completed = 0
        self.batch_size = 10  # Default batch size
        self._current_batch = []
        self._batch_lock = threading.Lock()
        
        # Performance metrics
        self.start_time = time.time()
        PerfCounter.reset()
        
        # Create worker threads
        for i in range(self.num_threads):
            worker = WorkerThread(self.task_queue, self.result_queue, self.should_stop, i)
            worker.start()
            self.workers.append(worker)
        
        print(f"ParallelSolver initialized with {self.num_threads} threads (out of {ThreadManager.TOTAL_CORES} available)")

    def submit(self, task, *args, **kwargs):
        """Submit a task to be executed by a worker thread"""
        if self.should_stop.is_set():
            return False
            
        PerfCounter.increment("tasks_submitted")
        self.tasks_submitted += 1
        self.task_queue.put((task, args, kwargs))
        return True
    
    def submit_batch(self, tasks):
        """Submit a batch of tasks at once for better efficiency
        
        Args:
            tasks: List of (task, args, kwargs) tuples
        """
        if self.should_stop.is_set() or not tasks:
            return False
            
        PerfCounter.increment("tasks_submitted", len(tasks))
        self.tasks_submitted += len(tasks)
        self.task_queue.put(tasks)
        return True
    
    def add_to_batch(self, task, *args, **kwargs):
        """Add a task to the current batch (will be sent when batch is full)"""
        if self.should_stop.is_set():
            return False
            
        with self._batch_lock:
            self._current_batch.append((task, args, kwargs))
            
            # Submit when batch is full
            if len(self._current_batch) >= self.batch_size:
                self.flush_batch()
        return True
    
    def flush_batch(self):
        """Force submission of the current batch even if not full"""
        with self._batch_lock:
            if self._current_batch:
                self.submit_batch(self._current_batch)
                self._current_batch = []
    
    def get_result(self, block=True, timeout=None):
        """Get a result from completed tasks"""
        try:
            result = self.result_queue.get(block=block, timeout=timeout)
            
            # Handle batch results
            if isinstance(result, tuple) and len(result) == 2 and result[0] == "batch":
                # Return first result from batch and queue the rest
                batch_results = result[1]
                if batch_results:
                    first_result = batch_results[0]
                    # Re-queue the remaining results
                    for r in batch_results[1:]:
                        self.result_queue.put(r)
                    self.tasks_completed += 1
                    PerfCounter.increment("tasks_completed")
                    return first_result
            
            self.tasks_completed += 1
            PerfCounter.increment("tasks_completed")
            return result
        except queue.Empty:
            return None
    
    def get_multiple_results(self, count=None, timeout=0.1):
        """Get multiple results at once, up to count (or all available if count=None)"""
        results = []
        start_time = time.time()
        remaining = count
        
        while (remaining is None or remaining > 0) and (time.time() - start_time < timeout):
            result = self.get_result(block=False)
            if result is None:
                # No more results available without blocking
                if results:  # Return what we have if anything
                    break
                # Wait a bit before checking again
                time.sleep(0.01)
                continue
                
            results.append(result)
            if remaining is not None:
                remaining -= 1
                
        return results
    
    def results_available(self):
        """Check if results are available"""
        return not self.result_queue.empty()
    
    def pending_tasks(self):
        """Return number of unprocessed tasks"""
        return self.tasks_submitted - self.tasks_completed
    
    def get_metrics(self):
        """Get performance metrics"""
        runtime = time.time() - self.start_time
        tasks_per_sec = self.tasks_completed / runtime if runtime > 0 else 0
        
        metrics = {
            "runtime_seconds": runtime,
            "tasks_submitted": self.tasks_submitted,
            "tasks_completed": self.tasks_completed,
            "tasks_per_second": tasks_per_sec,
            "queue_size": self.task_queue.qsize(),
            "result_queue_size": self.result_queue.qsize(),
            "counters": PerfCounter.get_all()
        }
        return metrics
    
    def stop(self):
        """Stop all worker threads"""
        if self.should_stop.is_set():
            return  # Already stopping
            
        self.should_stop.set()
        
        # Flush any remaining batch
        self.flush_batch()
        
        # Clear the task queue
        try:
            while True:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
        except queue.Empty:
            pass
        
        # Add sentinel tasks to ensure threads exit
        for _ in self.workers:
            self.task_queue.put(None)
        
        # Wait for threads to finish
        for worker in self.workers:
            worker.join(timeout=0.5)
        
        # Log metrics
        metrics = self.get_metrics()
        print(f"ParallelSolver stopped. Processed {metrics['tasks_completed']} tasks "
              f"in {metrics['runtime_seconds']:.2f}s ({metrics['tasks_per_second']:.2f}/s)")
