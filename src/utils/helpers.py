"""
Các hàm tiện ích
"""
import re
from datetime import datetime
import hashlib

def clean_text(text):
    """Làm sạch văn bản"""
    if not isinstance(text, str):
        return ""
    
    # Loại bỏ HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Loại bỏ URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Loại bỏ email
    text = re.sub(r'\S+@\S+', '', text)
    
    # Loại bỏ ký tự đặc biệt
    text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)
    
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def generate_hash(text):
    """Tạo hash từ text để check duplicate"""
    return hashlib.md5(text.encode()).hexdigest()

def format_date(date_obj):
    """Format datetime object"""
    if isinstance(date_obj, str):
        return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    return str(date_obj)

def truncate_text(text, length=100):
    """Cắt ngắn text"""
    if not text or len(text) <= length:
        return text
    
    return text[:length] + '...'

def get_domain_from_url(url):
    """Lấy domain từ URL"""
    from urllib.parse import urlparse
    
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return url

def calculate_sentiment_score(positive, negative, neutral):
    """Tính điểm sentiment tổng hợp"""
    total = positive + negative + neutral
    
    if total == 0:
        return 0
    
    # Điểm từ -100 đến 100
    score = ((positive - negative) / total) * 100
    
    return round(score, 2)