
import threading
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import logging
logger = logging.getLogger(__name__)
from src.crawler.news_crawler import FinancialNewsCrawler
from src.database.db_manager import DatabaseManager
from src.processing.text_preprocessor import VietnameseTextPreprocessor
from src.processing.sentiment_analyzer import SentimentAnalyzer

# Global state
crawl_state = {
    'running': False,
    'progress': 0,
    'crawled': 0,
    'processed': 0,
    'errors': 0,
    'recent_articles': []
}

def register_crawler_callbacks(app):
    """Đăng ký callbacks cho crawler"""
    
    @app.callback(
        [Output('crawl-status', 'children'),
         Output('start-crawl-btn', 'disabled'),
         Output('stop-crawl-btn', 'disabled'),
         Output('crawl-progress-interval', 'disabled')],
        Input('start-crawl-btn', 'n_clicks'),
        [State('crawler-sources', 'value'),
         State('max-workers', 'value')],
        prevent_initial_call=True
    )
    def start_crawling(n_clicks, sources, max_workers):
        """Bắt đầu crawl"""
        if not sources:
            return (
                dbc.Alert("Vui lòng chọn ít nhất 1 nguồn tin", color='warning'),
                False, True, True
            )
        
        # Start crawl in background thread
        thread = threading.Thread(
            target=run_crawler_background,
            args=(sources, max_workers)
        )
        thread.daemon = True
        thread.start()
        
        crawl_state['running'] = True
        
        return (
            dbc.Alert("Đang crawl dữ liệu...", color='info'),
            True, False, False  # Disable start, enable stop, enable interval
        )
    
    @app.callback(
        Output('stop-crawl-btn', 'disabled', allow_duplicate=True),
        Input('stop-crawl-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def stop_crawling(n_clicks):
        """Dừng crawl"""
        crawl_state['running'] = False
        return True
    
    @app.callback(
        [Output('crawl-progress', 'value'),
         Output('crawled-count', 'children'),
         Output('processed-count', 'children'),
         Output('error-count', 'children'),
         Output('recent-crawled-articles', 'children')],
        Input('crawl-progress-interval', 'n_intervals')
    )
    def update_crawl_progress(n):
        """Cập nhật progress real-time"""
        progress = crawl_state.get('progress', 0)
        crawled = crawl_state.get('crawled', 0)
        processed = crawl_state.get('processed', 0)
        errors = crawl_state.get('errors', 0)
        recent = crawl_state.get('recent_articles', [])
        
        # Render recent articles
        article_items = []
        for article in recent[-10:]:  # Hiển thị 10 bài gần nhất
            article_items.append(
                dbc.ListGroupItem([
                    html.Strong(article.get('title', 'N/A')),
                    html.Br(),
                    html.Small(f"Nguồn: {article.get('source', 'N/A')}", className='text-muted')
                ])
            )
        
        articles_display = dbc.ListGroup(article_items) if article_items else html.P("Chưa có bài viết", className="text-muted")
        
        return progress, str(crawled), str(processed), str(errors), articles_display

def run_crawler_background(sources, max_workers):
    """Chạy crawler trong background thread"""
    try:
        crawler = FinancialNewsCrawler()
        db_manager = DatabaseManager()
        preprocessor = VietnameseTextPreprocessor()
        sentiment_analyzer = SentimentAnalyzer()
        
        # Reset state
        crawl_state.update({
            'progress': 0,
            'crawled': 0,
            'processed': 0,
            'errors': 0,
            'recent_articles': []
        })
        
        # Crawl từng nguồn
        total_sources = len(sources)
        
        for idx, source in enumerate(sources):
            if not crawl_state['running']:
                break
            
            try:
                # Crawl
                articles = crawler.crawl_source(source)
                crawl_state['crawled'] += len(articles)
                
                # Process và lưu
                for article in articles:
                    try:
                        full_text = f"{article['title']} {article.get('summary', '')}"
                        processed = preprocessor.preprocess_pipeline(full_text)
                        sentiment = sentiment_analyzer.analyze(full_text)
                        
                        article.update({
                            'cleaned_text': processed['cleaned_text'],
                            'sentiment_positive': sentiment['positive'],
                            'sentiment_negative': sentiment['negative'],
                            'sentiment_neutral': sentiment['neutral'],
                            'predicted_label': sentiment['label'],
                            'sectors': ','.join(processed['sectors'])
                        })
                        
                        crawl_state['processed'] += 1
                        crawl_state['recent_articles'].append(article)
                        
                    except Exception as e:
                        crawl_state['errors'] += 1
                        logger.error(f"Error processing article: {e}")
                
                # Lưu vào database
                if articles:
                    df = pd.DataFrame(articles)
                    db_manager.save_processed_data(df)
                
            except Exception as e:
                crawl_state['errors'] += 1
                logger.error(f"Error crawling {source}: {e}")
            
            # Update progress
            crawl_state['progress'] = int(((idx + 1) / total_sources) * 100)
        
        crawl_state['running'] = False
        crawl_state['progress'] = 100
        
    except Exception as e:
        logger.error(f"Crawler background error: {e}")
        crawl_state['running'] = False