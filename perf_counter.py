import time
import threading
from typing import Dict

class PerfCounter:
    """
    Thread-safe performance counter for tracking algorithm metrics
    """
    
    _lock = threading.RLock()
    _counters: Dict[str, float] = {}
    _timers: Dict[str, float] = {}
    
    @staticmethod
    def start(key: str):
        """Start timing an operation"""
        with PerfCounter._lock:
            PerfCounter._timers[key] = time.time()
    
    @staticmethod
    def stop(key: str):
        """Stop timing an operation and add to counter"""
        with PerfCounter._lock:
            if key in PerfCounter._timers:
                duration = time.time() - PerfCounter._timers[key]
                if key in PerfCounter._counters:
                    PerfCounter._counters[key] += duration
                else:
                    PerfCounter._counters[key] = duration
                del PerfCounter._timers[key]
    
    @staticmethod
    def increment(key: str, amount: float = 1.0):
        """Increment a counter by amount"""
        with PerfCounter._lock:
            if key in PerfCounter._counters:
                PerfCounter._counters[key] += amount
            else:
                PerfCounter._counters[key] = amount
    
    @staticmethod
    def get_value(key: str) -> float:
        """Get the current value of a counter"""
        with PerfCounter._lock:
            return PerfCounter._counters.get(key, 0.0)
    
    @staticmethod
    def get_all() -> Dict[str, float]:
        """Get all counter values"""
        with PerfCounter._lock:
            return PerfCounter._counters.copy()
    
    @staticmethod
    def reset():
        """Reset all counters"""
        with PerfCounter._lock:
            PerfCounter._counters.clear()
            PerfCounter._timers.clear()
