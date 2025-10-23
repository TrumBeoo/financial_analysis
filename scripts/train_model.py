"""
Script huấn luyện model phân loại
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import pandas as pd
from src.database.db_manager import DatabaseManager
from src.models.classifier import NewsClassifier
from config.settings import MODEL_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Huấn luyện model từ dữ liệu trong database"""
    
    logger.info("🚀 Bắt đầu huấn luyện model...")
    
    # Load dữ liệu
    db_manager = DatabaseManager()
    df = db_manager.load_processed_data(limit=5000)
    
    if df.empty:
        logger.error("❌ Không có dữ liệu để huấn luyện!")
        return
    
    # Chuẩn bị dữ liệu
    if 'cleaned_text' not in df.columns or 'predicted_label' not in df.columns:
        logger.error("❌ Dữ liệu thiếu cột cần thiết!")
        return
    
    df_train = df[['cleaned_text', 'predicted_label']].copy()
    df_train.columns = ['text', 'label']
    df_train = df_train[df_train['text'].str.len() > 10]
    
    if len(df_train) < 100:
        logger.warning("⚠️ Dữ liệu quá ít để huấn luyện!")
        return
    
    logger.info(f"✓ Chuẩn bị {len(df_train)} mẫu dữ liệu")
    
    # Khởi tạo và huấn luyện model
    classifier = NewsClassifier(model_type='naive_bayes')
    
    X_train, X_test, y_train, y_test = classifier.prepare_training_data(df_train)
    
    logger.info("📊 Bắt đầu huấn luyện Naive Bayes...")
    classifier.train_naive_bayes(X_train, y_train)
    
    # Đánh giá
    logger.info("📈 Đánh giá model...")
    classifier.evaluate(X_test, y_test)
    
    # Lưu model
    import joblib
    model_path = MODEL_DIR / 'naive_bayes_model.pkl'
    vectorizer_path = MODEL_DIR / 'tfidf_vectorizer.pkl'
    
    joblib.dump(classifier.model, model_path)
    joblib.dump(classifier.vectorizer, vectorizer_path)
    
    logger.info(f"✅ Đã lưu model tại: {model_path}")
    logger.info("✅ Hoàn thành!")

if __name__ == '__main__':
    main()