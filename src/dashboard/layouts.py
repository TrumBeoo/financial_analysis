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
            dbc.NavItem(dbc.NavLink("Phân tích URL", href="/url-analysis", active="exact")),
            dbc.NavItem(dbc.NavLink("Thu thập dữ liệu", href="/crawler", active="exact")),  # ← Thêm
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


def create_crawler_management_layout():
    """Layout quản lý crawler"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H2("Thu thập dữ liệu tự động"),
                    
                ])
            ], className="mb-4"),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Cấu hình Crawl"),
                        dbc.CardBody([
                            # Chọn nguồn
                            html.Label("Chọn nguồn tin:", className="fw-bold mb-2"),
                            dcc.Checklist(
                                id='crawler-sources',
                                options=[
                                    {'label': ' CafeF', 'value': 'cafef'},
                                    {'label': ' VnEconomy', 'value': 'vneconomy'},
                                    {'label': ' VietStock', 'value': 'vietstock'},
                                    {'label': ' VNExpress', 'value': 'vnexpress'},
                                    {'label': ' Thanh Niên', 'value': 'thanhnien'},
                                    {'label': ' Tuổi Trẻ', 'value': 'tuoitre'},
                                    {'label': ' Dân Trí', 'value': 'dantri'},
                                    {'label': ' NDH', 'value': 'ndh'},
                                ],
                                value=['cafef', 'vnexpress'],
                                inline=False,
                                className="mb-3"
                            ),
                            
                            # Max workers
                            html.Label("Số luồng crawl:", className="fw-bold mb-2"),
                            dcc.Slider(
                                id='max-workers',
                                min=1, max=5, value=3,
                                marks={i: str(i) for i in range(1, 6)},
                                className="mb-3"
                            ),
                            
                            html.Hr(),
                            
                            # Buttons
                            dbc.ButtonGroup([
                                dbc.Button(
                                    "Bắt đầu Crawl",
                                    id='start-crawl-btn',
                                    color='success',
                                    size='lg'
                                ),
                                dbc.Button(
                                    "Dừng",
                                    id='stop-crawl-btn',
                                    color='danger',
                                    size='lg',
                                    disabled=True
                                ),
                            ], className='w-100 mb-3'),
                            
                            # Auto crawl schedule
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("Crawl tự động"),
                                    dbc.Checklist(
                                        id='auto-crawl-toggle',
                                        options=[{'label': ' Bật crawl định kỳ', 'value': 'enabled'}],
                                        value=[]
                                    ),
                                    dcc.Dropdown(
                                        id='crawl-interval',
                                        options=[
                                            {'label': 'Mỗi 30 phút', 'value': 30},
                                            {'label': 'Mỗi 1 giờ', 'value': 60},
                                            {'label': 'Mỗi 3 giờ', 'value': 180},
                                            {'label': 'Mỗi 6 giờ', 'value': 360},
                                        ],
                                        value=60,
                                        disabled=True
                                    )
                                ])
                            ], color='light', className='mt-2')
                        ])
                    ])
                ], width=4),
                
                # Status & Progress
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Trạng thái Crawl"),
                        dbc.CardBody([
                            html.Div(id='crawl-status', children=[
                                dbc.Alert("Chưa bắt đầu crawl", color='secondary')
                            ]),
                            
                            html.Hr(),
                            
                            # Progress bar
                            html.H6("Tiến độ:"),
                            dbc.Progress(
                                id='crawl-progress',
                                value=0,
                                striped=True,
                                animated=True,
                                className='mb-3'
                            ),
                            
                            # Stats
                            html.Div(id='crawl-stats', children=[
                                dbc.Row([
                                    dbc.Col([
                                        html.H4("0", id='crawled-count'),
                                        html.P("Đã crawl", className="text-muted")
                                    ]),
                                    dbc.Col([
                                        html.H4("0", id='processed-count'),
                                        html.P("Đã xử lý", className="text-muted")
                                    ]),
                                    dbc.Col([
                                        html.H4("0", id='error-count'),
                                        html.P("Lỗi", className="text-muted")
                                    ])
                                ])
                            ])
                        ])
                    ]),
                    
                    # Recent crawled articles
                    dbc.Card([
                        dbc.CardHeader("Bài viết mới crawl"),
                        dbc.CardBody([
                            html.Div(id='recent-crawled-articles', 
                                    style={'maxHeight': '400px', 'overflowY': 'auto'})
                        ])
                    ], className='mt-3')
                ], width=8)
            ])
        ], fluid=True),
        
        # Hidden interval for progress update
        dcc.Interval(id='crawl-progress-interval', interval=2000, disabled=True),
        
        # Store crawl state
        dcc.Store(id='crawl-state', data={'running': False})
    ])



def create_dashboard_layout():
    """Layout trang Dashboard với sidebar"""
    return html.Div([
        create_navbar(),
        dbc.Container([
            # Database Stats Card - OPTION 4
            
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
                    
                    # Pie Charts Row
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Phân bố Sentiment"),
                                dbc.CardBody([
                                    dcc.Graph(id='sentiment-pie-chart')
                                ])
                            ])
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Phân bố theo Ngành"),
                                dbc.CardBody([
                                    dcc.Graph(id='sector-pie-chart')
                                ])
                            ])
                        ], width=6),
                    ], className='mb-4'),
                    
                    # Sector Analysis
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Phân tích theo ngành"),
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
                                dbc.CardHeader("Timeline Sentiment"),
                                dbc.CardBody([
                                    dcc.Graph(id='sentiment-timeline')
                                ])
                            ])
                        ], width=8),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("Tương quan Sentiment-Giá"),
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
                                dbc.CardHeader("Tin tức & đánh giá tự động"),
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