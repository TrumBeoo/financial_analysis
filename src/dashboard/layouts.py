"""
Layouts cho Dashboard
"""
from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_navbar():
    """Tạo navigation bar"""
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Phân tích", href="/url-analysis", active="exact")),
        ],
        brand="Phân tích tác động tin tức đến cổ phiếu theo ngành",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-3"
    )

def create_sidebar():
    """Tạo sidebar với filters"""
    return dbc.Card([
        dbc.CardHeader(html.H5("Bộ lọc", className="mb-0")),
        dbc.CardBody([
            # Sector Filter
            html.Div([
                html.Label("Ngành:", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='sector-filter',
                    options=[
                        {'label': 'Tất cả', 'value': 'all'},
                        {'label': 'Ngân hàng', 'value': 'Banking'},
                        {'label': 'Năng lượng', 'value': 'Energy'},
                        {'label': 'Bất động sản', 'value': 'Real Estate'},
                        {'label': 'Công nghệ', 'value': 'Technology'},
                        {'label': 'Sản xuất', 'value': 'Manufacturing'},
                        {'label': 'Khác', 'value': 'Other'}
                    ],
                    value='all',
                    className="mb-3"
                )
            ]),
            
            # Time Range Filter
            html.Div([
                html.Label("Khoảng thời gian:", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='time-filter',
                    options=[
                        {'label': '7 ngày', 'value': 7},
                        {'label': '30 ngày', 'value': 30},
                        {'label': '90 ngày', 'value': 90}
                    ],
                    value=30,
                    className="mb-3"
                )
            ]),
            
            # Sentiment Filter
            html.Div([
                html.Label("Loại tin:", className="fw-bold mb-2"),
                dcc.Dropdown(
                    id='sentiment-filter',
                    options=[
                        {'label': 'Tất cả', 'value': 'all'},
                        {'label': 'Tích cực', 'value': 'Tích cực'},
                        {'label': 'Trung tính', 'value': 'Trung tính'},
                        {'label': 'Tiêu cực', 'value': 'Tiêu cực'}
                    ],
                    value='all',
                    className="mb-3"
                )
            ]),
            
            dbc.Button("Làm mới", id='refresh-btn', color='success', className="w-100")
        ])
    ], className="h-100")

def create_url_input_section():
    """Section nhập URL"""
    return dbc.Card([
        dbc.CardHeader(html.H4("Phân tích tin tức từ URL")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Input(
                        id='url-input',
                        type='url',
                        placeholder='Nhập URL tin tức (VD: https://cafef.vn/...)',
                        className='mb-2'
                    ),
                ], width=9),
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button(
                            "Phân tích",
                            id='analyze-btn',
                            color='primary'
                        ),
                        dbc.Button(
                            "Lưu",
                            id='save-btn',
                            color='success'
                        )
                    ], className='w-100')
                ], width=3)
            ]),
            html.Div(id='save-status', className='mt-2'),
            html.Div(id='url-analysis-result', className='mt-3')
        ])
    ], className='mb-4')

def create_stats_cards():
    """Thẻ thống kê với Market Sentiment Index"""
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id='total-articles', className='text-center'),
                    html.P("Tổng bài viết", className='text-center text-muted')
                ])
            ], color='info', outline=True)
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id='positive-count', className='text-center text-success'),
                    html.P("Tích cực", className='text-center text-muted')
                ])
            ], color='success', outline=True)
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id='neutral-count', className='text-center text-secondary'),
                    html.P("Trung tính", className='text-center text-muted')
                ])
            ], color='secondary', outline=True)
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("0", id='negative-count', className='text-center text-danger'),
                    html.P("Tiêu cực", className='text-center text-muted')
                ])
            ], color='danger', outline=True)
        ], width=2),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4("+0.00", id='market-sentiment-index', className='text-center'),
                    html.P("Market Sentiment Index", className='text-center text-muted')
                ])
            ], color='warning', outline=True)
        ], width=4),
    ], className='mb-4')

def create_dashboard_layout():
    """Layout trang Dashboard với sidebar"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            dbc.Row([
                # Sidebar
                dbc.Col([
                    create_sidebar()
                ], width=3),
                
                # Main content
                dbc.Col([
                    # Stats cards
                    create_stats_cards(),
                    
                    # Market Overview
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Tổng quan cảm xúc thị trường"),
                                dbc.CardBody([
                                    dcc.Graph(id='sentiment-gauge-chart')
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Bản đồ nhiệt theo ngành"),
                                dbc.CardBody([
                                    dcc.Graph(id='sector-heatmap')
                                ])
                            ])
                        ], width=6),
                    ], className='mb-4'),
                    
                    # Sector Analysis
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(" Phân tích theo ngành"),
                                dbc.CardBody([
                                    dcc.Graph(id='sector-bar-chart')
                                ])
                            ])
                        ], width=8),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Từ khóa nổi bật"),
                                dbc.CardBody([
                                    html.Div(id='word-cloud-display')
                                ])
                            ])
                        ], width=4),
                    ], className='mb-4'),
                    
                    # Timeline & Correlation
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("⏱ Timeline Sentiment"),
                                dbc.CardBody([
                                    dcc.Graph(id='sentiment-timeline')
                                ])
                            ])
                        ], width=8),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(" Tương quan Sentiment-Giá"),
                                dbc.CardBody([
                                    dcc.Graph(id='correlation-chart')
                                ])
                            ])
                        ], width=4),
                    ], className='mb-4'),
                    
                    # Enhanced news table
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(" Tin tức & đánh giá tự động"),
                                dbc.CardBody([
                                    html.Div(id='enhanced-news-table')
                                ])
                            ])
                        ], width=12)
                    ])
                ], width=9)
            ])
        ], fluid=True),
        
        # Auto refresh
        dcc.Interval(
            id='interval-component',
            interval=30*1000,
            n_intervals=0
        ),
        
        # Modal for article details
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Chi tiết bài viết")),
            dbc.ModalBody(id='article-modal-body'),
            dbc.ModalFooter(
                dbc.Button("Đóng", id='close-modal', className="ms-auto", n_clicks=0)
            ),
        ], id='article-modal', is_open=False, size='lg')
    ])

def create_url_analysis_layout():
    """Layout trang phân tích URL với chi tiết"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            create_url_input_section(),
            
            # Enhanced analysis result
            html.Div(id='detailed-url-analysis')
        ], fluid=True)
    ])