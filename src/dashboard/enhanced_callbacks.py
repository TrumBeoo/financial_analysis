"""
Enhanced Callbacks cho Dashboard với tất cả tính năng mới
"""
from dash import Output, Input, State, html, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import logging
import numpy as np

from src.database.db_manager import DatabaseManager
from src.utils.performance import cache_result, optimize_dataframe, dashboard_cache
from config.settings import SECTOR_MAPPINGS, PERFORMANCE_CONFIG
from src.crawler.url_parser import URLParser
from src.processing.text_preprocessor import VietnameseTextPreprocessor
from src.processing.sentiment_analyzer import SentimentAnalyzer
from config.settings import SENTIMENT_COLORS, SENTIMENT_LABELS

logger = logging.getLogger(__name__)

# Khởi tạo
db_manager = DatabaseManager()
url_parser = URLParser()
preprocessor = VietnameseTextPreprocessor()
sentiment_analyzer = SentimentAnalyzer()

def register_enhanced_callbacks(app):
    """Đăng ký tất cả callbacks nâng cao"""
    
    # Stats với filters
    @app.callback(
        [Output('total-articles', 'children'),
         Output('positive-count', 'children'),
         Output('neutral-count', 'children'),
         Output('negative-count', 'children'),
         Output('market-sentiment-index', 'children')],
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_stats_with_filters(n, sector, days, sentiment_type):
        """Cập nhật thống kê với filters"""
        df = get_filtered_data(sector, days, sentiment_type)
        
        if df.empty:
            return "0", "0", "0", "0", "+0.00"
        
        total = len(df)
        positive = len(df[df['predicted_label'] == 2]) if 'predicted_label' in df.columns else 0
        neutral = len(df[df['predicted_label'] == 1]) if 'predicted_label' in df.columns else 0
        negative = len(df[df['predicted_label'] == 0]) if 'predicted_label' in df.columns else 0
        
        # Market Sentiment Index
        if 'predicted_label' in df.columns:
            sentiment_scores = df['predicted_label'].map({0: -1, 1: 0, 2: 1})
            avg_score = sentiment_scores.mean()
            market_index = f"{avg_score:+.2f}"
        else:
            market_index = "+0.00"
        
        return str(total), str(positive), str(neutral), str(negative), market_index
    
    # Gauge Chart cho Market Sentiment
    @app.callback(
        Output('sentiment-gauge-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_gauge_chart(n, sector, days, sentiment_type):
        """Biểu đồ gauge cho sentiment tổng quan"""
        df = get_filtered_data(sector, days, sentiment_type)
        
        if df.empty or 'predicted_label' not in df.columns:
            return go.Figure()
        
        # Tính tỷ lệ tích cực
        sentiment_counts = df['predicted_label'].value_counts(normalize=True)
        positive_ratio = sentiment_counts.get(2, 0) * 100
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = positive_ratio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Tỷ lệ tin tích cực (%)"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#2ecc71"},
                'steps': [
                    {'range': [0, 25], 'color': "#ffebee"},
                    {'range': [25, 50], 'color': "#fff3e0"},
                    {'range': [50, 75], 'color': "#e8f5e8"},
                    {'range': [75, 100], 'color': "#c8e6c9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        return fig
    
    # Heatmap theo ngành
    @app.callback(
        Output('sector-heatmap', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_heatmap(n, days, sentiment_type):
        """Bản đồ nhiệt theo ngành"""
        df = get_filtered_data('all', days, sentiment_type)
        
        if df.empty or 'predicted_label' not in df.columns:
            return go.Figure()
        
        # Các ngành chính
        sectors = ['Banking', 'Energy', 'Real Estate', 'Technology', 'Manufacturing', 'Other']
        sentiment_matrix = []
        
        for sector in sectors:
            if 'sectors' in df.columns:
                sector_data = df[df['sectors'].str.contains(sector, na=False)]
            else:
                sector_data = df
                
            if not sector_data.empty:
                sentiment_scores = sector_data['predicted_label'].map({0: -1, 1: 0, 2: 1})
                avg_score = sentiment_scores.mean()
            else:
                avg_score = 0
            sentiment_matrix.append([avg_score])
        
        fig = go.Figure(data=go.Heatmap(
            z=sentiment_matrix,
            y=sectors,
            x=['Sentiment Score'],
            colorscale='RdYlGn',
            zmid=0,
            colorbar=dict(title="Sentiment Score"),
            text=[[f"{score[0]:.2f}"] for score in sentiment_matrix],
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            height=300,
            xaxis_title='',
            yaxis_title='',
            margin=dict(l=100, r=50, t=20, b=20)
        )
        
        return fig
    
    # Enhanced Sector Bar Chart
    @app.callback(
        Output('sector-bar-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_sector_chart(n, sector, days, sentiment_type):
        """Biểu đồ cột theo ngành với điểm sentiment"""
        df = get_filtered_data('all', days, sentiment_type)
        
        if df.empty or 'predicted_label' not in df.columns:
            return go.Figure()
        
        # Ensure sectors column
        if 'sectors' not in df.columns:
            df['sectors'] = 'Other'
        
        # Calculate average sentiment score by sector
        df['sentiment_score'] = df['predicted_label'].map({0: -1, 1: 0, 2: 1})
        sector_stats = df.groupby('sectors').agg({
            'sentiment_score': 'mean',
            'predicted_label': 'count'
        }).reset_index()
        
        sector_stats = sector_stats.sort_values('sentiment_score', ascending=False)
        
        # Color based on sentiment
        colors = [SENTIMENT_COLORS['Tích cực'] if score > 0.1 else 
                 SENTIMENT_COLORS['Tiêu cực'] if score < -0.1 else 
                 SENTIMENT_COLORS['Trung tính'] for score in sector_stats['sentiment_score']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=sector_stats['sectors'],
            y=sector_stats['sentiment_score'],
            marker_color=colors,
            text=[f'{score:.2f}<br>({count} bài)' for score, count in 
                  zip(sector_stats['sentiment_score'], sector_stats['predicted_label'])],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Sentiment: %{y:.2f}<br>Số bài: %{customdata}<extra></extra>',
            customdata=sector_stats['predicted_label']
        ))
        
        fig.update_layout(
            xaxis_title='Ngành',
            yaxis_title='Điểm Sentiment Trung bình',
            yaxis=dict(range=[-1, 1]),
            hovermode='x unified'
        )
        
        return fig
    
    # Word Cloud Display
    @app.callback(
        Output('word-cloud-display', 'children'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value')]
    )
    def update_word_cloud(n, sector, days):
        """Hiển thị từ khóa nổi bật"""
        df = get_filtered_data(sector, days, 'all')
        
        if df.empty or 'cleaned_text' not in df.columns:
            return html.P("Chưa có dữ liệu", className='text-muted text-center')
        
        # Extract keywords
        all_text = ' '.join(df['cleaned_text'].dropna())
        keywords = extract_keywords(all_text, top_n=15)
        
        if not keywords:
            return html.P("Chưa có từ khóa", className='text-muted text-center')
        
        # Create badges with different sizes
        badges = []
        for i, (word, count) in enumerate(keywords):
            size = 'lg' if i < 3 else 'md' if i < 8 else 'sm'
            color = 'primary' if i < 3 else 'info' if i < 8 else 'secondary'
            
            badges.append(
                dbc.Badge(
                    f"{word} ({count})",
                    color=color,
                    className=f'me-1 mb-1 badge-{size}',
                    style={'fontSize': '14px' if size == 'lg' else '12px' if size == 'md' else '10px'}
                )
            )
        
        return html.Div(badges)
    
    # Enhanced Timeline
    @app.callback(
        Output('sentiment-timeline', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_timeline(n, sector, days, sentiment_type):
        """Timeline với smooth line và trend"""
        df = get_filtered_data(sector, days, sentiment_type)
        
        if df.empty or 'crawl_time' not in df.columns:
            return go.Figure()
        
        # Prepare data
        if 'predicted_sentiment' not in df.columns and 'predicted_label' in df.columns:
            df['predicted_sentiment'] = df['predicted_label'].map({0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'})
        
        df['date'] = pd.to_datetime(df['crawl_time']).dt.date
        
        # Group by date and sentiment
        timeline_data = df.groupby(['date', 'predicted_sentiment']).size().reset_index(name='count')
        
        fig = go.Figure()
        
        for sentiment in ['Tích cực', 'Trung tính', 'Tiêu cực']:
            sentiment_data = timeline_data[timeline_data['predicted_sentiment'] == sentiment]
            if not sentiment_data.empty:
                fig.add_trace(go.Scatter(
                    x=sentiment_data['date'],
                    y=sentiment_data['count'],
                    mode='lines+markers',
                    name=sentiment,
                    line=dict(color=SENTIMENT_COLORS[sentiment], width=3),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{sentiment}</b><br>Ngày: %{{x}}<br>Số bài: %{{y}}<extra></extra>'
                ))
        
        fig.update_layout(
            xaxis_title='Ngày',
            yaxis_title='Số lượng bài viết',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    # Correlation Chart (Mock data for now)
    @app.callback(
        Output('correlation-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_correlation(n):
        """Biểu đồ tương quan sentiment-giá (mock data)"""
        # Generate mock correlation data
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        sentiment_scores = np.random.normal(0, 0.3, 30)
        price_changes = sentiment_scores * 0.6 + np.random.normal(0, 0.15, 30)
        
        fig = go.Figure()
        
        # Sentiment line
        fig.add_trace(go.Scatter(
            x=dates,
            y=sentiment_scores,
            mode='lines',
            name='Sentiment Score',
            line=dict(color='#3498db', width=2),
            yaxis='y'
        ))
        
        # Price change line
        fig.add_trace(go.Scatter(
            x=dates,
            y=price_changes,
            mode='lines',
            name='Price Change (%)',
            line=dict(color='#e74c3c', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            yaxis=dict(title='Sentiment Score', side='left', color='#3498db'),
            yaxis2=dict(title='Price Change (%)', side='right', overlaying='y', color='#e74c3c'),
            hovermode='x unified',
            height=300,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    # Enhanced News Table
    @app.callback(
        Output('enhanced-news-table', 'children'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_enhanced_table(n, sector, days, sentiment_type):
        """Bảng tin tức nâng cao với tương tác"""
        df = get_filtered_data(sector, days, sentiment_type, limit=20)
        
        if df.empty:
            return html.P("Chưa có dữ liệu", className='text-muted text-center')
        
        # Ensure sentiment column
        if 'predicted_sentiment' not in df.columns and 'predicted_label' in df.columns:
            df['predicted_sentiment'] = df['predicted_label'].map({0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'})
        
        rows = []
        for idx, row in df.iterrows():
            sentiment = row.get('predicted_sentiment', 'N/A')
            color_map = {'Tích cực': 'success', 'Trung tính': 'secondary', 'Tiêu cực': 'danger'}
            color = color_map.get(sentiment, 'secondary')
            
            # Format title with highlighting
            title = row.get('title', 'N/A')
            truncated_title = title[:80] + '...' if len(title) > 80 else title
            highlighted_title = highlight_sentiment_words(truncated_title)
            
            # Format time
            crawl_time = row.get('crawl_time', datetime.now())
            if hasattr(crawl_time, 'strftime'):
                time_str = crawl_time.strftime('%d/%m %H:%M')
            else:
                time_str = 'N/A'
            
            rows.append(
                html.Tr([
                    html.Td([
                        html.Div([
                            html.Strong(highlighted_title),
                            html.Br(),
                            html.Small(str(row.get('content', ''))[:100] + '...', className='text-muted')
                        ])
                    ]),
                    html.Td(row.get('source', 'N/A')),
                    html.Td([
                        dbc.Badge(sentiment, color=color, className='me-1'),
                        html.Br(),
                        html.Small(f"Score: {row.get('sentiment_positive', 0):.2f}", className='text-muted')
                    ]),
                    html.Td(row.get('sectors', 'Other')),
                    html.Td(time_str)
                ])
            )
        
        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Tiêu đề & Nội dung"),
                    html.Th("Nguồn"),
                    html.Th("Sentiment"),
                    html.Th("Ngành"),
                    html.Th("Thời gian")
                ])
            ),
            html.Tbody(rows)
        ], bordered=True, hover=True, responsive=True, striped=True)
        
        return table
    
    # Enhanced URL Analysis
    @app.callback(
        [Output('url-analysis-result', 'children'),
         Output('detailed-url-analysis', 'children')],
        Input('analyze-btn', 'n_clicks'),
        State('url-input', 'value'),
        prevent_initial_call=True
    )
    def analyze_url_enhanced(n_clicks, url):
        """Phân tích URL chi tiết với keyword highlighting"""
        if not url:
            alert = dbc.Alert("Vui lòng nhập URL", color='warning')
            return alert, alert
        
        try:
            # Parse URL
            result = url_parser.parse_url(url)
            
            if not result['success']:
                error_alert = dbc.Alert(f"Lỗi: {result.get('error', 'Không thể trích xuất nội dung')}", color='danger')
                return error_alert, error_alert
            
            # Preprocess
            full_text = f"{result['title']} {result['content']}"
            processed = preprocessor.preprocess_pipeline(full_text)
            
            # Analyze sentiment
            sentiment = sentiment_analyzer.analyze(full_text)
            sentiment_label = SENTIMENT_LABELS[sentiment['label']]
            
            # Extract keywords
            keywords = extract_keywords(processed['cleaned_text'])
            
            # Save to database
            save_data = {
                'source': result['source'],
                'title': result['title'],
                'content': result['content'][:500],
                'link': url,
                'crawl_time': datetime.now(),
                'cleaned_text': processed['cleaned_text'],
                'sentiment_positive': sentiment['positive'],
                'sentiment_negative': sentiment['negative'],
                'sentiment_neutral': sentiment['neutral'],
                'predicted_label': sentiment['label'],
                'predicted_sentiment': sentiment_label,
                'sectors': 'Other'
            }
            
            df_save = pd.DataFrame([save_data])
            db_manager.save_processed_data(df_save)
            
            # Basic result
            basic_result = dbc.Alert(f"✅ Phân tích thành công! Sentiment: {sentiment_label}", color='success')
            
            # Detailed result
            sentiment_color_map = {'Tích cực': 'success', 'Trung tính': 'secondary', 'Tiêu cực': 'danger'}
            color = sentiment_color_map.get(sentiment_label, 'secondary')
            
            detailed_result = dbc.Card([
                dbc.CardHeader([
                    html.H4("🔍 Phân tích chi tiết bài viết", className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H5("📰 Thông tin bài viết"),
                            html.P([html.Strong("Tiêu đề: "), result['title']]),
                            html.P([html.Strong("Nguồn: "), result['source']]),
                            html.P([html.Strong("Ngày: "), datetime.now().strftime('%d/%m/%Y %H:%M')]),
                            html.Hr(),
                            html.H5("📊 Phân tích Sentiment"),
                            dbc.Badge(sentiment_label, color=color, className='fs-6 mb-3'),
                            html.Div([
                                html.P(f"Tích cực: {sentiment['positive']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['positive']*100, color='success', className='mb-2'),
                                html.P(f"Trung tính: {sentiment['neutral']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['neutral']*100, color='secondary', className='mb-2'),
                                html.P(f"Tiêu cực: {sentiment['negative']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['negative']*100, color='danger')
                            ], className='mb-3')
                        ], width=6),
                        dbc.Col([
                            html.H5("📝 Tóm tắt nội dung"),
                            html.P(result['content'][:400] + '...' if len(result['content']) > 400 else result['content']),
                            html.Hr(),
                            html.H5("🔑 Từ khóa quan trọng"),
                            html.Div([
                                dbc.Badge(keyword[0], color='info', className='me-1 mb-1') 
                                for keyword in keywords[:10]
                            ]),
                            html.Hr(),
                            html.H5("🔗 Liên kết"),
                            html.A("Xem bài gốc", href=url, target="_blank", className="btn btn-outline-primary")
                        ], width=6)
                    ])
                ])
            ], className='mt-3')
            
            return basic_result, detailed_result
            
        except Exception as e:
            logger.error(f"Error in URL analysis: {str(e)}")
            error_alert = dbc.Alert(f"Lỗi xử lý: {str(e)}", color='danger')
            return error_alert, error_alert

@cache_result(timeout=PERFORMANCE_CONFIG['cache_timeout'])
def get_filtered_data(sector='all', days=30, sentiment_type='all', limit=1000):
    """Lấy dữ liệu đã lọc theo các tiêu chí với cache"""
    # Try cache first
    cache_key = f"filtered_data_{sector}_{days}_{sentiment_type}_{limit}"
    cached_result = dashboard_cache.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    df = db_manager.load_processed_data(limit=limit)
    
    if df.empty:
        return df
    
    # Optimize DataFrame
    df = optimize_dataframe(df)
    
    # Filter by time
    if 'crawl_time' in df.columns:
        cutoff_date = datetime.now() - timedelta(days=days)
        df = df[pd.to_datetime(df['crawl_time']) >= cutoff_date]
    
    # Map sectors to standard names
    if 'sectors' in df.columns:
        df['sectors'] = df['sectors'].map(lambda x: SECTOR_MAPPINGS.get(x, 'Other') if pd.notna(x) else 'Other')
    
    # Filter by sector
    if sector != 'all' and 'sectors' in df.columns:
        df = df[df['sectors'] == sector]
    
    # Filter by sentiment
    if sentiment_type != 'all':
        if 'predicted_sentiment' in df.columns:
            df = df[df['predicted_sentiment'] == sentiment_type]
        elif 'predicted_label' in df.columns:
            label_map = {'Tích cực': 2, 'Trung tính': 1, 'Tiêu cực': 0}
            if sentiment_type in label_map:
                df = df[df['predicted_label'] == label_map[sentiment_type]]
    
    # Cache result
    dashboard_cache.set(cache_key, df)
    
    return df

def highlight_sentiment_words(text):
    """Highlight từ cảm xúc trong text"""
    from dash import dcc
    
    positive_words = ['tăng', 'mạnh', 'tốt', 'phục hồi', 'ổn định', 'khả quan', 'tích cực', 'lợi nhuận', 'tăng trưởng']
    negative_words = ['giảm', 'khó khăn', 'suy giảm', 'rủi ro', 'thách thức', 'tiêu cực', 'lỗ', 'sụt giảm']
    
    highlighted = text
    for word in positive_words:
        if word in highlighted.lower():
            highlighted = highlighted.replace(word, f'<span style="color: #2ecc71; font-weight: bold;">{word}</span>')
    for word in negative_words:
        if word in highlighted.lower():
            highlighted = highlighted.replace(word, f'<span style="color: #e74c3c; font-weight: bold;">{word}</span>')
    
    return dcc.Markdown(highlighted, dangerously_allow_html=True)

def extract_keywords(text, top_n=10):
    """Trích xuất từ khóa quan trọng"""
    if not text:
        return []
    
    words = text.split()
    # Filter words longer than 3 characters
    keywords = [word for word in words if len(word) > 3]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Return top keywords with count
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]