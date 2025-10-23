# file: text_preprocessing.py

import re
import string
from underthesea import word_tokenize, pos_tag, ner
from pyvi import ViTokenizer
import numpy as np

class VietnameseTextPreprocessor:
    """
    Xử lý văn bản tiếng Việt cho phân tích tài chính
    """
    
    def __init__(self):
        # Từ điển từ vựng tài chính
        self.financial_terms = {
            'tích_cực': ['tăng trưởng', 'lợi nhuận', 'tăng', 'đột phá', 'thành công', 
                        'phát triển', 'cải thiện', 'khả quan', 'tốt', 'cao'],
            'tiêu_cực': ['giảm', 'lỗ', 'sụt giảm', 'thua lỗ', 'khó khăn', 
                        'thách thức', 'rủi ro', 'suy giảm', 'tệ', 'thấp'],
            'trung_tính': ['ổn định', 'duy trì', 'giữ nguyên', 'không đổi', 'bình thường']
        }
        
        # Các ngành quan trọng trên thị trường chứng khoán VN
        self.sectors = {
            'ngân_hàng': ['ngân hàng', 'bank', 'tín dụng', 'cho vay', 'huy động'],
            'bất_động_sản': ['bất động sản', 'nhà đất', 'căn hộ', 'dự án', 'khu đô thị'],
            'chứng_khoán': ['chứng khoán', 'cổ phiếu', 'trái phiếu', 'đầu tư', 'niêm yết'],
            'bán_lẻ': ['bán lẻ', 'siêu thị', 'thương mại', 'cửa hàng', 'mua sắm'],
            'công_nghệ': ['công nghệ', 'phần mềm', 'công nghệ thông tin', 'it', 'digital'],
            'sản_xuất': ['sản xuất', 'nhà máy', 'công nghiệp', 'chế biến', 'gia công'],
            'năng_lượng': ['điện', 'năng lượng', 'dầu khí', 'xăng dầu', 'petro'],
            'vận_tải': ['hàng không', 'vận tải', 'logistics', 'cảng', 'giao nhận'],
            'nông_nghiệp': ['nông nghiệp', 'thủy sản', 'cao su', 'gạo', 'cà phê']
        }
        
        # Stopwords tiếng Việt
        self.stopwords = set([
            'và', 'của', 'có', 'được', 'trong', 'là', 'với', 'cho', 
            'theo', 'từ', 'này', 'đó', 'các', 'những', 'một', 'để'
        ])
    
    def clean_text(self, text):
        """Làm sạch văn bản"""
        if not isinstance(text, str):
            return ""
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Loại bỏ URL
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Loại bỏ email
        text = re.sub(r'\S+@\S+', '', text)
        
        # Loại bỏ số điện thoại
        text = re.sub(r'\d{10,}', '', text)
        
        # Loại bỏ ký tự đặc biệt nhưng giữ dấu tiếng Việt
        text = re.sub(r'[^\w\s\u00C0-\u1EF9]', ' ', text)
        
        # Loại bỏ khoảng trắng thừa
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text):
        """Tách từ tiếng Việt"""
        text = self.clean_text(text)
        
        # Sử dụng underthesea để tách từ
        tokens = word_tokenize(text, format="text")
        
        return tokens
    
    def remove_stopwords(self, text):
        """Loại bỏ stopwords"""
        tokens = text.split()
        filtered_tokens = [token for token in tokens if token not in self.stopwords]
        return ' '.join(filtered_tokens)
    
    def extract_sentiment_keywords(self, text):
        """Trích xuất từ khóa cảm xúc"""
        text = text.lower()
        
        sentiment_score = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        for word in self.financial_terms['tích_cực']:
            if word in text:
                sentiment_score['positive'] += text.count(word)
        
        for word in self.financial_terms['tiêu_cực']:
            if word in text:
                sentiment_score['negative'] += text.count(word)
        
        for word in self.financial_terms['trung_tính']:
            if word in text:
                sentiment_score['neutral'] += text.count(word)
        
        return sentiment_score
    
    def extract_sector(self, text):
        """Xác định ngành liên quan"""
        text = text.lower()
        detected_sectors = []
        
        for sector, keywords in self.sectors.items():
            for keyword in keywords:
                if keyword in text:
                    detected_sectors.append(sector)
                    break
        
        return detected_sectors if detected_sectors else ['tổng_hợp']
    
    def preprocess_pipeline(self, text):
        """Pipeline xử lý hoàn chỉnh"""
        # Làm sạch
        cleaned = self.clean_text(text)
        
        # Tách từ
        tokenized = self.tokenize(cleaned)
        
        # Loại bỏ stopwords
        no_stopwords = self.remove_stopwords(tokenized)
        
        # Trích xuất đặc trưng
        sentiment = self.extract_sentiment_keywords(text)
        sectors = self.extract_sector(text)
        
        return {
            'cleaned_text': no_stopwords,
            'sentiment_score': sentiment,
            'sectors': sectors
        }