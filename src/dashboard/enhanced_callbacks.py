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
    
    # Sentiment Pie Chart
    @app.callback(
        Output('sentiment-pie-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('sector-filter', 'value'),
         Input('time-filter', 'value')]
    )
    def update_sentiment_pie(n, sector, days):
        """Biểu đồ tròn phân bố sentiment"""
        df = get_filtered_data(sector, days, 'all')
        
        if df.empty or 'predicted_sentiment' not in df.columns:
            return go.Figure()
        
        sentiment_counts = df['predicted_sentiment'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            marker=dict(colors=[SENTIMENT_COLORS.get(s, '#95a5a6') for s in sentiment_counts.index]),
            hole=0.4,
            textinfo='label+percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Số lượng: %{value}<br>Tỷ lệ: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        return fig
    
    # Sector Pie Chart
    @app.callback(
        Output('sector-pie-chart', 'figure'),
        [Input('interval-component', 'n_intervals'),
         Input('time-filter', 'value'),
         Input('sentiment-filter', 'value')]
    )
    def update_sector_pie(n, days, sentiment_type):
        """Biểu đồ tròn phân bố theo ngành"""
        df = get_filtered_data('all', days, sentiment_type)
        
        if df.empty or 'sectors' not in df.columns:
            return go.Figure()
        
        sector_counts = df['sectors'].value_counts()
        
        # Màu sắc cho các ngành
        sector_colors = {
            'Banking': '#3498db',
            'Energy': '#f39c12',
            'Real Estate': '#e74c3c',
            'Technology': '#9b59b6',
            'Manufacturing': '#1abc9c',
            'Transportation': '#34495e',
            'Agriculture': '#27ae60',
            'Retail': '#e67e22',
            'Finance': '#2ecc71',
            'Other': '#95a5a6'
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=sector_counts.index,
            values=sector_counts.values,
            marker=dict(colors=[sector_colors.get(s, '#95a5a6') for s in sector_counts.index]),
            hole=0.4,
            textinfo='percent',
            textposition='inside',
            hovertemplate='<b>%{label}</b><br>Số bài viết: %{value}<br>Tỷ lệ: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            showlegend=True,
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=10))
        )
        
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
        """Timeline với đầy đủ các ngày và hover chi tiết"""
        df = get_filtered_data(sector, days, sentiment_type)
        
        if df.empty or 'crawl_time' not in df.columns:
            return go.Figure()
        
        # Ensure crawl_time is datetime
        df['crawl_time'] = pd.to_datetime(df['crawl_time'], errors='coerce')
        df = df[df['crawl_time'].notna()]
        df['date'] = df['crawl_time'].dt.date
        
        # ===== FIX: Xử lý predicted_sentiment NULL =====
        if 'predicted_sentiment' not in df.columns or df['predicted_sentiment'].isna().all():
            logger.warning("⚠️ predicted_sentiment column missing or all NULL, creating from predicted_label")
            
            if 'predicted_label' in df.columns:
                df['predicted_sentiment'] = df['predicted_label'].map({
                    0: 'Tiêu cực',
                    1: 'Trung tính', 
                    2: 'Tích cực'
                })
                logger.info(f"✅ Created predicted_sentiment for {len(df)} records")
            else:
                logger.error("❌ Neither predicted_sentiment nor predicted_label available!")
                return go.Figure()
        
        # ===== FIX: Clean NaN values trong predicted_sentiment =====
        # Convert NaN to proper sentiment based on predicted_label
        mask_null = df['predicted_sentiment'].isna()
        if mask_null.any():
            logger.warning(f"⚠️ Found {mask_null.sum()} NULL predicted_sentiment, fixing...")
            
            if 'predicted_label' in df.columns:
                df.loc[mask_null, 'predicted_sentiment'] = df.loc[mask_null, 'predicted_label'].map({
                    0: 'Tiêu cực',
                    1: 'Trung tính',
                    2: 'Tích cực'
                })
                logger.info(f"✅ Fixed {mask_null.sum()} NULL values")
        
        # Chuẩn hóa sentiment (phần code cũ tiếp tục...)
        df['predicted_sentiment'] = df['predicted_sentiment'].astype(str)
        sentiment_map = {
            'Negative': 'Tiêu cực',
            'Neutral': 'Trung tính', 
            'Positive': 'Tích cực',
            'Tiêu cực': 'Tiêu cực',
            'Trung tính': 'Trung tính',
            'Tích cực': 'Tích cực',
            '0': 'Tiêu cực',
            '1': 'Trung tính',
            '2': 'Tích cực',
            'nan': 'Trung tính'  # ← THÊM mapping cho 'nan' string
        }
        df['predicted_sentiment'] = df['predicted_sentiment'].map(sentiment_map).fillna('Trung tính')
        
        
        # BƯỚC 1: Tạo timeline đầy đủ từ ngày đầu đến ngày cuối
        if len(df) > 0:
            min_date = df['date'].min()
            max_date = df['date'].max()
            
            # Tạo danh sách đầy đủ tất cả các ngày
            all_dates = pd.date_range(start=min_date, end=max_date, freq='D').date
            
            # BƯỚC 2: Đếm số lượng bài viết theo ngày và sentiment
            timeline_data = df.groupby(['date', 'predicted_sentiment']).size().reset_index(name='count')
            
            # BƯỚC 3: Tạo DataFrame đầy đủ với tất cả ngày và tất cả sentiment
            sentiments = ['Tích cực', 'Trung tính', 'Tiêu cực']
            
            # Tạo MultiIndex với tất cả các kết hợp date x sentiment
            full_index = pd.MultiIndex.from_product(
                [all_dates, sentiments],
                names=['date', 'predicted_sentiment']
            )
            
            # Tạo DataFrame đầy đủ
            timeline_full = pd.DataFrame(index=full_index).reset_index()
            
            # BƯỚC 4: Merge với dữ liệu thực tế và điền 0 cho missing values
            timeline_full = timeline_full.merge(
                timeline_data,
                on=['date', 'predicted_sentiment'],
                how='left'
            ).fillna({'count': 0})
            
            # Convert count to int
            timeline_full['count'] = timeline_full['count'].astype(int)
            
            # Convert date to datetime for plotly
            timeline_full['date'] = pd.to_datetime(timeline_full['date'])
            
            logger.info(f"Timeline data shape: {timeline_full.shape}")
            logger.info(f"Date range: {timeline_full['date'].min()} to {timeline_full['date'].max()}")
            logger.info(f"Sample data:\n{timeline_full.head(20)}")
            
        else:
            return go.Figure()
        
        # BƯỚC 5: Vẽ biểu đồ với hover chi tiết
        fig = go.Figure()
        
        for sentiment in sentiments:
            sentiment_data = timeline_full[timeline_full['predicted_sentiment'] == sentiment]
            
            # Tạo hover text chi tiết
            hover_texts = []
            for _, row in sentiment_data.iterrows():
                hover_text = (
                    f"<b>Ngày:</b> {row['date'].strftime('%d/%m/%Y')}<br>"
                    f"<b>Sentiment:</b> {sentiment}<br>"
                    f"<b>Số bài viết:</b> {row['count']}<br>"
                    f"<extra></extra>"
                )
                hover_texts.append(hover_text)
            
            fig.add_trace(go.Scatter(
                x=sentiment_data['date'],
                y=sentiment_data['count'],
                mode='lines+markers',
                name=sentiment,
                line=dict(
                    color=SENTIMENT_COLORS[sentiment],
                    width=2,
                    shape='spline'  # Đường cong mượt hơn
                ),
                marker=dict(
                    size=6,
                    symbol='circle',
                    line=dict(width=1, color='white')
                ),
                hovertemplate='%{text}',
                text=hover_texts,
                connectgaps=False  # Không nối các gap
            ))
        
        # BƯỚC 6: Cấu hình layout
        fig.update_layout(
            xaxis=dict(
                title='Ngày',
                tickformat='%d/%m',
                dtick='D1' if days <= 7 else 'D2' if days <= 30 else 'D7',  # Tự động điều chỉnh tick spacing
                tickangle=-45,
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)'
            ),
            yaxis=dict(
                title='Số lượng bài viết',
                showgrid=True,
                gridcolor='rgba(128, 128, 128, 0.2)',
                zeroline=True
            ),
            hovermode='x unified',  # Hiển thị tất cả values khi hover vào một ngày
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
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
        """Bảng tin tức nâng cao với tương tác - CẢI THIỆN"""
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
            
            # SỬA: Hiển thị content thay vì summary nếu có
            content_text = ''
            if 'content' in row and pd.notna(row['content']) and row['content']:
                content_text = str(row['content'])[:200] + '...'
                content_length = len(str(row['content']))
            elif 'summary' in row and pd.notna(row['summary']):
                content_text = str(row['summary'])[:200] + '...'
                content_length = len(str(row['summary']))
            else:
                content_text = "Không có nội dung"
                content_length = 0
            
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
                            html.Strong(truncated_title),
                            html.Br(),
                            html.Small(content_text, className='text-muted'),
                            html.Br(),
                            html.Small([
                                html.I(className='fas fa-align-left me-1'),
                                f"{content_length} ký tự"
                            ], className='text-info') if content_length > 0 else None
                        ])
                    ]),
                    html.Td(row.get('source', 'N/A')),
                    html.Td([
                        dbc.Badge(sentiment, color=color, className='me-1'),
                        html.Br(),
                        html.Small([
                            html.I(className='fas fa-smile me-1'),
                            f"{row.get('sentiment_positive', 0):.2f}"
                        ], className='text-muted')
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
        """Phân tích URL chi tiết với keyword highlighting - CẢI THIỆN"""
        if not url:
            alert = dbc.Alert("Vui lòng nhập URL", color='warning')
            return alert, alert
        
        try:
            # Parse URL
            result = url_parser.parse_url(url)
            
            if not result['success']:
                error_alert = dbc.Alert(f"Lỗi: {result.get('error', 'Không thể trích xuất nội dung')}", color='danger')
                return error_alert, error_alert

            # Kiểm tra content
            if not result.get('content') or len(result['content']) < 100:
                warning_alert = dbc.Alert(
                    f"⚠️ Nội dung quá ngắn ({len(result.get('content', ''))} ký tự). Kết quả phân tích có thể không chính xác.",
                    color='warning'
                )
            else:
                warning_alert = None
            
            logger.info(f"[URL PARSE] Extracted {len(result['content'])} chars from {url}")

            # Save raw data to news_articles
            raw_data = {
                'source': result['source'],
                'title': result['title'],
                'summary': result.get('summary', result['content'][:200]),
                'content': result['content'],  # THÊM: Lưu full content
                'link': url,
                'crawl_time': datetime.now()
            }
            df_raw = pd.DataFrame([raw_data])
            db_manager.save_news_data(df_raw)
            
            # Preprocess - SỬA: Sử dụng full content
            full_text = f"{result['title']} {result['content']}"
            processed = preprocessor.preprocess_pipeline(full_text)
            
            logger.info(f"[PREPROCESS] Cleaned text: {len(processed['cleaned_text'])} chars")
            logger.info(f"[PREPROCESS] Detected sectors: {processed['sectors']}")
            
            # Analyze sentiment
            sentiment = sentiment_analyzer.analyze(full_text)
            sentiment_label = SENTIMENT_LABELS[sentiment['label']]
            
            logger.info(f"[SENTIMENT] Label: {sentiment_label} | Scores: {sentiment}")
            
            # Extract keywords
            keywords = extract_keywords(processed['cleaned_text'])
            
            # Save processed data
            processed_data = {
                'source': result['source'],
                'title': result['title'],
                'content': result['content'],
                'summary': result.get('summary', result['content'][:500]),
                'link': url,
                'crawl_time': datetime.now(),
                'cleaned_text': processed['cleaned_text'],
                'sentiment_positive': float(sentiment['positive']),
                'sentiment_negative': float(sentiment['negative']),
                'sentiment_neutral': float(sentiment['neutral']),
                'predicted_label': sentiment['label'],
                'predicted_sentiment': sentiment_label,  # ← ĐÃ CÓ DÒNG NÀY
                'sectors': ','.join(processed['sectors']) if processed['sectors'] else 'Other',
                'processed_at': datetime.now()
            }
            df_processed = pd.DataFrame([processed_data])
            db_manager.save_processed_data(df_processed)

            # Save prediction data
            prediction_data = {
                'article_id': url,
                'predicted_label': sentiment['label'],
                'predicted_sentiment': sentiment_label,
                'confidence_scores': {
                    'positive': float(sentiment['positive']),
                    'negative': float(sentiment['negative']),
                    'neutral': float(sentiment['neutral'])
                },
                'model_version': '1.0',
                'predicted_at': datetime.now()
            }
            db_manager.save_predictions(prediction_data)
            
            # Basic result
            basic_result = dbc.Alert([
                html.H5(f"✓ Phân tích thành công!", className='mb-2'),
                html.P([
                    html.Strong("Sentiment: "),
                    dbc.Badge(sentiment_label, color='success' if sentiment['label']==2 else 'danger' if sentiment['label']==0 else 'secondary'),
                    html.Br(),
                    html.Small(f"Phân tích từ {len(result['content'])} ký tự nội dung", className='text-muted')
                ])
            ], color='success')
            
            # Detailed result
            sentiment_color_map = {'Tích cực': 'success', 'Trung tính': 'secondary', 'Tiêu cực': 'danger'}
            color = sentiment_color_map.get(sentiment_label, 'secondary')
            
            detailed_result = dbc.Card([
                dbc.CardHeader([
                    html.H4("📊 Phân tích chi tiết bài viết", className="mb-0")
                ]),
                dbc.CardBody([
                    # Warning nếu content ngắn
                    warning_alert if warning_alert else None,
                    
                    dbc.Row([
                        dbc.Col([
                            html.H5([html.I(className='fas fa-newspaper me-2'), "Thông tin bài viết"]),
                            html.P([html.Strong("Tiêu đề: "), result['title']]),
                            html.P([html.Strong("Nguồn: "), result['source']]),
                            html.P([html.Strong("Ngày: "), datetime.now().strftime('%d/%m/%Y %H:%M')]),
                            html.P([
                                html.Strong("Độ dài: "), 
                                f"{len(result['content'])} ký tự",
                                html.Span(" ✓", className='text-success') if len(result['content']) > 300 else html.Span(" ⚠️", className='text-warning')
                            ]),
                            html.Hr(),
                            html.H5([html.I(className='fas fa-chart-line me-2'), "Phân tích Sentiment"]),
                            dbc.Badge(sentiment_label, color=color, className='fs-6 mb-3'),
                            html.Div([
                                html.P(f"Tích cực: {sentiment['positive']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['positive']*100, color='success', className='mb-2'),
                                html.P(f"Trung tính: {sentiment['neutral']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['neutral']*100, color='secondary', className='mb-2'),
                                html.P(f"Tiêu cực: {sentiment['negative']:.2f}", className='mb-1'),
                                dbc.Progress(value=sentiment['negative']*100, color='danger')
                            ], className='mb-3'),
                            html.Hr(),
                            html.H5([html.I(className='fas fa-industry me-2'), "Ngành nghề"]),
                            html.Div([
                                dbc.Badge(sector, color='primary', className='me-1 mb-1') 
                                for sector in processed['sectors']
                            ])
                        ], width=6),
                        dbc.Col([
                            html.H5([html.I(className='fas fa-file-alt me-2'), "Tóm tắt nội dung"]),
                            html.Div([
                                html.P(result['content'][:600] + '...' if len(result['content']) > 600 else result['content'],
                                    style={'maxHeight': '200px', 'overflowY': 'auto', 'fontSize': '0.9rem'})
                            ], className='p-2 bg-light rounded'),
                            html.Hr(),
                            html.H5([html.I(className='fas fa-key me-2'), "Từ khóa quan trọng"]),
                            html.Div([
                                dbc.Badge(f"{keyword[0]} ({keyword[1]})", color='info', className='me-1 mb-1') 
                                for keyword in keywords[:15]
                            ]),
                            html.Hr(),
                            html.H5([html.I(className='fas fa-link me-2'), "Liên kết"]),
                            html.A([
                                html.I(className='fas fa-external-link-alt me-2'),
                                "Xem bài gốc"
                            ], href=url, target="_blank", className="btn btn-outline-primary")
                        ], width=6)
                    ])
                ])
            ], className='mt-3')
            
            return basic_result, detailed_result
            
        except Exception as e:
            logger.error(f"Error in URL analysis: {str(e)}", exc_info=True)
            error_alert = dbc.Alert(f"Lỗi xử lý: {str(e)}", color='danger')
            return error_alert, error_alert
    
@cache_result(timeout=PERFORMANCE_CONFIG['cache_timeout'])
def get_filtered_data(sector='all', days=30, sentiment_type='all', limit=1000):
    """Lấy dữ liệu đã lọc theo các tiêu chí với cache - CẢI THIỆN"""
    # Try cache first
    cache_key = f"filtered_data_{sector}_{days}_{sentiment_type}_{limit}"
    cached_result = dashboard_cache.get(cache_key)
    if cached_result is not None:
        logger.info(f"Cache hit for: {cache_key}")
        return cached_result
    
    logger.info(f"Loading data with filters: sector={sector}, days={days}, sentiment={sentiment_type}")
    
    df = db_manager.load_processed_data(limit=limit)
    
    if df.empty:
        logger.warning("No data loaded from database")
        return df
    
    logger.info(f"Loaded {len(df)} records from database")
    logger.info(f"Columns available: {df.columns.tolist()}")
    
    # Optimize DataFrame
    df = optimize_dataframe(df)
    
    # BƯỚC 1: Đảm bảo có cột predicted_sentiment và chuẩn hóa sang tiếng Việt
    if 'predicted_sentiment' not in df.columns:
        if 'predicted_label' in df.columns:
            df['predicted_sentiment'] = df['predicted_label'].map({
                0: 'Tiêu cực', 
                1: 'Trung tính', 
                2: 'Tích cực'
            })
            logger.info("Created predicted_sentiment from predicted_label")
        else:
            logger.warning("Neither predicted_sentiment nor predicted_label found in data")
            df['predicted_sentiment'] = 'Trung tính'
    else:
        # Convert to string first to avoid Categorical issues
        df['predicted_sentiment'] = df['predicted_sentiment'].astype(str)
        sentiment_map = {
            'Negative': 'Tiêu cực',
            'Neutral': 'Trung tính', 
            'Positive': 'Tích cực',
            'Tiêu cực': 'Tiêu cực',
            'Trung tính': 'Trung tính',
            'Tích cực': 'Tích cực'
        }
        df['predicted_sentiment'] = df['predicted_sentiment'].map(sentiment_map).fillna('Trung tính')
        logger.info(f"Normalized predicted_sentiment. Unique values: {df['predicted_sentiment'].unique().tolist()}")
    
    # BƯỚC 2: Xử lý cột sectors
    if 'sectors' not in df.columns:
        logger.warning("No sectors column found, creating default")
        df['sectors'] = 'Other'
    else:
        def normalize_sector(sector_value):
            """Chuẩn hóa giá trị sector - CẢI THIỆN"""
            try:
                # Xử lý giá trị rỗng
                if pd.isna(sector_value) or sector_value == '' or sector_value == 'nan':
                    return 'Other'
                
                # Convert to string
                sector_str = str(sector_value).strip()
                
                # Nếu là chuỗi rỗng sau khi strip
                if not sector_str or sector_str == 'nan':
                    return 'Other'
                
                # THÊM: Mapping tiếng Việt -> tiếng Anh
                vn_to_en_map = {
                    'bất_động_sản': 'Real Estate',
                    'ngân_hàng': 'Banking',
                    'chứng_khoán': 'Finance',
                    'công_nghệ': 'Technology',
                    'sản_xuất': 'Manufacturing',
                    'năng_lượng': 'Energy',
                    'vận_tải': 'Transportation',
                    'nông_nghiệp': 'Agriculture',
                    'bán_lẻ': 'Retail',
                    'tổng_hợp': 'Other'
                }
                
                # Nếu chứa dấu phẩy (comma-separated), lấy ngành đầu tiên
                if ',' in sector_str:
                    sectors_list = [s.strip() for s in sector_str.split(',')]
                    main_sector = sectors_list[0] if sectors_list else 'Other'
                else:
                    main_sector = sector_str
                
                # Mapping tiếng Việt sang tiếng Anh
                if main_sector in vn_to_en_map:
                    main_sector = vn_to_en_map[main_sector]
                
                # Mapping thêm từ SECTOR_MAPPINGS
                mapped_sector = SECTOR_MAPPINGS.get(main_sector, main_sector)
                
                # Kiểm tra mapped_sector có hợp lệ không
                valid_sectors = ['Banking', 'Real Estate', 'Finance', 'Technology', 
                            'Manufacturing', 'Energy', 'Transportation', 
                            'Agriculture', 'Retail', 'Other']
                
                if mapped_sector in valid_sectors:
                    return mapped_sector
                else:
                    return 'Other'
                    
            except Exception as e:
                logger.error(f"Error normalizing sector '{sector_value}': {e}")
                return 'Other'
            
        df['sectors'] = df['sectors'].apply(normalize_sector)
        logger.info(f"Normalized sectors. Unique values: {df['sectors'].unique().tolist()}")
    
    # BƯỚC 3: Filter by time
    if 'crawl_time' in df.columns:
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            df['crawl_time'] = pd.to_datetime(df['crawl_time'], errors='coerce')
            # Loại bỏ các giá trị NaT (Not a Time)
            df = df[df['crawl_time'].notna()]
            df = df[df['crawl_time'] >= cutoff_date]
            logger.info(f"After time filter: {len(df)} records (from {cutoff_date} to now)")
        except Exception as e:
            logger.error(f"Error filtering by time: {e}")
    
    # BƯỚC 4: Filter by sector
    if sector != 'all':
        before_count = len(df)
        df = df[df['sectors'] == sector]
        logger.info(f"Sector filter '{sector}': {before_count} -> {len(df)} records")
    
    # BƯỚC 5: Filter by sentiment (chuẩn hóa tiếng Việt)
    if sentiment_type != 'all':
        before_count = len(df)
        # Đảm bảo sentiment_type là tiếng Việt
        sentiment_map = {
            'Negative': 'Tiêu cực',
            'Neutral': 'Trung tính', 
            'Positive': 'Tích cực',
            'Tiêu cực': 'Tiêu cực',
            'Trung tính': 'Trung tính',
            'Tích cực': 'Tích cực'
        }
        normalized_sentiment = sentiment_map.get(sentiment_type, sentiment_type)
        df = df[df['predicted_sentiment'] == normalized_sentiment]
        logger.info(f"Sentiment filter '{sentiment_type}' (normalized: '{normalized_sentiment}'): {before_count} -> {len(df)} records")
    
    logger.info(f"Final filtered data: {len(df)} records")
    
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


    