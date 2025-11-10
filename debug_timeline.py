"""
Script debug timeline data
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime, date
from src.database.db_manager import DatabaseManager

def debug_timeline():
    """Debug dữ liệu timeline"""
    
    db = DatabaseManager()
    df = db.load_processed_data(limit=1000)
    
    print("=" * 80)
    print("📊 DATABASE DEBUG - TIMELINE")
    print("=" * 80)
    
    if df.empty:
        print("❌ NO DATA in database!")
        return
    
    print(f"\n✅ Total records: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Convert crawl_time
    df['crawl_time'] = pd.to_datetime(df['crawl_time'], errors='coerce')
    df['date'] = df['crawl_time'].dt.date
    
    print(f"\n📅 Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Check ngày 10/11
    target_date = date(2025, 11, 10)
    nov_10 = df[df['date'] == target_date]
    
    print(f"\n🔍 Checking date: {target_date}")
    print(f"Records found: {len(nov_10)}")
    
    if not nov_10.empty:
        print("\n📰 Articles on 10/11:")
        for idx, row in nov_10.iterrows():
            print(f"\n  - Title: {row['title'][:60]}...")
            print(f"    Source: {row['source']}")
            print(f"    Crawl time: {row['crawl_time']}")
            print(f"    Predicted label: {row.get('predicted_label', 'N/A')}")
            print(f"    Predicted sentiment: {row.get('predicted_sentiment', 'N/A')}")
        
        # Count by sentiment
        if 'predicted_label' in nov_10.columns:
            print("\n📊 Sentiment distribution on 10/11:")
            label_counts = nov_10['predicted_label'].value_counts().sort_index()
            for label, count in label_counts.items():
                sentiment_name = {0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'}.get(label, f'Unknown({label})')
                print(f"  {sentiment_name}: {count} bài")
        
        if 'predicted_sentiment' in nov_10.columns:
            print("\n📊 Predicted sentiment distribution on 10/11:")
            sentiment_counts = nov_10['predicted_sentiment'].value_counts()
            for sentiment, count in sentiment_counts.items():
                print(f"  {sentiment}: {count} bài")
    else:
        print("❌ NO ARTICLES found for 10/11!")
        print("\nAvailable dates:")
        for d in sorted(df['date'].unique())[-10:]:  # Last 10 dates
            count = len(df[df['date'] == d])
            print(f"  {d}: {count} bài")
    
    # Check timezone issues
    print("\n🕐 Timezone check:")
    print(f"Sample crawl_time dtypes: {df['crawl_time'].dtype}")
    print(f"Has timezone: {df['crawl_time'].dt.tz is not None}")
    
    if df['crawl_time'].dt.tz is not None:
        print(f"⚠️ WARNING: Data has timezone info!")
        print("Converting to local time...")
        df['crawl_time_local'] = df['crawl_time'].dt.tz_convert('Asia/Ho_Chi_Minh')
        df['date_local'] = df['crawl_time_local'].dt.date
        
        nov_10_local = df[df['date_local'] == target_date]
        print(f"After timezone conversion: {len(nov_10_local)} records on 10/11")

if __name__ == "__main__":
    debug_timeline()