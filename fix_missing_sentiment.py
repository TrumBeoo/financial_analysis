#!/usr/bin/env python3
"""
Script fix dữ liệu cũ thiếu predicted_sentiment
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from config.database import MongoDBConfig
from datetime import datetime

def fix_missing_sentiment():
    """Fix predicted_sentiment bị null"""
    config = MongoDBConfig()
    db = config.get_database()
    
    if db is None:
        print("❌ Không thể kết nối database!")
        return
    
    collection = db['processed_articles']
    
    # Mapping
    sentiment_map = {
        0: 'Tiêu cực',
        1: 'Trung tính',
        2: 'Tích cực'
    }
    
    # Find documents with null predicted_sentiment
    query = {
        '$or': [
            {'predicted_sentiment': {'$exists': False}},
            {'predicted_sentiment': None},
            {'predicted_sentiment': float('nan')},
            {'predicted_sentiment': 'nan'}
        ]
    }
    
    docs_to_fix = list(collection.find(query))
    
    print(f"📊 Found {len(docs_to_fix)} documents with missing predicted_sentiment")
    
    if len(docs_to_fix) == 0:
        print("✅ All documents have predicted_sentiment!")
        return
    
    # Confirm
    confirm = input(f"\n⚠️  Fix {len(docs_to_fix)} documents? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled")
        return
    
    # Update
    fixed_count = 0
    error_count = 0
    
    for doc in docs_to_fix:
        try:
            predicted_label = doc.get('predicted_label')
            
            if predicted_label is not None and predicted_label in [0, 1, 2]:
                predicted_sentiment = sentiment_map[predicted_label]
                
                collection.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'predicted_sentiment': predicted_sentiment}}
                )
                
                fixed_count += 1
                
                if fixed_count % 50 == 0:
                    print(f"  Processed {fixed_count}/{len(docs_to_fix)}...")
            else:
                print(f"⚠️  Skipping doc with invalid predicted_label: {predicted_label}")
                error_count += 1
                
        except Exception as e:
            print(f"❌ Error fixing doc {doc.get('_id')}: {e}")
            error_count += 1
    
    print(f"\n✅ Fixed {fixed_count} documents")
    print(f"⚠️  Errors: {error_count}")
    
    # Verify
    remaining = collection.count_documents(query)
    print(f"📊 Remaining null sentiment: {remaining}")

if __name__ == "__main__":
    print("🔧 Fix Missing Predicted Sentiment")
    print("=" * 50)
    fix_missing_sentiment()