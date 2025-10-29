#!/usr/bin/env python3
"""
Script sửa dữ liệu sectors và sentiment trong database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager
from config.database import MongoDBConfig
import pandas as pd

# Mapping sectors từ tiếng Việt sang tiếng Anh
SECTOR_MAPPING = {
    'bất_động_sản': 'Real Estate',
    'ngân_hàng': 'Banking',
    'chứng_khoán': 'Finance',
    'công_nghệ': 'Technology',
    'sản_xuất': 'Manufacturing',
    'năng_lượng': 'Energy',
    'vận_tải': 'Transportation',
    'nông_nghiệp': 'Agriculture',
    'bán_lẻ': 'Retail',
    'tổng_hợp': 'Other',
    'Finance': 'Finance',
    'Real Estate': 'Real Estate',
    'Banking': 'Banking',
    'Technology': 'Technology',
    'Manufacturing': 'Manufacturing',
    'Energy': 'Energy',
    'Transportation': 'Transportation',
    'Agriculture': 'Agriculture',
    'Retail': 'Retail',
    'Other': 'Other'
}

def normalize_sectors(sector_str):
    """Chuẩn hóa chuỗi sectors"""
    if pd.isna(sector_str) or not sector_str or sector_str == 'nan':
        return 'Other'
    
    # Split by comma
    sectors = [s.strip() for s in str(sector_str).split(',')]
    
    # Map to English
    normalized = []
    for sector in sectors:
        mapped = SECTOR_MAPPING.get(sector, 'Other')
        if mapped not in normalized:  # Avoid duplicates
            normalized.append(mapped)
    
    # Return main sector (first one)
    return normalized[0] if normalized else 'Other'

def fix_data():
    """Sửa dữ liệu trong database"""
    config = MongoDBConfig()
    db = config.get_database()
    collection = db['processed_articles']
    
    print("🔧 BẮT ĐẦU SỬA DỮ LIỆU...")
    print("=" * 60)
    
    # Lấy tất cả documents
    documents = list(collection.find())
    print(f"📊 Tìm thấy {len(documents)} bài viết")
    
    updated_count = 0
    sentiment_fixed = 0
    sector_fixed = 0
    
    for doc in documents:
        update_fields = {}
        
        # 1. Sửa predicted_sentiment nếu thiếu
        if 'predicted_sentiment' not in doc or not doc['predicted_sentiment']:
            if 'predicted_label' in doc:
                label_map = {0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'}
                update_fields['predicted_sentiment'] = label_map.get(doc['predicted_label'], 'Trung tính')
                sentiment_fixed += 1
        
        # 2. Sửa sectors
        if 'sectors' in doc:
            old_sector = doc['sectors']
            new_sector = normalize_sectors(old_sector)
            
            if old_sector != new_sector:
                update_fields['sectors'] = new_sector
                sector_fixed += 1
                print(f"  ✓ Sector: '{old_sector}' -> '{new_sector}'")
        else:
            update_fields['sectors'] = 'Other'
            sector_fixed += 1
        
        # Update document
        if update_fields:
            collection.update_one(
                {'_id': doc['_id']},
                {'$set': update_fields}
            )
            updated_count += 1
    
    print("\n" + "=" * 60)
    print(f"✅ HOÀN THÀNH!")
    print(f"   - Tổng số bài cập nhật: {updated_count}")
    print(f"   - Sentiment đã sửa: {sentiment_fixed}")
    print(f"   - Sectors đã sửa: {sector_fixed}")
    print("=" * 60)
    
    # Kiểm tra kết quả
    print("\n🔍 KIỂM TRA KẾT QUẢ:")
    
    # Count by sentiment
    pipeline_sentiment = [
        {'$group': {'_id': '$predicted_sentiment', 'count': {'$sum': 1}}}
    ]
    sentiment_counts = list(collection.aggregate(pipeline_sentiment))
    print("\n📊 Sentiment distribution:")
    for item in sentiment_counts:
        print(f"   - {item['_id']}: {item['count']}")
    
    # Count by sector
    pipeline_sector = [
        {'$group': {'_id': '$sectors', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    sector_counts = list(collection.aggregate(pipeline_sector))
    print("\n🏢 Sector distribution:")
    for item in sector_counts[:10]:  # Top 10
        print(f"   - {item['_id']}: {item['count']}")

if __name__ == "__main__":
    confirm = input("⚠️  Bạn có chắc muốn sửa dữ liệu? (yes/no): ")
    if confirm.lower() == 'yes':
        fix_data()
    else:
        print("❌ Hủy bỏ")