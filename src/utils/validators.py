"""
Validators cho dữ liệu đầu vào
"""
import re
from urllib.parse import urlparse

class InputValidator:
    """Validate các input từ user"""
    
    @staticmethod
    def validate_url(url):
        """Kiểm tra URL hợp lệ"""
        if not url or not isinstance(url, str):
            return False, "URL không hợp lệ"
        
        # Check format cơ bản
        url_pattern = re.compile(
            r'^https?://'  # http:// hoặc https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "URL không đúng định dạng"
        
        # Check domain có hợp lệ
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "URL thiếu scheme hoặc domain"
        except:
            return False, "URL không thể parse"
        
        return True, "OK"
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """Kiểm tra khoảng thời gian hợp lệ"""
        from datetime import datetime
        
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            if start_date > end_date:
                return False, "Ngày bắt đầu phải trước ngày kết thúc"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Lỗi định dạng ngày: {e}"
    
    @staticmethod
    def validate_keyword(keyword):
        """Kiểm tra từ khóa tìm kiếm"""
        if not keyword or not isinstance(keyword, str):
            return False, "Từ khóa không hợp lệ"
        
        keyword = keyword.strip()
        
        if len(keyword) < 2:
            return False, "Từ khóa quá ngắn (tối thiểu 2 ký tự)"
        
        if len(keyword) > 100:
            return False, "Từ khóa quá dài (tối đa 100 ký tự)"
        
        return True, "OK"