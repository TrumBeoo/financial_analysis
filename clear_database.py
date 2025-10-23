#!/usr/bin/env python3
"""
Script xóa toàn bộ dữ liệu trong MongoDB database
"""

from config.database import MongoDBConfig
from src.services.cache_service import dashboard_cache
import sys

def clear_database():
    """Xóa toàn bộ dữ liệu trong database"""
    config = MongoDBConfig()
    
    # Kết nối database
    db = config.get_database()
    if db is None:
        print("❌ Không thể kết nối đến database!")
        return False
    
    try:
        # Lấy danh sách collections
        collections = db.list_collection_names()
        
        if not collections:
            print("✅ Database đã trống!")
            return True
        
        print(f"📋 Tìm thấy {len(collections)} collections:")
        for col in collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
        
        # Xác nhận xóa
        confirm = input("\n⚠️  Bạn có chắc muốn xóa TOÀN BỘ dữ liệu? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Hủy bỏ thao tác xóa")
            return False
        
        # Xóa từng collection
        deleted_total = 0
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            result = collection.delete_many({})
            deleted_total += result.deleted_count
            print(f"🗑️  Đã xóa {result.deleted_count} documents từ {collection_name}")
        
        # Xóa cache
        dashboard_cache.clear()
        print("🧹 Đã xóa cache dashboard")
        
        print(f"\n✅ Hoàn thành! Đã xóa tổng cộng {deleted_total} documents và cache")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi xóa database: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Script xóa toàn bộ dữ liệu database")
    print("=" * 40)
    
    success = clear_database()
    sys.exit(0 if success else 1)