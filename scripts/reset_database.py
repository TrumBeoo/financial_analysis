#!/usr/bin/env python3
"""
Script reset database với nhiều tùy chọn
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import MongoDBConfig
from src.services.cache_service import dashboard_cache
import argparse

def clear_specific_collections(collection_names):
    """Xóa các collections cụ thể"""
    config = MongoDBConfig()
    db = config.get_database()
    
    if db is None:
        print("❌ Không thể kết nối database!")
        return False
    
    deleted_total = 0
    for col_name in collection_names:
        if col_name in db.list_collection_names():
            count = db[col_name].count_documents({})
            result = db[col_name].delete_many({})
            deleted_total += result.deleted_count
            print(f"🗑️  Xóa {result.deleted_count} documents từ {col_name}")
        else:
            print(f"⚠️  Collection '{col_name}' không tồn tại")
    
    # Xóa cache
    dashboard_cache.clear()
    print("🧹 Đã xóa cache dashboard")
    
    print(f"✅ Tổng cộng xóa {deleted_total} documents và cache")
    return True

def drop_collections(collection_names):
    """Xóa hoàn toàn collections"""
    config = MongoDBConfig()
    db = config.get_database()
    
    if db is None:
        return False
    
    for col_name in collection_names:
        if col_name in db.list_collection_names():
            db[col_name].drop()
            print(f"🗑️  Đã xóa collection '{col_name}'")
        else:
            print(f"⚠️  Collection '{col_name}' không tồn tại")
    
    return True

def show_database_info():
    """Hiển thị thông tin database"""
    config = MongoDBConfig()
    db = config.get_database()
    
    if db is None:
        print("❌ Không thể kết nối database!")
        return
    
    collections = db.list_collection_names()
    print(f"📊 Database: {config.database}")
    print(f"📋 Collections ({len(collections)}):")
    
    total_docs = 0
    for col in collections:
        count = db[col].count_documents({})
        total_docs += count
        print(f"  - {col}: {count:,} documents")
    
    print(f"\n📈 Tổng: {total_docs:,} documents")

def main():
    parser = argparse.ArgumentParser(description='Reset MongoDB database')
    parser.add_argument('--info', action='store_true', help='Hiển thị thông tin database')
    parser.add_argument('--clear', nargs='*', help='Xóa dữ liệu từ collections cụ thể')
    parser.add_argument('--drop', nargs='*', help='Xóa hoàn toàn collections')
    parser.add_argument('--all', action='store_true', help='Xóa toàn bộ dữ liệu')
    parser.add_argument('--cache', action='store_true', help='Chỉ xóa cache dashboard')
    
    args = parser.parse_args()
    
    if args.info:
        show_database_info()
    elif args.clear is not None:
        if len(args.clear) == 0:
            # Xóa tất cả collections
            config = MongoDBConfig()
            collections = list(config.collections.values())
        else:
            collections = args.clear
        clear_specific_collections(collections)
    elif args.drop is not None:
        drop_collections(args.drop)
    elif args.all:
        confirm = input("⚠️  Xóa TOÀN BỘ database? (yes/no): ")
        if confirm.lower() == 'yes':
            config = MongoDBConfig()
            db = config.get_database()
            collections = db.list_collection_names()
            clear_specific_collections(collections)
    elif args.cache:
        dashboard_cache.clear()
        print("✅ Đã xóa cache dashboard")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()