"""
Service layer để tách biệt logic xử lý dữ liệu khỏi UI
"""
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Dict, Any, Optional

from src.database.db_manager import DatabaseManager
from src.crawler.url_parser import URLParser
from src.processing.text_preprocessor import VietnameseTextPreprocessor
from src.processing.sentiment_analyzer import SentimentAnalyzer
from src.services.cache_service import dashboard_cache
from config.settings import SENTIMENT_LABELS

logger = logging.getLogger(__name__)

class DataService:
    """Service xử lý dữ liệu độc lập với UI"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.url_parser = URLParser()
        self.preprocessor = VietnameseTextPreprocessor()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_url(self, url: str) -> Dict[str, Any]:
        """Phân tích URL và trả về kết quả"""
        try:
            # Parse URL
            result = self.url_parser.parse_url(url)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Không thể trích xuất nội dung')
                }
            
            # Preprocess
            full_text = f"{result['title']} {result['content']}"
            processed = self.preprocessor.preprocess_pipeline(full_text)
            
            # Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze(full_text)
            sentiment_label = SENTIMENT_LABELS[sentiment['label']]
            
            return {
                'success': True,
                'data': {
                    'source': result['source'],
                    'title': result['title'],
                    'content': result['content'],
                    'link': url,
                    'cleaned_text': processed['cleaned_text'],
                    'sectors': processed.get('sectors', []),
                    'sentiment': {
                        'label': sentiment_label,
                        'scores': {
                            'positive': sentiment['positive'],
                            'negative': sentiment['negative'],
                            'neutral': sentiment['neutral']
                        },
                        'predicted_label': sentiment['label']
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing URL: {str(e)}")
            return {
                'success': False,
                'error': f"Lỗi xử lý: {str(e)}"
            }
    
    def save_analysis_result(self, analysis_result: Dict[str, Any]) -> bool:
        """Lưu kết quả phân tích vào database"""
        try:
            if not analysis_result.get('success'):
                return False
            
            data = analysis_result['data']
            sentiment = data['sentiment']
            
            save_data = {
                'source': data['source'],
                'title': data['title'],
                'content': data['content'][:500],
                'link': data['link'],
                'crawl_time': datetime.now(),
                'cleaned_text': data['cleaned_text'],
                'sentiment_positive': sentiment['scores']['positive'],
                'sentiment_negative': sentiment['scores']['negative'],
                'sentiment_neutral': sentiment['scores']['neutral'],
                'predicted_label': sentiment['predicted_label'],
                'predicted_sentiment': sentiment['label'],
                'sectors': ','.join(data['sectors']) if data['sectors'] else 'Other',
                'processed_at': datetime.now()
            }
            
            df_save = pd.DataFrame([save_data])
            success = self.db_manager.save_processed_data(df_save)
            
            # Xóa cache khi có dữ liệu mới
            if success:
                dashboard_cache.clear()
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving analysis result: {str(e)}")
            return False
    
    def get_dashboard_data(self, limit: int = 1000, use_cache: bool = True) -> pd.DataFrame:
        """Lấy dữ liệu cho dashboard với cache"""
        cache_key = f"dashboard_data_{limit}"
        
        if use_cache:
            cached_data = dashboard_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        try:
            df = self.db_manager.load_processed_data(limit=limit)
            
            if use_cache and not df.empty:
                dashboard_cache.set(cache_key, df, timeout=60)  # Cache 1 phút
            
            return df
        except Exception as e:
            logger.error(f"Error loading dashboard data: {str(e)}")
            return pd.DataFrame()
    
    def get_stats(self, df: Optional[pd.DataFrame] = None, use_cache: bool = True) -> Dict[str, Any]:
        """Tính toán thống kê từ DataFrame với cache"""
        cache_key = "dashboard_stats"
        
        if use_cache:
            cached_stats = dashboard_cache.get(cache_key)
            if cached_stats is not None:
                return cached_stats
        
        if df is None:
            df = self.get_dashboard_data(use_cache=use_cache)
        
        if df.empty:
            stats = {
                'total': 0,
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
        else:
            total = len(df)
            positive = len(df[df['predicted_label'] == 2]) if 'predicted_label' in df.columns else 0
            neutral = len(df[df['predicted_label'] == 1]) if 'predicted_label' in df.columns else 0
            negative = len(df[df['predicted_label'] == 0]) if 'predicted_label' in df.columns else 0
            
            stats = {
                'total': total,
                'positive': positive,
                'neutral': neutral,
                'negative': negative
            }
        
        if use_cache:
            dashboard_cache.set(cache_key, stats, timeout=60)
        
        return stats