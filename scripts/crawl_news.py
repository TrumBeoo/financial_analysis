"""
Script để crawl tin tức từ command line
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from datetime import datetime
from src.crawler.news_crawler import FinancialNewsCrawler
from src.database.db_manager import DatabaseManager
from src.processing.text_preprocessor import VietnameseTextPreprocessor
from src.processing.sentiment_analyzer import SentimentAnalyzer
from src.models.classifier import NewsClassifier
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Chạy crawler và lưu vào database"""
    
    logger.info("🚀 Bắt đầu crawl tin tức...")
    
    # Khởi tạo
    crawler = FinancialNewsCrawler()
    db_manager = DatabaseManager()
    preprocessor = VietnameseTextPreprocessor()
    sentiment_analyzer = SentimentAnalyzer()
    
    # Crawl
    df_news = crawler.crawl_all(max_workers=3)
    
    if df_news.empty:
        logger.warning("⚠️ Không crawl được tin tức nào!")
        return
    
    logger.info(f"✓ Crawled {len(df_news)} articles")
    
    # Kiểm tra content
    if 'content' in df_news.columns:
        avg_length = df_news['content'].str.len().mean()
        logger.info(f"📊 Average content length: {avg_length:.0f} chars")
    else:
        logger.warning("⚠️ No content field in crawled data!")
    
    # Lưu dữ liệu gốc
    db_manager.save_news_data(df_news)
    
    # Xử lý từng bài
    processed_data = []
    
    for idx, row in df_news.iterrows():
        try:
            # SỬA: Sử dụng full content thay vì chỉ title + summary
            if 'content' in row and row['content']:
                full_text = f"{row['title']} {row['content']}"
            else:
                full_text = f"{row['title']} {row.get('summary', '')}"
            
            logger.info(f"Processing article {idx+1}/{len(df_news)}: {row['title'][:50]}...")
            logger.info(f"  Text length: {len(full_text)} chars")
            
            # Preprocess
            processed = preprocessor.preprocess_pipeline(full_text)
            
            # Analyze sentiment
            sentiment = sentiment_analyzer.analyze(full_text)
            
            logger.info(f"  Sentiment: {sentiment['label']} | Sectors: {processed['sectors']}")
            
            processed_data.append({
                'source': row['source'],
                'title': row['title'],
                'summary': row.get('summary', ''),
                'content': row.get('content', ''),  # THÊM: Lưu full content
                'link': row['link'],
                'crawl_time': row['crawl_time'],
                'cleaned_text': processed['cleaned_text'],
                'sentiment_positive': sentiment['positive'],
                'sentiment_negative': sentiment['negative'],
                'sentiment_neutral': sentiment['neutral'],
                'predicted_label': sentiment['label'],
                'predicted_sentiment': ['Tiêu cực', 'Trung tính', 'Tích cực'][sentiment['label']],
                'sectors': ','.join(processed['sectors']),
                'processed_at': datetime.now()
            })
            
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý bài {idx}: {e}")
            continue
    
    # Lưu dữ liệu đã xử lý
    if processed_data:
        df_processed = pd.DataFrame(processed_data)
        db_manager.save_processed_data(df_processed)
        logger.info(f"✅ Đã xử lý và lưu {len(df_processed)} bài viết")
        
        # Statistics
        logger.info(f"\n📊 THỐNG KÊ:")
        logger.info(f"  - Tích cực: {len(df_processed[df_processed['predicted_label']==2])}")
        logger.info(f"  - Trung tính: {len(df_processed[df_processed['predicted_label']==1])}")
        logger.info(f"  - Tiêu cực: {len(df_processed[df_processed['predicted_label']==0])}")
        
        if 'content' in df_processed.columns:
            logger.info(f"  - Avg content: {df_processed['content'].str.len().mean():.0f} chars")
    
    logger.info("✅ Hoàn thành!")

if __name__ == '__main__':
    main()