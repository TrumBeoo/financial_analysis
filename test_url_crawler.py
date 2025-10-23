#!/usr/bin/env python3
"""
Script test chức năng crawl dữ liệu từ URL và lưu vào database
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

def test_url_crawler():
    """Test crawl từ URL cụ thể"""
    
    # URLs test
    test_urls = [
        "https://cafef.vn/chung-khoan-vn30-tang-manh-hon-1-trong-phien-giao-dich-cuoi-tuan-20241220142856789.chn",
        "https://vneconomy.vn/chung-khoan-viet-nam-tang-manh-trong-phien-20-12.htm",
        "https://vietstock.vn/2024/12/tin-tuc-doanh-nghiep-moi-nhat-1234567.htm"
    ]
    
    print("Bat dau test URL crawler...")
    
    # Khởi tạo
    url_parser = URLParser()
    db_manager = DatabaseManager()
    preprocessor = VietnameseTextPreprocessor()
    sentiment_analyzer = SentimentAnalyzer()
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest URL {i}: {url}")
        
        try:
            # 1. Parse URL
            result = url_parser.parse_url(url)
            
            if not result['success']:
                print(f"Loi parse URL: {result.get('error', 'Unknown error')}")
                continue
            
            print(f"Parse thanh cong:")
            print(f"   - Tiêu đề: {result['title'][:100]}...")
            print(f"   - Nguồn: {result['source']}")
            print(f"   - Nội dung: {len(result['content'])} ký tự")
            
            # 2. Preprocess
            full_text = f"{result['title']} {result['content']}"
            processed = preprocessor.preprocess_pipeline(full_text)
            
            print(f"Preprocess thanh cong:")
            print(f"   - Text đã làm sạch: {len(processed['cleaned_text'])} ký tự")
            print(f"   - Ngành phát hiện: {processed['sectors']}")
            
            # 3. Analyze sentiment
            sentiment = sentiment_analyzer.analyze(full_text)
            sentiment_labels = ['Tiêu cực', 'Trung tính', 'Tích cực']
            sentiment_label = sentiment_labels[sentiment['label']]
            
            print(f"Phan tich sentiment:")
            print(f"   - Kết quả: {sentiment_label}")
            print(f"   - Tích cực: {sentiment['positive']:.3f}")
            print(f"   - Trung tính: {sentiment['neutral']:.3f}")
            print(f"   - Tiêu cực: {sentiment['negative']:.3f}")
            
            # 4. Chuẩn bị dữ liệu lưu
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
            
            results.append(save_data)
            print(f"Chuan bi du lieu thanh cong")
            
        except Exception as e:
            print(f"Loi xu ly URL {i}: {str(e)}")
            continue
    
    # 5. Lưu vào database
    if results:
        print(f"\nLuu {len(results)} bai viet vao database...")
        
        try:
            # Lưu dữ liệu gốc
            df_news = pd.DataFrame([{
                'source': r['source'],
                'title': r['title'],
                'summary': r['summary'],
                'link': r['link'],
                'crawl_time': r['crawl_time']
            } for r in results])
            
            success_news = db_manager.save_news_data(df_news)
            
            # Lưu dữ liệu đã xử lý
            df_processed = pd.DataFrame(results)
            success_processed = db_manager.save_processed_data(df_processed)
            
            if success_news and success_processed:
                print("Luu database thanh cong!")
            else:
                print("Co loi khi luu database")
                
        except Exception as e:
            print(f"Loi luu database: {str(e)}")
    
    else:
        print("Khong co du lieu de luu")
    
    print(f"\nTong ket:")
    print(f"   - URLs test: {len(test_urls)}")
    print(f"   - Thành công: {len(results)}")
    print(f"   - Thất bại: {len(test_urls) - len(results)}")

def test_database_connection():
    """Test kết nối database"""
    print("\nTest ket noi database...")
    
    try:
        db_manager = DatabaseManager()
        
        # Test load dữ liệu
        df_news = db_manager.load_news_data(limit=5)
        df_processed = db_manager.load_processed_data(limit=5)
        
        print(f"Ket noi database thanh cong!")
        print(f"   - Tin tức gốc: {len(df_news)} bài")
        print(f"   - Tin tức đã xử lý: {len(df_processed)} bài")
        
        if not df_processed.empty:
            print(f"   - Cột dữ liệu: {list(df_processed.columns)}")
            
    except Exception as e:
        print(f"Loi ket noi database: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST URL CRAWLER & DATABASE")
    print("=" * 60)
    
    # Test database trước
    test_database_connection()
    
    # Test URL crawler
    test_url_crawler()
    
    print("\n" + "=" * 60)
    print("HOAN THANH TEST")
    print("=" * 60)