"""
Article scraper for extracting full content from news URLs
"""
import requests
import logging
from typing import Optional, Dict
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class ArticleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape full article content from a URL
        Returns dict with title, content, author, publish_date, etc.
        """
        try:
            logger.info(f"Scraping article: {url}")
            
            # Add delay to be respectful
            time.sleep(1)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article data
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'content': self._extract_content(soup),
                'author': self._extract_author(soup),
                'publish_date': self._extract_publish_date(soup),
                'domain': urlparse(url).netloc
            }
            
            if article_data['content']:
                logger.info(f"Successfully scraped article: {article_data['title'][:50]}...")
                return article_data
            else:
                logger.warning(f"No content found for: {url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try multiple selectors for title
        title_selectors = [
            'h1.article-title',
            'h1.headline',
            'h1[data-testid="headline"]',
            'h1',
            '.headline',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        return ""
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try multiple selectors for article content
        content_selectors = [
            'article .article-body',
            'article .content',
            '.article-content',
            '.story-body',
            '.post-content',
            'article p',
            '.entry-content',
            '[data-testid="article-body"]'
        ]
        
        content_text = ""
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Get all paragraphs within the content
                paragraphs = content_elem.find_all('p')
                if paragraphs:
                    content_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                    break
        
        # If no specific content found, try to get all paragraphs
        if not content_text:
            paragraphs = soup.find_all('p')
            content_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Clean up the content
        content_text = ' '.join(content_text.split())  # Remove extra whitespace
        
        return content_text[:5000]  # Limit to 5000 characters
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extract article author"""
        author_selectors = [
            '.author',
            '.byline',
            '[data-testid="author"]',
            '.article-author',
            '.writer'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.get_text().strip()
        
        return ""
    
    def _extract_publish_date(self, soup: BeautifulSoup) -> str:
        """Extract article publish date"""
        date_selectors = [
            'time[datetime]',
            '.publish-date',
            '.article-date',
            '[data-testid="timestamp"]'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                # Try to get datetime attribute first
                datetime_attr = date_elem.get('datetime')
                if datetime_attr:
                    return datetime_attr
                return date_elem.get_text().strip()
        
        return ""
    
    def close(self):
        """Close the session"""
        self.session.close()
