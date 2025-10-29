"""
Cấu hình chung cho ứng dụng
"""
import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Logging
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'app.log',
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Model Settings
MODEL_DIR = BASE_DIR / 'models' / 'trained'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_CONFIG = {
    'type': 'naive_bayes',  # 'naive_bayes' hoặc 'phobert'
    'max_features': 5000,
    'ngram_range': (1, 2),
    'min_df': 2
}

# Crawler Settings
CRAWLER_CONFIG = {
    'max_workers': 3,
    'timeout': 60,
    'retry_times': 3,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Dashboard Settings
DASHBOARD_CONFIG = {
    'host': 'localhost',
    'port': 8050,
    'debug': True,
    'title': 'Phân tích tác động tin tức đến cổ phiếu'
}

# Sentiment Labels
SENTIMENT_LABELS = {
    0: 'Tiêu cực',
    1: 'Trung tính',
    2: 'Tích cực'
}

SENTIMENT_COLORS = {
    'Tiêu cực': '#e74c3c',
    'Trung tính': '#95a5a6',
    'Tích cực': '#2ecc71'
}

# Sector Mappings
SECTOR_MAPPINGS = {
    # Mapping cũ (backward compatibility)
    'ngân_hàng': 'Banking',
    'bất_động_sản': 'Real Estate',
    'chứng_khoán': 'Finance',
    'công_nghệ': 'Technology',
    'sản_xuất': 'Manufacturing',
    'năng_lượng': 'Energy',
    'vận_tải': 'Transportation',
    'nông_nghiệp': 'Agriculture',
    'bán_lẻ': 'Retail',
    'tổng_hợp': 'Other',
    
    # Mapping mới (trực tiếp từ preprocessor)
    'Banking': 'Banking',
    'Real Estate': 'Real Estate',
    'Finance': 'Finance',
    'Technology': 'Technology',
    'Manufacturing': 'Manufacturing',
    'Energy': 'Energy',
    'Transportation': 'Transportation',
    'Agriculture': 'Agriculture',
    'Retail': 'Retail',
    'Other': 'Other'
}

# Performance Settings
PERFORMANCE_CONFIG = {
    'cache_timeout': 300,  # 5 minutes
    'max_articles_display': 50,
    'chart_update_interval': 30,  # seconds
    'enable_caching': True
}