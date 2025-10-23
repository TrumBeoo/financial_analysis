# file: news_crawler.py

import scrapy
from scrapy.crawler import CrawlerProcess
from newspaper import Article
import newspaper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import pandas as pd
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsSpider(scrapy.Spider):
    name = 'news_spider'
    
    def __init__(self, source_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_config = source_config
        self.articles = []
    
    def start_requests(self):
        for url in self.source_config['urls']:
            yield scrapy.Request(url, callback=self.parse)
    
    def parse(self, response):
        articles = response.css(self.source_config['article_selector'])
        for article in articles[:20]:
            title_elem = article.css(self.source_config['title_selector'])
            if title_elem:
                title = title_elem.css('::text').get('').strip()
                link = title_elem.css('::attr(href)').get('')
                if link and not link.startswith('http'):
                    link = urljoin(self.source_config['base_url'], link)
                
                content_elem = article.css(self.source_config['content_selector'])
                summary = content_elem.css('::text').get('').strip() if content_elem else ''
                
                if title and link:
                    self.articles.append({
                        'source': self.source_config['name'],
                        'title': title,
                        'summary': summary,
                        'link': link,
                        'crawl_time': datetime.now()
                    })

class FinancialNewsCrawler:
    """
    Crawler tin tức tài chính sử dụng Scrapy, Selenium và Newspaper3k
    """
    
    def __init__(self):
        # Khởi tạo cấu hình Chrome
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Cấu hình Newspaper
        self.newspaper_config = newspaper.Config()
        self.newspaper_config.language = 'vi'
        self.newspaper_config.memoize_articles = False
        
        # Định nghĩa các nguồn tin
        self.news_sources = {
            'cafef': {
                'name': 'CafeF',
                'base_url': 'https://cafef.vn',
                'urls': ['https://cafef.vn/timeline.chn', 'https://cafef.vn/chung-khoan.chn'],
                'use_selenium': False,
                'article_selector': '.tlitem, .item-news',
                'title_selector': '.tltitle a, .title a',
                'content_selector': '.tlsummary, .sapo'
            },
            'vneconomy': {
                'name': 'VnEconomy',
                'base_url': 'https://vneconomy.vn',
                'urls': ['https://vneconomy.vn/chung-khoan.htm', 'https://vneconomy.vn/doanh-nghiep.htm'],
                'use_selenium': True,
                'article_selector': '.story, .item-news',
                'title_selector': '.story__title a',
                'content_selector': '.story__summary'
            },
            'vietstock': {
                'name': 'VietStock',
                'base_url': 'https://vietstock.vn',
                'urls': ['https://vietstock.vn/tin-tuc-doanh-nghiep.htm'],
                'use_selenium': True,
                'article_selector': '.news-item',
                'title_selector': '.news-title a',
                'content_selector': '.news-summary'
            },
            'vnexpress': {
                'name': 'VNExpress',
                'base_url': 'https://vnexpress.net',
                'urls': ['https://vnexpress.net/kinh-doanh/chung-khoan'],
                'use_selenium': False,
                'article_selector': 'article.item-news',
                'title_selector': 'h3.title-news a',
                'content_selector': 'p.description'
            },
            'thanhnien': {
                'name': 'Thanh Niên',
                'base_url': 'https://thanhnien.vn',
                'urls': ['https://thanhnien.vn/tai-chinh-kinh-doanh/chung-khoan.htm'],
                'use_selenium': False,
                'article_selector': 'div.story',
                'title_selector': 'h3.story-title a',
                'content_selector': 'p.summary'
            },
            'tuoitre': {
                'name': 'Tuổi Trẻ',
                'base_url': 'https://tuoitre.vn',
                'urls': ['https://tuoitre.vn/kinh-doanh/chung-khoan.htm'],
                'use_selenium': False,
                'article_selector': 'div.story',
                'title_selector': 'h3.title-news a',
                'content_selector': 'p.sapo'
            },
            'dantri': {
                'name': 'Dân Trí',
                'base_url': 'https://dantri.com.vn',
                'urls': ['https://dantri.com.vn/kinh-doanh/chung-khoan.htm'],
                'use_selenium': False,
                'article_selector': '.article',
                'title_selector': '.article-title a',
                'content_selector': '.article-sapo'
            },
            'ndh': {
                'name': 'NDH',
                'base_url': 'https://ndh.vn',
                'urls': ['https://ndh.vn/chung-khoan', 'https://ndh.vn/doanh-nghiep'],
                'use_selenium': False,
                'article_selector': '.story',
                'title_selector': '.story__title a',
                'content_selector': '.story__summary'
            }
        }
    
    def crawl_with_scrapy(self, source_name):
        """Crawl sử dụng Scrapy"""
        if source_name not in self.news_sources:
            return []
        
        source_config = self.news_sources[source_name]
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'ROBOTSTXT_OBEY': False,
            'LOG_LEVEL': 'ERROR'
        })
        
        spider = NewsSpider(source_config=source_config)
        process.crawl(spider)
        process.start()
        
        return spider.articles
    
    def crawl_with_selenium(self, source_name):
        """Crawl sử dụng Selenium cho trang cần JS"""
        if source_name not in self.news_sources:
            return []
        
        source_config = self.news_sources[source_name]
        articles = []
        
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            
            for url in source_config['urls']:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                article_elements = driver.find_elements(By.CSS_SELECTOR, source_config['article_selector'])
                
                for elem in article_elements[:20]:
                    try:
                        title_elem = elem.find_element(By.CSS_SELECTOR, source_config['title_selector'])
                        title = title_elem.text.strip()
                        link = title_elem.get_attribute('href')
                        
                        if not link.startswith('http'):
                            link = urljoin(source_config['base_url'], link)
                        
                        try:
                            content_elem = elem.find_element(By.CSS_SELECTOR, source_config['content_selector'])
                            summary = content_elem.text.strip()
                        except:
                            summary = ''
                        
                        if title and link:
                            articles.append({
                                'source': source_config['name'],
                                'title': title,
                                'summary': summary,
                                'link': link,
                                'crawl_time': datetime.now()
                            })
                    except:
                        continue
            
            driver.quit()
        except Exception as e:
            logger.error(f"Selenium error for {source_name}: {e}")
        
        return articles
    
    def crawl_with_newspaper(self, source_name):
        """Crawl sử dụng Newspaper3k"""
        if source_name not in self.news_sources:
            return []
        
        source_config = self.news_sources[source_name]
        articles = []
        
        try:
            paper = newspaper.build(source_config['base_url'], config=self.newspaper_config)
            
            for article_url in paper.article_urls()[:20]:
                try:
                    article = Article(article_url, config=self.newspaper_config)
                    article.download()
                    article.parse()
                    
                    if article.title and len(article.text) > 100:
                        articles.append({
                            'source': source_config['name'],
                            'title': article.title,
                            'summary': article.text[:200] + '...',
                            'link': article_url,
                            'crawl_time': datetime.now()
                        })
                except:
                    continue
        except Exception as e:
            logger.error(f"Newspaper error for {source_name}: {e}")
        
        return articles
    
    def get_article_detail(self, url):
        """Lấy nội dung chi tiết bằng Newspaper3k"""
        try:
            article = Article(url, config=self.newspaper_config)
            article.download()
            article.parse()
            return article.text
        except Exception as e:
            logger.error(f"Error getting article detail: {e}")
            return ""
    
    def crawl_source(self, source_name):
        """Crawl một nguồn tin cụ thể"""
        if source_name not in self.news_sources:
            return []
        
        source_config = self.news_sources[source_name]
        
        if source_config.get('use_selenium', False):
            return self.crawl_with_selenium(source_name)
        else:
            # Thử newspaper3k trước, fallback sang scrapy
            articles = self.crawl_with_newspaper(source_name)
            if not articles:
                articles = self.crawl_with_scrapy(source_name)
            return articles
    
    def crawl_all(self, max_workers=3):
        """Crawl tất cả nguồn tin song song"""
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.crawl_source, source): source 
                      for source in self.news_sources.keys()}
            
            for future in futures:
                try:
                    articles = future.result(timeout=60)
                    all_articles.extend(articles)
                    logger.info(f"Crawled {len(articles)} articles from {futures[future]}")
                except Exception as e:
                    logger.error(f"Error crawling {futures[future]}: {e}")
        
        df = pd.DataFrame(all_articles)
        if not df.empty:
            df = df.drop_duplicates(subset=['title'], keep='first')
        
        return df

# Example usage
if __name__ == "__main__":
    crawler = FinancialNewsCrawler()
    
    # Crawl một nguồn cụ thể
    # articles = crawler.crawl_source('cafef')
    
    # Crawl tất cả nguồn
    df = crawler.crawl_all()
    print(f"Crawled {len(df)} articles total")
    
    # Lưu kết quả
    if not df.empty:
        df.to_csv('financial_news.csv', index=False, encoding='utf-8')
        print("Saved to financial_news.csv")