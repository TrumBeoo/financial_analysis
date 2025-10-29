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
        """Trích xuất nội dung bằng Newspaper3k - CẢI THIỆN"""
        try:
            article = Article(url, language='vi')
            article.download()
            article.parse()
            
            # Kiểm tra content có đầy đủ không
            if not article.text or len(article.text) < 100:
                logger.warning(f"Content too short from newspaper3k: {len(article.text)} chars")
                return {'success': False, 'error': 'Content too short'}
            
            return {
                'success': True,
                'title': article.title,
                'content': article.text,  # Full content
                'summary': article.text[:500] + '...' if len(article.text) > 500 else article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'source': urlparse(url).netloc,
                'content_length': len(article.text)  # Debug info
            }
        except Exception as e:
            logger.error(f"Newspaper extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def extract_with_beautifulsoup(self, url):
        """Trích xuất nội dung bằng BeautifulSoup (fallback) - CẢI THIỆN"""
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
            
            # Tìm nội dung - CẢI THIỆN
            content = []
            
            # Thử các selector phổ biến cho nội dung bài viết
            selectors = [
                'article', 'div.article-body', 'div.content', 'div.entry-content',
                'div.post-content', 'div.article-content', 'div.detail-content'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        paragraphs = elem.find_all('p')
                        content.extend([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
                    if content:
                        break
            
            # Nếu không tìm thấy, lấy tất cả thẻ p
            if not content:
                paragraphs = soup.find_all('p')
                content = [p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20]
            
            full_content = '\n'.join(content)
            
            if not full_content or len(full_content) < 100:
                logger.warning(f"Content too short from BeautifulSoup: {len(full_content)} chars")
                return {'success': False, 'error': 'Content too short'}
            
            return {
                'success': True,
                'title': title or 'No title',
                'content': full_content,  # Full content
                'summary': full_content[:500] + '...' if len(full_content) > 500 else full_content,
                'source': urlparse(url).netloc,
                'content_length': len(full_content)
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
        
        # Nếu thất bại hoặc content quá ngắn, thử BeautifulSoup
        if not result['success']:
            logger.info("Trying BeautifulSoup fallback...")
            result = self.extract_with_beautifulsoup(url)
        
        # Log kết quả
        if result['success']:
            logger.info(f"✓ Extracted {result.get('content_length', 0)} chars from {url}")
        else:
            logger.error(f"✗ Failed to extract content from {url}")
        
        return result