# -*- coding: utf-8 -*-
"""
Demo script for URL analysis functionality
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

def demo_url_analysis():
    print("=" * 60)
    print("DEMO: URL ANALYSIS FUNCTIONALITY")
    print("=" * 60)
    
    # Real URLs for testing
    test_urls = [
        "https://vnexpress.net/kinh-doanh",
        "https://example.com"
    ]
    
    # Initialize components
    url_parser = URLParser()
    db_manager = DatabaseManager()
    preprocessor = VietnameseTextPreprocessor()
    sentiment_analyzer = SentimentAnalyzer()
    
    print("\n1. TESTING URL PARSING...")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- URL {i}: {url} ---")
        
        try:
            # Parse URL
            result = url_parser.parse_url(url)
            
            if not result['success']:
                print(f"FAILED: {result.get('error', 'Unknown error')}")
                continue
            
            print("SUCCESS: URL parsed")
            print(f"Title: {result['title']}")
            print(f"Source: {result['source']}")
            print(f"Content length: {len(result['content'])} characters")
            
            # Process text if content exists
            if result['content']:
                full_text = f"{result['title']} {result['content']}"
                
                # Preprocess
                processed = preprocessor.preprocess_pipeline(full_text)
                print(f"Cleaned text: {processed['cleaned_text'][:100]}...")
                print(f"Detected sectors: {processed['sectors']}")
                
                # Analyze sentiment
                sentiment = sentiment_analyzer.analyze(full_text)
                sentiment_labels = ['Negative', 'Neutral', 'Positive']
                sentiment_label = sentiment_labels[sentiment['label']]
                
                print(f"Sentiment: {sentiment_label}")
                print(f"Scores - Pos: {sentiment['positive']:.3f}, "
                      f"Neu: {sentiment['neutral']:.3f}, "
                      f"Neg: {sentiment['negative']:.3f}")
                
                # Prepare data for saving
                save_data = {
                    'source': result['source'],
                    'title': result['title'],
                    'summary': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                    'content': result['content'],
                    'link': url,
                    'crawl_time': datetime.now(),
                    'cleaned_text': processed['cleaned_text'],
                    'sentiment_positive': sentiment['positive'],
                    'sentiment_negative': sentiment['negative'],
                    'sentiment_neutral': sentiment['neutral'],
                    'predicted_label': sentiment['label'],
                    'predicted_sentiment': sentiment_label,
                    'sectors': ','.join(processed['sectors']) if processed['sectors'] else 'Other',
                    'processed_at': datetime.now()
                }
                
                print("Data prepared for database")
                
                # Save to database
                try:
                    df_save = pd.DataFrame([save_data])
                    success = db_manager.save_processed_data(df_save)
                    if success:
                        print("SUCCESS: Data saved to database")
                    else:
                        print("FAILED: Could not save to database")
                except Exception as e:
                    print(f"ERROR saving to database: {str(e)}")
            
            else:
                print("No content to process")
                
        except Exception as e:
            print(f"ERROR processing URL: {str(e)}")
    
    print("\n2. TESTING DATABASE RETRIEVAL...")
    try:
        df_processed = db_manager.load_processed_data(limit=5)
        print(f"Retrieved {len(df_processed)} processed articles from database")
        
        if not df_processed.empty:
            print("Sample data columns:", list(df_processed.columns))
            print("Latest article:", df_processed.iloc[0]['title'] if 'title' in df_processed.columns else 'N/A')
        
    except Exception as e:
        print(f"ERROR retrieving from database: {str(e)}")
    
    print("\n3. SUMMARY...")
    print("URL Analysis functionality includes:")
    print("- URL validation and content extraction")
    print("- Vietnamese text preprocessing")
    print("- Sentiment analysis with confidence scores")
    print("- Sector detection")
    print("- Database storage and retrieval")
    print("- Dashboard integration for real-time analysis")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    demo_url_analysis()