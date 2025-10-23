# -*- coding: utf-8 -*-
"""
Simple test script for URL crawler functionality
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.crawler.url_parser import URLParser
from src.database.db_manager import DatabaseManager
from src.processing.text_preprocessor import VietnameseTextPreprocessor
from src.processing.sentiment_analyzer import SentimentAnalyzer
from datetime import datetime
import pandas as pd

def test_simple():
    print("=" * 50)
    print("SIMPLE URL CRAWLER TEST")
    print("=" * 50)
    
    # Test URLs that should work
    test_urls = [
        "https://cafef.vn",
        "https://vnexpress.net/kinh-doanh",
        "https://example.com"
    ]
    
    # Initialize components
    url_parser = URLParser()
    db_manager = DatabaseManager()
    
    print("\n1. Testing database connection...")
    try:
        df = db_manager.load_news_data(limit=1)
        print("Database connection: OK")
        print(f"Existing records: {len(df)}")
    except Exception as e:
        print(f"Database error: {str(e)}")
    
    print("\n2. Testing URL parser...")
    for i, url in enumerate(test_urls, 1):
        print(f"\nTesting URL {i}: {url}")
        try:
            result = url_parser.parse_url(url)
            if result['success']:
                print("Parse: SUCCESS")
                print(f"Title: {result['title'][:50]}...")
                print(f"Content length: {len(result['content'])}")
            else:
                print(f"Parse: FAILED - {result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"Parse: ERROR - {str(e)}")
    
    print("\n3. Testing text processing...")
    try:
        preprocessor = VietnameseTextPreprocessor()
        sentiment_analyzer = SentimentAnalyzer()
        
        test_text = "Chung khoan tang manh trong phien hom nay"
        processed = preprocessor.preprocess_pipeline(test_text)
        sentiment = sentiment_analyzer.analyze(test_text)
        
        print("Text processing: SUCCESS")
        print(f"Cleaned text: {processed['cleaned_text']}")
        print(f"Sentiment: {sentiment['label']}")
        
    except Exception as e:
        print(f"Text processing: ERROR - {str(e)}")
    
    print("\n4. Testing data save...")
    try:
        sample_data = {
            'source': 'test',
            'title': 'Test article',
            'summary': 'Test summary',
            'link': 'http://test.com',
            'crawl_time': datetime.now(),
            'cleaned_text': 'test text',
            'sentiment_positive': 0.5,
            'sentiment_negative': 0.3,
            'sentiment_neutral': 0.2,
            'predicted_label': 1,
            'predicted_sentiment': 'Neutral',
            'sectors': 'Other',
            'processed_at': datetime.now()
        }
        
        df_test = pd.DataFrame([sample_data])
        success = db_manager.save_processed_data(df_test)
        
        if success:
            print("Data save: SUCCESS")
        else:
            print("Data save: FAILED")
            
    except Exception as e:
        print(f"Data save: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("TEST COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    test_simple()