"""
Parser URL và trích xuất nội dung từ link
"""
import requests
from newspaper import Article
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class URLParser:
    """Parse và trích xuất nội dung từ URL"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def validate_url(self, url):
        """Kiểm tra URL hợp lệ"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def extract_with_newspaper(self, url):
        """Trích xuất nội dung bằng Newspaper3k"""
        try:
            article = Article(url, language='vi')
            article.download()
            article.parse()
            
            return {
                'success': True,
                'title': article.title,
                'content': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'source': urlparse(url).netloc
            }
        except Exception as e:
            logger.error(f"Newspaper extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_with_beautifulsoup(self, url):
        """Trích xuất nội dung bằng BeautifulSoup (fallback)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm tiêu đề
            title = None
            for tag in ['h1', 'title']:
                element = soup.find(tag)
                if element:
                    title = element.get_text().strip()
                    break
            
            # Tìm nội dung
            content = []
            for tag in ['article', 'div.content', 'div.article-body']:
                elements = soup.select(tag)
                if elements:
                    for elem in elements:
                        paragraphs = elem.find_all('p')
                        content.extend([p.get_text().strip() for p in paragraphs])
                    break
            
            if not content:
                paragraphs = soup.find_all('p')
                content = [p.get_text().strip() for p in paragraphs]
            
            return {
                'success': True,
                'title': title or 'No title',
                'content': '\n'.join(content),
                'source': urlparse(url).netloc
            }
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def parse_url(self, url):
        """Parse URL và trích xuất nội dung"""
        if not self.validate_url(url):
            return {'success': False, 'error': 'URL không hợp lệ'}
        
        # Thử Newspaper3k trước
        result = self.extract_with_newspaper(url)
        
        # Nếu thất bại, thử BeautifulSoup
        if not result['success']:
            result = self.extract_with_beautifulsoup(url)
        
        return result