#!/usr/bin/env python3
"""
Script xóa cache dashboard
"""

from src.services.cache_service import dashboard_cache

def clear_cache():
    """Xóa toàn bộ cache dashboard"""
    try:
        dashboard_cache.clear()
        print("✅ Đã xóa toàn bộ cache dashboard")
        return True
    except Exception as e:
        print(f"❌ Lỗi xóa cache: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Xóa cache dashboard")
    print("=" * 25)
    clear_cache()