"""
Cache service để tối ưu hiệu suất dashboard
"""
import time
from typing import Any, Optional
import pandas as pd

class CacheService:
    """Service quản lý cache cho dashboard"""
    
    def __init__(self, default_timeout: int = 300):
        self._cache = {}
        self.default_timeout = default_timeout
    
    def get(self, key: str) -> Optional[Any]:
        """Lấy dữ liệu từ cache"""
        if key in self._cache:
            data, timestamp, timeout = self._cache[key]
            if time.time() - timestamp < timeout:
                return data
            else:
                # Xóa cache hết hạn
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Lưu dữ liệu vào cache"""
        if timeout is None:
            timeout = self.default_timeout
        
        self._cache[key] = (value, time.time(), timeout)
    
    def clear(self) -> None:
        """Xóa toàn bộ cache"""
        self._cache.clear()
    
    def delete(self, key: str) -> bool:
        """Xóa một key khỏi cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

# Global cache instance
dashboard_cache = CacheService(default_timeout=300)  # 5 phút