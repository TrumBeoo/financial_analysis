"""
File chính chạy ứng dụng
"""
import logging
import logging.config
from config.settings import LOG_CONFIG
from src.dashboard.app import app
from src.dashboard.layouts import create_dashboard_layout, create_url_analysis_layout
from src.dashboard.enhanced_callbacks import register_enhanced_callbacks
from dash import dcc, html
from dash.dependencies import Input, Output

from src.dashboard.layouts import create_crawler_management_layout
from src.dashboard.crawler_callbacks import register_crawler_callbacks

# Đăng ký callback cho crawler
register_crawler_callbacks(app)

# Setup logging
logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)

# Register enhanced callbacks
register_enhanced_callbacks(app)

# Layout chính với routing
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Router cho các trang"""
    if pathname == '/url-analysis':
        return create_url_analysis_layout()
    elif pathname == '/crawler':  # ← Thêm route mới
        return create_crawler_management_layout()
    else:
        return create_dashboard_layout()
if __name__ == '__main__':
    logger.info("Starting Financial News Analysis Application...")
    
    # Chạy dashboard
    from src.dashboard.app import run_dashboard
    run_dashboard()