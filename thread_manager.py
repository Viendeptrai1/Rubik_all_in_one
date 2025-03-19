from PyQt5.QtCore import QObject, QThreadPool, pyqtSignal
import multiprocessing
import os

class ThreadManager(QObject):
    """Manages thread pool for CPU-intensive tasks"""
    
    # Get total number of CPU cores
    TOTAL_CORES = multiprocessing.cpu_count()
    
    # Reserve some cores for UI (at least 2, but no more than half the total)
    UI_CORES = min(max(2, TOTAL_CORES // 4), TOTAL_CORES // 2)
    
    # Number of cores to use for computation
    NUM_CORES = max(1, TOTAL_CORES - UI_CORES)
    
    def __init__(self):
        super().__init__()
        # Set environment variable to control thread usage in NumPy and other libraries
        os.environ["OMP_NUM_THREADS"] = str(self.NUM_CORES)
        os.environ["OPENBLAS_NUM_THREADS"] = str(self.NUM_CORES)
        os.environ["MKL_NUM_THREADS"] = str(self.NUM_CORES)
        
        # Use QThreadPool which doesn't have pickling issues
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(self.NUM_CORES)
        print(f"Thread pool initialized with {self.NUM_CORES} of {self.TOTAL_CORES} cores (reserving {self.UI_CORES} for UI)")
    
    def start_task(self, runnable):
        """Add a task to the thread pool"""
        self.thread_pool.start(runnable)
        
    def clear(self):
        """Clear all remaining tasks"""
        self.thread_pool.clear()
        
    def wait_for_done(self):
        """Wait for all tasks to complete"""
        self.thread_pool.waitForDone()
        
    @property
    def active_thread_count(self):
        """Get number of active threads"""
        return self.thread_pool.activeThreadCount()
        
# Global thread manager instance
thread_manager = ThreadManager()
