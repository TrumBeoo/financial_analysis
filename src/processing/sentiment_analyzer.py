"""
Phân tích sentiment cho văn bản tiếng Việt
"""
import numpy as np
from config.settings import SENTIMENT_LABELS

class SentimentAnalyzer:
    """Phân tích sentiment dựa trên từ khóa"""
    
    def __init__(self):
        self.positive_keywords = [
            'tăng', 'tăng trưởng', 'lợi nhuận', 'thành công', 'phát triển',
            'cải thiện', 'khả quan', 'tốt', 'cao', 'đột phá', 'tích cực',
            'hiệu quả', 'bứt phá', 'vượt trội', 'ấn tượng', 'mạnh mẽ'
        ]
        
        self.negative_keywords = [
            'giảm', 'lỗ', 'sụt giảm', 'thua lỗ', 'khó khăn', 'thách thức',
            'rủi ro', 'suy giảm', 'tệ', 'thấp', 'tiêu cực', 'khủng hoảng',
            'suy thoái', 'đình trệ', 'giảm sút', 'sa sút'
        ]
        
        self.neutral_keywords = [
            'ổn định', 'duy trì', 'giữ nguyên', 'không đổi', 'bình thường',
            'trung bình', 'vừa phải'
        ]
    
    def analyze(self, text):
        """
        Phân tích sentiment
        Returns: dict với sentiment score
        """
        text = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        negative_count = sum(1 for word in self.negative_keywords if word in text)
        neutral_count = sum(1 for word in self.neutral_keywords if word in text)
        
        total = positive_count + negative_count + neutral_count
        
        if total == 0:
            return {
                'positive': 0,
                'negative': 0,
                'neutral': 1,
                'label': 1  # Trung tính
            }
        
        scores = {
            'positive': positive_count,
            'negative': negative_count,
            'neutral': neutral_count
        }
        
        # Xác định label
        max_score = max(scores.items(), key=lambda x: x[1])
        if max_score[0] == 'positive':
            label = 2
        elif max_score[0] == 'negative':
            label = 0
        else:
            label = 1
        
        return {
            **scores,
            'label': label
        }