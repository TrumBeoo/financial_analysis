# -*- coding: utf-8 -*-
"""
Improved URL Crawler with better error handling and encoding
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
import time

class ImprovedURLCrawler:
    def __init__(self):
        self.url_parser = URLParser()
        self.db_manager = DatabaseManager()
        self.preprocessor = VietnameseTextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_url(self, url, save_to_db=True):
        """
        Analyze single URL with improved error handling
        """
        result = {
            'success': False,
            'url': url,
            'error': None,
            'data': None
        }
        
        try:
            # 1. Parse URL
            parse_result = self.url_parser.parse_url(url)
            
            if not parse_result['success']:
                result['error'] = f"Parse failed: {parse_result.get('error', 'Unknown')}"
                return result
            
            # 2. Process text if content exists
            if not parse_result['content']:
                result['error'] = "No content found"
                return result
            
            full_text = f"{parse_result['title']} {parse_result['content']}"
            
            # 3. Preprocess
            processed = self.preprocessor.preprocess_pipeline(full_text)
            
            # 4. Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze(full_text)
            sentiment_labels = ['Tiêu cực', 'Trung tính', 'Tích cực']
            sentiment_label = sentiment_labels[sentiment['label']]
            
            # 5. Prepare data
            data = {
                'source': parse_result['source'],
                'title': parse_result['title'],
                'summary': parse_result['content'][:200] + '...' if len(parse_result['content']) > 200 else parse_result['content'],
                'content': parse_result['content'],
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
            
            # 6. Save to database
            if save_to_db:
                try:
                    df_save = pd.DataFrame([data])
                    self.db_manager.save_processed_data(df_save)
                except Exception as e:
                    print(f"Warning: Could not save to database: {str(e)}")
            
            result['success'] = True
            result['data'] = data
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def batch_analyze(self, urls, delay=1):
        """
        Analyze multiple URLs with delay between requests
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"Processing {i}/{len(urls)}: {url}")
            
            result = self.analyze_url(url)
            results.append(result)
            
            if result['success']:
                print(f"  SUCCESS: {result['data']['title'][:50]}...")
                print(f"  Sentiment: {result['data']['predicted_sentiment']}")
            else:
                print(f"  FAILED: {result['error']}")
            
            # Delay between requests
            if i < len(urls):
                time.sleep(delay)
        
        return results
    
    def get_stats(self):
        """Get database statistics"""
        try:
            df = self.db_manager.load_processed_data(limit=1000)
            
            if df.empty:
                return {"total": 0, "by_sentiment": {}, "by_source": {}}
            
            stats = {
                "total": len(df),
                "by_sentiment": df['predicted_sentiment'].value_counts().to_dict() if 'predicted_sentiment' in df.columns else {},
                "by_source": df['source'].value_counts().to_dict() if 'source' in df.columns else {},
                "latest": df.iloc[0]['title'] if 'title' in df.columns else 'N/A'
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}

def demo_improved_crawler():
    """Demo the improved crawler"""
    print("IMPROVED URL CRAWLER DEMO")
    print("=" * 50)
    
    crawler = ImprovedURLCrawler()
    
    # Test URLs (use real ones)
    test_urls = [
        "https://example.com",
        "https://httpbin.org/html"  # Simple test page
    ]
    
    print("\n1. Testing batch analysis...")
    results = crawler.batch_analyze(test_urls)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nResults: {len(successful)} successful, {len(failed)} failed")
    
    print("\n2. Database statistics...")
    stats = crawler.get_stats()
    
    if 'error' not in stats:
        print(f"Total articles: {stats['total']}")
        print(f"By sentiment: {stats['by_sentiment']}")
        print(f"By source: {stats['by_source']}")
        print(f"Latest: {stats['latest']}")
    else:
        print(f"Error getting stats: {stats['error']}")
    
    print("\n" + "=" * 50)
    print("DEMO COMPLETED")

if __name__ == "__main__":
    demo_improved_crawler()