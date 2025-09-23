"""
Web scraper for financial news websites without RSS feeds
"""
import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def scrape_wealthspire(self, max_articles: int = 5) -> List[Dict]:
        """
        Scrape recent articles from wealthspire.com
        """
        try:
            logger.info("Scraping wealthspire.com...")
            
            # Try both homepage and blog page
            urls_to_try = [
                "https://www.wealthspire.com/",
                "https://www.wealthspire.com/blog/",
                "https://www.wealthspire.com/news/"
            ]
            
            article_links = set()
            
            for base_url in urls_to_try:
                try:
                    logger.info(f"Checking {base_url}...")
                    response = self.session.get(base_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for article links - WealthSpire specific patterns
                    all_links = soup.find_all('a', href=True)
                    
                    for link in all_links:
                        href = link.get('href')
                        text = link.get_text().strip()
                        
                        if href and text:
                            # Convert relative URLs to absolute
                            full_url = urljoin(base_url, href)
                            
                            # Look for blog/news articles
                            if any(pattern in href.lower() for pattern in ['/blog/', '/news/']) and len(text) > 10:
                                # Skip navigation and footer links
                                if not any(skip in href.lower() for skip in ['/about/', '/contact/', '/team/', '/services/']):
                                    article_links.add(full_url)
                                    logger.info(f"Found article link: {full_url} - '{text[:50]}...'")
                
                except Exception as e:
                    logger.warning(f"Error checking {base_url}: {e}")
                    continue
            
            logger.info(f"Found {len(article_links)} potential article links")
            
            # Initialize articles list
            articles = []
            
            # Scrape individual articles
            for i, article_url in enumerate(list(article_links)[:max_articles]):
                try:
                    article_data = self._scrape_article(article_url)
                    if article_data:
                        articles.append(article_data)
                        logger.info(f"Scraped article {i+1}/{max_articles}: {article_data['title'][:50]}...")
                    
                    # Be respectful - add delay between requests
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping article {article_url}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from wealthspire.com")
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping wealthspire.com: {e}")
            return []

    def _is_article_url(self, url: str) -> bool:
        """Check if URL looks like an article"""
        # Skip certain URL patterns
        skip_patterns = [
            '/category/',
            '/tag/',
            '/author/',
            '/page/',
            '/search',
            '/about',
            '/contact',
            '/privacy',
            '/terms',
            '/subscribe',
            '/login',
            '/register',
            '/team/',
            '/services/',
            '.pdf',
            '.jpg',
            '.png',
            '.gif',
            '#'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        # Must have article-like path (WealthSpire specific)
        article_patterns = [
            '/blog/',
            '/news/'
        ]
        
        # For WealthSpire, we want URLs that have /blog/ or /news/ with additional path segments
        if any(pattern in url.lower() for pattern in article_patterns):
            # Make sure it's not just the base blog/news page
            path_parts = url.split('/')
            if len(path_parts) > 4:  # Should have more than just /blog/ or /news/
                return True
        
        return False

    def _scrape_article(self, url: str) -> Optional[Dict]:
        """Scrape individual article content"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            if not title:
                return None
            
            # Extract content
            content = self._extract_content(soup)
            if not content or len(content.strip()) < 100:
                return None
            
            # Extract author
            author = self._extract_author(soup)
            
            # Extract publish date
            publish_date = self._extract_publish_date(soup)
            
            # Extract image
            image_url = self._extract_image(soup, url)
            
            # Clean and prepare content
            content = self._clean_content(content)
            
            return {
                'title': title.strip(),
                'content': content,
                'author': author,
                'publish_date': publish_date,
                'url': url,
                'image_url': image_url,
                'source_name': 'WealthSpire',
                'domain': urlparse(url).netloc
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title"""
        selectors = [
            'h1.article-title',
            'h1.headline',
            'h1.entry-title',
            'h1.post-title',
            'h1',
            '.article-header h1',
            '.story-header h1',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title and len(title) > 10:
                    return title
        
        return None

    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        selectors = [
            '.article-content',
            '.article-body',
            '.story-content',
            '.entry-content',
            '.post-content',
            '.content',
            'article',
            '.article-text'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Get all paragraph text
                paragraphs = element.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                if content and len(content) > 100:
                    return content
        
        # Fallback: if no specific content container found, get all paragraphs from the page
        all_paragraphs = soup.find_all('p')
        if all_paragraphs:
            content = ' '.join([p.get_text().strip() for p in all_paragraphs if p.get_text().strip() and len(p.get_text().strip()) > 20])
            
            if content and len(content) > 100:
                return content
        
        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author"""
        selectors = [
            '.author-name',
            '.byline',
            '.article-author',
            '.story-author',
            '[rel="author"]',
            '.author',
            'meta[name="author"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                else:
                    author = element.get_text().strip()
                    if author and len(author) < 100:
                        return author
        
        return None

    def _extract_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publish date"""
        selectors = [
            '.publish-date',
            '.article-date',
            '.story-date',
            '.entry-date',
            'time[datetime]',
            'meta[property="article:published_time"]',
            'meta[name="date"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    return element.get('content', '').strip()
                elif element.name == 'time':
                    return element.get('datetime', '').strip()
                else:
                    date_text = element.get_text().strip()
                    if date_text:
                        return date_text
        
        return None

    def _extract_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract article image"""
        selectors = [
            '.article-image img',
            '.story-image img',
            '.featured-image img',
            '.hero-image img',
            'article img',
            'meta[property="og:image"]',
            'meta[name="twitter:image"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    image_url = element.get('content', '').strip()
                else:
                    image_url = element.get('src', '').strip()
                
                if image_url:
                    # Convert relative URLs to absolute
                    return urljoin(base_url, image_url)
        
        return None

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted text
        unwanted_phrases = [
            'Subscribe to',
            'Read more:',
            'Continue reading',
            'Advertisement',
            'Related:',
            'More from',
            'Follow us on'
        ]
        
        for phrase in unwanted_phrases:
            content = content.replace(phrase, '')
        
        return content.strip()

    def close(self):
        """Close the session"""
        self.session.close()
