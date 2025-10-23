"""
Dashboard chính sử dụng Dash
"""
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from config.settings import DASHBOARD_CONFIG
import logging

logger = logging.getLogger(__name__)

# Khởi tạo app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    title=DASHBOARD_CONFIG['title']
)

# Server cho production
server = app.server

def run_dashboard():
    """Chạy dashboard"""
    logger.info(f"Starting dashboard on {DASHBOARD_CONFIG['host']}:{DASHBOARD_CONFIG['port']}")
    app.run_server(
        host=DASHBOARD_CONFIG['host'],
        port=DASHBOARD_CONFIG['port'],
        debug=DASHBOARD_CONFIG['debug']
    )