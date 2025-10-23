from config.database import MongoDBConfig
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.config = MongoDBConfig()
        self.db = self.config.get_database()
    
    def save_news_data(self, df_news):
        """Lưu dữ liệu tin tức vào MongoDB"""
        try:
            collection = self.config.get_collection('news_articles')
            if collection is None:
                print("Không thể kết nối đến collection news_articles")
                return False
        
            # Chuyển DataFrame thành dict
            records = df_news.to_dict('records')
            for record in records:
                record['created_at'] = datetime.now()
            
            result = collection.insert_many(records)
            print(f"Đã lưu {len(result.inserted_ids)} bài viết vào collection news_articles")
            return True
        except Exception as e:
            print(f"Lỗi lưu dữ liệu: {e}")
            return False
    
    def save_processed_data(self, df_processed):
        """Lưu dữ liệu đã xử lý"""
        try:
            collection = self.config.get_collection('processed_articles')
            if collection is None:
                return False
            
            # Xử lý cả DataFrame và list
            if isinstance(df_processed, pd.DataFrame):
                records = df_processed.to_dict('records')
            elif isinstance(df_processed, list):
                records = df_processed
            else:
                records = [df_processed]
            
            for record in records:
                record['processed_at'] = datetime.now()
            
            result = collection.insert_many(records)
            print(f"Đã lưu {len(result.inserted_ids)} bài viết đã xử lý")
            return True
        except Exception as e:
            print(f"Lỗi lưu dữ liệu xử lý: {e}")
            return False
    
    def load_news_data(self, limit=None):
        """Tải dữ liệu tin tức từ MongoDB"""
        try:
            collection = self.config.get_collection('news_articles')
            if collection is None:
                return pd.DataFrame()
            
            cursor = collection.find().sort('created_at', -1)
            if limit:
                cursor = cursor.limit(limit)
            
            data = list(cursor)
            if data:
                df = pd.DataFrame(data)
                df.drop('_id', axis=1, inplace=True, errors='ignore')
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")
            return pd.DataFrame()
    
    def load_processed_data(self, limit=None):
        """Tải dữ liệu đã xử lý từ MongoDB"""
        try:
            collection = self.config.get_collection('processed_articles')
            if collection is None:
                return pd.DataFrame()
            
            cursor = collection.find().sort('processed_at', -1)
            if limit:
                cursor = cursor.limit(limit)
            
            data = list(cursor)
            if data:
                df = pd.DataFrame(data)
                df.drop('_id', axis=1, inplace=True, errors='ignore')
                return df
            return pd.DataFrame()
        except Exception as e:
            print(f"Lỗi tải dữ liệu đã xử lý: {e}")
            return pd.DataFrame()
    
    def save_predictions(self, predictions_data):
        """Lưu kết quả dự đoán"""
        try:
            collection = self.config.get_collection('predictions')
            if collection is None:
                return False
            
            if isinstance(predictions_data, dict):
                predictions_data['predicted_at'] = datetime.now()
                collection.insert_one(predictions_data)
                return True
            return False
        except Exception as e:
            print(f"Lỗi lưu dự đoán: {e}")
            return False