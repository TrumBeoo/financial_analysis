import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBConfig:
    def __init__(self):
        # Cấu hình MongoDB
        self.host = os.getenv('MONGO_HOST', 'localhost')
        self.port = int(os.getenv('MONGO_PORT', 27017))
        self.database = os.getenv('MONGO_DATABASE', 'financial_analysis')
        self.username = os.getenv('MONGO_USERNAME', '')
        self.password = os.getenv('MONGO_PASSWORD', '')
        
        # Collections
        self.collections = {
            'news': 'news_articles',
            'processed': 'processed_articles',
            'models': 'ml_models',
            'predictions': 'predictions'
        }
    
    def get_connection_string(self):
        # Uu tien dung connection string tu .env
        connection_string = os.getenv('MONGO_CONNECTION_STRING')
        if connection_string:
            return connection_string
        
        # Fallback sang cau hinh local
        if self.username and self.password:
            username = quote_plus(self.username)
            password = quote_plus(self.password)
            return f"mongodb://{username}:{password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"mongodb://{self.host}:{self.port}/{self.database}"
    
    def get_client(self):
        try:
            client = MongoClient(self.get_connection_string())
            # Test connection
            client.admin.command('ping')
            return client
        except Exception as e:
            print(f"Loi ket noi MongoDB: {e}")
            return None
    
    def get_database(self):
        client = self.get_client()
        if client is not None:
            return client[self.database]
        return None
    
    def get_collection(self, collection_name):
        db = self.get_database()
        if db is not None:
            if collection_name in self.collections:
                return db[self.collections[collection_name]]
            else:
                # Fallback cho collection name trực tiếp
                return db[collection_name]
        return None