"""
Performance optimization utilities
"""
import functools
import time
import logging
from typing import Any, Callable
import pandas as pd

logger = logging.getLogger(__name__)

def cache_result(timeout: int = 300):
    """
    Decorator để cache kết quả function trong thời gian timeout (seconds)
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Tạo cache key từ args và kwargs
            cache_key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()
            
            # Kiểm tra cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if current_time - timestamp < timeout:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            # Thực thi function và cache kết quả
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            
            # Cleanup old cache entries
            keys_to_remove = []
            for key, (_, timestamp) in cache.items():
                if current_time - timestamp >= timeout:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del cache[key]
            
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            return result
        
        return wrapper
    return decorator

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tối ưu hóa DataFrame để giảm memory usage
    """
    if df.empty:
        return df
    
    # Optimize numeric columns
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # Optimize string columns
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # If less than 50% unique values
            df[col] = df[col].astype('category')
    
    return df

def batch_process(data: list, batch_size: int = 100, process_func: Callable = None):
    """
    Xử lý dữ liệu theo batch để tránh memory overflow
    """
    results = []
    
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        if process_func:
            batch_result = process_func(batch)
            results.extend(batch_result if isinstance(batch_result, list) else [batch_result])
        else:
            results.extend(batch)
    
    return results

def measure_performance(func: Callable) -> Callable:
    """
    Decorator để đo performance của function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper

class DataCache:
    """
    Simple in-memory cache for dashboard data
    """
    def __init__(self, default_timeout: int = 300):
        self.cache = {}
        self.default_timeout = default_timeout
    
    def get(self, key: str) -> Any:
        """Get cached value"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.default_timeout:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, timeout: int = None) -> None:
        """Set cached value"""
        timeout = timeout or self.default_timeout
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        keys_to_remove = []
        
        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp >= self.default_timeout:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]

# Global cache instance
dashboard_cache = DataCache()