import os
import json
import pickle
import time
import threading
import hashlib

class CacheManager:
    """
    Class quản lý cache cho các pattern database và trạng thái
    """
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    _lock = threading.RLock()
    _cache = {}
    _max_memory_cache_size = 100  # Maximum number of items in memory cache
    
    @staticmethod
    def ensure_cache_dir():
        """Đảm bảo thư mục cache tồn tại"""
        if not os.path.exists(CacheManager.CACHE_DIR):
            os.makedirs(CacheManager.CACHE_DIR)
    
    @staticmethod
    def save_db(db, name):
        """Lưu database vào file"""
        with CacheManager._lock:
            CacheManager.ensure_cache_dir()
            path = os.path.join(CacheManager.CACHE_DIR, f"{name}.pkl")
            
            # Lưu dạng binary để nhanh hơn và nhỏ gọn hơn
            with open(path, 'wb') as f:
                pickle.dump(db, f, protocol=pickle.HIGHEST_PROTOCOL)
                
    @staticmethod
    def load_db(name):
        """Tải database từ file"""
        with CacheManager._lock:
            CacheManager.ensure_cache_dir()
            path = os.path.join(CacheManager.CACHE_DIR, f"{name}.pkl")
            
            # Nếu đã có trong memory cache, trả về từ đó
            if name in CacheManager._cache:
                return CacheManager._cache[name]
                
            # Nếu không, tải từ file
            if os.path.exists(path):
                try:
                    with open(path, 'rb') as f:
                        db = pickle.load(f)
                        # Lưu vào memory cache
                        CacheManager._add_to_memory_cache(name, db)
                        return db
                except Exception as e:
                    print(f"Error loading cache {name}: {e}")
                    
            return {}
    
    @staticmethod
    def _add_to_memory_cache(name, data):
        """Add item to memory cache, managing cache size"""
        with CacheManager._lock:
            # If cache is full, remove oldest item
            if len(CacheManager._cache) >= CacheManager._max_memory_cache_size:
                oldest_key = next(iter(CacheManager._cache))
                del CacheManager._cache[oldest_key]
                
            CacheManager._cache[name] = data
            
    @staticmethod
    def compute_db_hash(cube):
        """Tính hash cho cube để sử dụng làm tên db"""
        # Tính hash dựa trên kích thước cube
        return f"cube_{cube.size}_db"
    
    @staticmethod
    def clear_memory_cache():
        """Xóa cache trong bộ nhớ để giải phóng RAM"""
        with CacheManager._lock:
            CacheManager._cache.clear()
