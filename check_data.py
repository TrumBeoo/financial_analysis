#!/usr/bin/env python3
"""
Script kiểm tra dữ liệu trong database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import DatabaseManager
import pandas as pd

def check_data():
    """Kiểm tra dữ liệu chi tiết"""
    db = DatabaseManager()
    
    print("=" * 60)
    print("KIỂM TRA DỮ LIỆU PROCESSED_ARTICLES")
    print("=" * 60)
    
    df = db.load_processed_data(limit=100)
    
    if df.empty:
        print("❌ KHÔNG CÓ DỮ LIỆU!")
        return
    
    print(f"\n✓ Số lượng bài: {len(df)}")
    print(f"\n📋 Các cột có sẵn:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\n📊 Mẫu dữ liệu đầu tiên:")
    print(df.head(1).to_dict('records'))
    
    # Kiểm tra sentiment
    print(f"\n🎭 SENTIMENT:")
    if 'predicted_label' in df.columns:
        print(f"  predicted_label: {df['predicted_label'].value_counts().to_dict()}")
    if 'predicted_sentiment' in df.columns:
        print(f"  predicted_sentiment: {df['predicted_sentiment'].value_counts().to_dict()}")
    
    # Kiểm tra sectors
    print(f"\n🏢 SECTORS:")
    if 'sectors' in df.columns:
        print(f"  Unique sectors: {df['sectors'].unique().tolist()}")
        print(f"  Sample values: {df['sectors'].head(10).tolist()}")
    
    # Kiểm tra content
    print(f"\n📝 CONTENT:")
    if 'content' in df.columns:
        avg_len = df['content'].str.len().mean()
        print(f"  Avg content length: {avg_len:.0f} chars")
        print(f"  Sample: {df['content'].iloc[0][:200]}...")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_data()