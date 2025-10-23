"""
Callbacks cho Dashboard
"""
from dash import Output, Input, State, html
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import logging
from dash import Input, Output, State, html
import dash_bootstrap_components as dbc

from src.services.data_service import DataService
from config.settings import SENTIMENT_COLORS, SENTIMENT_LABELS

logger = logging.getLogger(__name__)

# Khởi tạo service
data_service = DataService()

def register_callbacks(app):
    """Đăng ký tất cả callbacks"""
    
    @app.callback(
        [Output('total-articles', 'children'),
         Output('positive-count', 'children'),
         Output('neutral-count', 'children'),
         Output('negative-count', 'children')],
        Input('interval-component', 'n_intervals')
    )
    def update_stats(n):
        """Cập nhật thống kê"""
        stats = data_service.get_stats()
        return str(stats['total']), str(stats['positive']), str(stats['neutral']), str(stats['negative'])
    
    @app.callback(
        Output('sentiment-pie-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_pie_chart(n):
        """Cập nhật biểu đồ tròn sentiment"""
        df = data_service.get_dashboard_data(limit=1000)
        
        if df.empty:
            return go.Figure()
        
        # Kiểm tra cột sentiment có sẵn
        sentiment_col = None
        if 'predicted_sentiment' in df.columns:
            sentiment_col = 'predicted_sentiment'
        elif 'predicted_label' in df.columns:
            # Chuyển đổi label thành sentiment
            df['predicted_sentiment'] = df['predicted_label'].map({0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'})
            sentiment_col = 'predicted_sentiment'
        
        if sentiment_col is None:
            return go.Figure()
        
        sentiment_counts = df[sentiment_col].value_counts()
        
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title='',
            color=sentiment_counts.index,
            color_discrete_map=SENTIMENT_COLORS
        )
        
        fig.update_traces(textinfo='percent+label')
        
        return fig
    
    @app.callback(
        Output('sector-bar-chart', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_sector_chart(n):
        """Cập nhật biểu đồ ngành"""
        df = data_service.get_dashboard_data(limit=1000)
        
        if df.empty:
            return go.Figure()
        
        # Kiểm tra cột sentiment
        if 'predicted_sentiment' not in df.columns:
            if 'predicted_label' in df.columns:
                df['predicted_sentiment'] = df['predicted_label'].map({0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'})
            else:
                return go.Figure()
        
        # Kiểm tra cột sectors
        if 'sectors' not in df.columns:
            df['sectors'] = 'Khác'
        
        # Phân tích theo ngành
        sector_sentiment = df.groupby(['sectors', 'predicted_sentiment']).size().unstack(fill_value=0)
        
        fig = go.Figure()
        
        for sentiment in ['Tiêu cực', 'Trung tính', 'Tích cực']:
            if sentiment in sector_sentiment.columns:
                fig.add_trace(go.Bar(
                    name=sentiment,
                    x=sector_sentiment.index,
                    y=sector_sentiment[sentiment],
                    marker_color=SENTIMENT_COLORS[sentiment]
                ))
        
        fig.update_layout(
            barmode='stack',
            xaxis_title='Ngành',
            yaxis_title='Số lượng bài viết',
            hovermode='x unified'
        )
        
        return fig
    
    @app.callback(
        Output('sentiment-timeline', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_timeline(n):
        """Cập nhật timeline"""
        df = data_service.get_dashboard_data(limit=1000)
        
        if df.empty:
            return go.Figure()
        
        # Kiểm tra cột sentiment
        if 'predicted_sentiment' not in df.columns:
            if 'predicted_label' in df.columns:
                df['predicted_sentiment'] = df['predicted_label'].map({0: 'Tiêu cực', 1: 'Trung tính', 2: 'Tích cực'})
            else:
                return go.Figure()
        
        # Chuyển đổi cột thời gian
        if 'crawl_time' in df.columns:
            df['date'] = pd.to_datetime(df['crawl_time']).dt.date
        elif 'processed_at' in df.columns:
            df['date'] = pd.to_datetime(df['processed_at']).dt.date
        else:
            return go.Figure()
        
        # Đếm theo ngày và sentiment
        timeline_data = df.groupby(['date', 'predicted_sentiment']).size().reset_index(name='count')
        
        fig = px.line(
            timeline_data,
            x='date',
            y='count',
            color='predicted_sentiment',
            color_discrete_map=SENTIMENT_COLORS,
            title=''
        )
        
        fig.update_layout(
            xaxis_title='Ngày',
            yaxis_title='Số lượng bài viết',
            hovermode='x unified'
        )
        
        return fig
    
    @app.callback(
        Output('recent-news-table', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_news_table(n):
        """Cập nhật bảng tin tức"""
        df = data_service.get_dashboard_data(limit=20)
        
        if df.empty:
            return html.P("Chưa có dữ liệu", className='text-muted text-center')
        
        # Tạo bảng
        rows = []
        for idx, row in df.iterrows():
            sentiment = row.get('predicted_sentiment', 'N/A')
            color = SENTIMENT_COLORS.get(sentiment, 'secondary')
            
            rows.append(
                html.Tr([
                    html.Td(row.get('title', 'N/A')[:100] + '...'),
                    html.Td(row.get('source', 'N/A')),
                    html.Td(
                        dbc.Badge(sentiment, color=color.replace('#', ''), className='me-1')
                    ),
                    html.Td(row.get('sectors', 'N/A')),
                ])
            )
        
        table = dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Tiêu đề"),
                    html.Th("Nguồn"),
                    html.Th("Sentiment"),
                    html.Th("Ngành"),
                ])
            ),
            html.Tbody(rows)
        ], bordered=True, hover=True, responsive=True, striped=True, color='light')
        
        return table
    
    @app.callback(
        [Output('url-analysis-result', 'children'),
         Output('save-status', 'children', allow_duplicate=True)],
        Input('analyze-btn', 'n_clicks'),
        State('url-input', 'value'),
        prevent_initial_call=True
    )
    def analyze_url(n_clicks, url):
        """Phân tích URL - chỉ hiển thị kết quả"""
        if not url:
            return dbc.Alert("Vui lòng nhập URL", color='warning'), ""
        
        # Phân tích URL
        analysis_result = data_service.analyze_url(url)
        
        if not analysis_result['success']:
            return dbc.Alert(f"Lỗi: {analysis_result['error']}", color='danger'), ""
        
        data = analysis_result['data']
        sentiment = data['sentiment']
        
        # Hiển thị kết quả
        result_card = dbc.Card([
            dbc.CardHeader([
                html.H5(data['title']),
                dbc.Badge(sentiment['label'], color=SENTIMENT_COLORS[sentiment['label']].replace('#', ''), className='ms-2')
            ]),
            dbc.CardBody([
                html.P(data['content'][:300] + '...'),
                html.Hr(),
                dbc.Row([
                    dbc.Col([
                        html.Strong("Nguồn: "),
                        html.Span(data['source'])
                    ], width=4),
                    dbc.Col([
                        html.Strong("Ngành: "),
                        html.Span(', '.join(data['sectors']))
                    ], width=4),
                    dbc.Col([
                        html.Strong("Sentiment Score: "),
                        html.Span(f"Tích cực: {sentiment['scores']['positive']:.2f}, Tiêu cực: {sentiment['scores']['negative']:.2f}")
                    ], width=4)
                ])
            ])
        ], className='mt-3', color='light')
        
        return result_card, ""
    
    @app.callback(
        Output('save-status', 'children'),
        Input('save-btn', 'n_clicks'),
        State('url-input', 'value'),
        prevent_initial_call=True
    )
    def save_analysis(n_clicks, url):
        """Lưu kết quả phân tích - tách biệt khỏi hiển thị"""
        if not url:
            return dbc.Alert("Không có dữ liệu để lưu", color='warning', dismissable=True)
        
        # Phân tích lại để lưu
        analysis_result = data_service.analyze_url(url)
        
        if not analysis_result['success']:
            return dbc.Alert(f"Lỗi phân tích: {analysis_result['error']}", color='danger', dismissable=True)
        
        # Lưu vào database
        save_success = data_service.save_analysis_result(analysis_result)
        
        if save_success:
            return dbc.Alert("✅ Đã lưu thành công!", color='success', dismissable=True)
        else:
            return dbc.Alert("❌ Lỗi lưu dữ liệu", color='danger', dismissable=True)