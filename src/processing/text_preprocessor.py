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
        
        # Các ngành quan trọng trên thị trường chứng khoán VN - CẢI THIỆN
        self.sectors = {
            'Banking': [
                # Tiếng Việt
                'ngân hàng', 'bank', 'vietcombank', 'vietinbank', 'bidv', 'agribank',
                'techcombank', 'vpbank', 'acb', 'mb', 'sacombank', 'scb',
                'tín dụng', 'cho vay', 'huy động', 'tiền gửi', 'lãi suất',
                'npl', 'nợ xấu', 'dư nợ', 'tăng trưởng tín dụng', 'nim',
                # Tiếng Anh
                'credit growth', 'deposit', 'lending', 'loan', 'interest rate'
            ],
            'Real Estate': [
                # Tiếng Việt
                'bất động sản', 'bds', 'nhà đất', 'căn hộ', 'chung cư',
                'dự án', 'khu đô thị', 'condotel', 'biệt thự', 'townhouse',
                'vingroup', 'vinhomes', 'novaland', 'khang điền', 'đất xanh',
                'hưng thịnh', 'phát đạt', 'cotec', 'hòa bình',
                'thị trường nhà đất', 'giá nhà', 'giao dịch bđs',
                # Tiếng Anh  
                'property', 'housing', 'apartment', 'villa', 'real estate developer'
            ],
            'Finance': [
                # Tiếng Việt
                'chứng khoán', 'cổ phiếu', 'trái phiếu', 'đầu tư', 'niêm yết',
                'hose', 'hnx', 'upcom', 'vnindex', 'vn30', 'vn diamond',
                'ssi', 'hsc', 'vndirect', 'vcbs', 'vps', 'fpts', 'bvsc',
                'giao dịch', 'thanh khoản', 'vốn hóa', 'p/e', 'eps',
                'cổ tức', 'phát hành', 'thị trường vốn',
                # Tiếng Anh
                'stock', 'bond', 'securities', 'trading', 'market cap', 'dividend'
            ],
            'Retail': [
                # Tiếng Việt
                'bán lẻ', 'siêu thị', 'thương mại', 'cửa hàng', 'mua sắm',
                'vinmart', 'winmart', 'co.op mart', 'saigon co.op', 'aeon', 'lotte',
                'mm mega market', 'big c', 'vincom', 'emart',
                'thế giới di động', 'điện máy xanh', 'fpt shop', 'cellphones',
                'bách hóa', 'trung tâm thương mại', 'tiêu dùng',
                # Tiếng Anh
                'retail', 'supermarket', 'shopping mall', 'consumer', 'e-commerce'
            ],
            'Technology': [
                # Tiếng Việt
                'công nghệ', 'phần mềm', 'công nghệ thông tin', 'it', 'digital',
                'fpt', 'viettel', 'vnpt', 'cmg', 'cmb', 'sam', 'vng', 'momo',
                'fintech', 'ai', 'blockchain', 'iot', 'cloud', 'saas',
                'chuyển đổi số', 'số hóa', 'ứng dụng', 'nền tảng',
                # Tiếng Anh
                'software', 'platform', 'app', 'digitalization', 'tech startup'
            ],
            'Manufacturing': [
                # Tiếng Việt
                'sản xuất', 'nhà máy', 'công nghiệp', 'chế biến', 'gia công',
                'dệt may', 'da giày', 'điện tử', 'linh kiện', 'ô tô', 'xe máy',
                'hòa phát', 'vinfast', 'thaco', 'vinatex', 'garco', 'pyn',
                'xuất khẩu', 'fdi', 'khu công nghiệp', 'nhà xưởng',
                # Tiếng Anh
                'manufacturing', 'factory', 'production', 'textile', 'automotive'
            ],
            'Energy': [
                # Tiếng Việt
                'điện', 'năng lượng', 'dầu khí', 'xăng dầu', 'petro',
                'evn', 'petrovietnam', 'pvn', 'pv gas', 'pv power', 'pv oil',
                'nhiệt điện', 'thủy điện', 'điện gió', 'điện mặt trời',
                'năng lượng tái tạo', 'khí đốt', 'lng',
                # Tiếng Anh
                'electricity', 'power', 'renewable energy', 'solar', 'wind power', 'oil gas'
            ],
            'Transportation': [
                # Tiếng Việt
                'hàng không', 'vận tải', 'logistics', 'cảng', 'giao nhận',
                'vietnam airlines', 'vietjet', 'bamboo airways', 'vietjet air',
                'gemadept', 'hải phòng', 'sài gòn port', 'tan cang',
                'vận chuyển', 'kho bãi', 'container', 'hậu cần',
                # Tiếng Anh
                'airline', 'shipping', 'port', 'freight', 'cargo', 'warehouse'
            ],
            'Agriculture': [
                # Tiếng Việt
                'nông nghiệp', 'thủy sản', 'cao su', 'gạo', 'cà phê',
                'hồ tiêu', 'điều', 'tôm', 'cá tra', 'thuỷ sản',
                'vinamilk', 'masan', 'hoang anh gia lai', 'thadi', 'phu nhuan jewelry',
                'chăn nuôi', 'trồng trọt', 'chế biến thực phẩm',
                # Tiếng Anh
                'agriculture', 'seafood', 'rubber', 'coffee', 'rice', 'aquaculture'
            ],
            'Other': [
                'tổng hợp', 'đa ngành', 'khác', 'other', 'diversified', 'conglomerate'
            ]
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
        """Xác định ngành liên quan - CẢI THIỆN"""
        text = text.lower()
        detected_sectors = []
        
        # Tính điểm cho mỗi ngành
        sector_scores = {}
        
        for sector, keywords in self.sectors.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text:
                    # Từ dài hơn có trọng số cao hơn
                    weight = len(keyword.split())
                    score += weight
            
            if score > 0:
                sector_scores[sector] = score
        
        # Sắp xếp theo điểm số và lấy top ngành
        if sector_scores:
            sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)
            # Lấy ngành có điểm cao nhất, hoặc top 2 nếu điểm gần bằng nhau
            detected_sectors.append(sorted_sectors[0][0])
            
            if len(sorted_sectors) > 1:
                # Nếu ngành thứ 2 có điểm >= 70% ngành đầu
                if sorted_sectors[1][1] >= sorted_sectors[0][1] * 0.7:
                    detected_sectors.append(sorted_sectors[1][0])
        
        return detected_sectors if detected_sectors else ['Other']
    
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