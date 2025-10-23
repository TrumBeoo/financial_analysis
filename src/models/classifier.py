"""
Mô hình phân loại sentiment cho tin tức tài chính
"""
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pandas as pd
import logging
from pathlib import Path
from config.settings import MODEL_DIR, MODEL_CONFIG

logger = logging.getLogger(__name__)

class FinancialSentimentClassifier:
    """Mô hình phân loại sentiment cho tin tức tài chính"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.model_path = MODEL_DIR / 'sentiment_model.pkl'
        
    def create_pipeline(self):
        """Tạo pipeline xử lý"""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=MODEL_CONFIG['max_features'],
                ngram_range=MODEL_CONFIG['ngram_range'],
                min_df=MODEL_CONFIG['min_df'],
                stop_words=None
            )),
            ('classifier', MultinomialNB(alpha=0.1))
        ])
        
    def train(self, texts, labels):
        """Huấn luyện mô hình"""
        if self.pipeline is None:
            self.create_pipeline()
            
        # Chia dữ liệu
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Huấn luyện
        logger.info("Training sentiment classifier...")
        self.pipeline.fit(X_train, y_train)
        
        # Đánh giá
        y_pred = self.pipeline.predict(X_test)
        report = classification_report(y_test, y_pred)
        logger.info(f"Classification Report:\n{report}")
        
        # Lưu mô hình
        self.save_model()
        
        return {
            'accuracy': self.pipeline.score(X_test, y_test),
            'report': report
        }
    
    def predict(self, texts):
        """Dự đoán sentiment"""
        if self.pipeline is None:
            self.load_model()
            
        if self.pipeline is None:
            logger.error("No model available for prediction")
            return None
            
        if isinstance(texts, str):
            texts = [texts]
            
        predictions = self.pipeline.predict(texts)
        probabilities = self.pipeline.predict_proba(texts)
        
        results = []
        for i, text in enumerate(texts):
            results.append({
                'text': text,
                'prediction': int(predictions[i]),
                'probabilities': probabilities[i].tolist()
            })
            
        return results
    
    def save_model(self):
        """Lưu mô hình"""
        try:
            MODEL_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Tải mô hình"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                logger.info(f"Model loaded from {self.model_path}")
                return True
            else:
                logger.warning("No saved model found")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def create_sample_data(self):
        """Tạo dữ liệu mẫu để huấn luyện"""
        sample_data = [
            ("Lợi nhuận tăng trưởng mạnh mẽ", 2),
            ("Doanh thu giảm sút đáng kể", 0),
            ("Kết quả kinh doanh ổn định", 1),
            ("Cổ phiếu tăng giá liên tục", 2),
            ("Thị trường chứng khoán suy giảm", 0),
            ("Triển vọng phát triển tích cực", 2),
            ("Gặp khó khăn trong kinh doanh", 0),
            ("Duy trì hoạt động bình thường", 1),
            ("Đạt được thành công vượt bậc", 2),
            ("Thua lỗ trong quý này", 0)
        ]
        
        texts = [item[0] for item in sample_data]
        labels = [item[1] for item in sample_data]
        
        return texts, labels