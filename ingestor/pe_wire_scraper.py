"""
Private Equity Wire News Scraper
Scrapes recent articles from Private Equity Wire RSS feed and extracts full content
Uses proper headers and respects rate limits
"""
import requests
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import json
import re
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import feedparser
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PEWireScraper:
    def __init__(self):
        self.rss_url = "https://www.privateequitywire.co.uk/rss.xml"
        
        # Use proper headers to avoid blocking
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
        
        # Rate limiting: 1 request per second to be respectful
        self.rate_limit_delay = 1.0
        self.max_concurrent = 3

    def get_recent_articles(self, days_back: int = 7, max_articles: int = 10) -> List[Dict]:
        """
        Get recent articles from Private Equity Wire RSS feed
        """
        try:
            logger.info(f"Fetching recent articles from Private Equity Wire RSS feed...")
            
            # Parse RSS feed
            feed = feedparser.parse(self.rss_url)
            
            if not feed.entries:
                logger.warning("No entries found in PE Wire RSS feed")
                return []
            
            articles = []
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            for entry in feed.entries[:max_articles]:
                try:
                    # Parse publication date
                    pub_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                    
                    # Skip if article is too old
                    if pub_date and pub_date < cutoff_date:
                        continue
                    
                    # Use RSS content as the main content since we can't scrape the full articles
                    # Try to get full content from RSS feed
                    full_content = ''
                    if entry.get('content'):
                        # Extract text from HTML content
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
                        full_content = soup.get_text(separator=' ', strip=True)
                    
                    # Fallback to summary if no full content
                    rss_content = full_content or entry.get('summary', '') or entry.get('description', '')
                    
                    article_data = {
                        'title': entry.get('title', ''),
                        'url': entry.get('link', ''),
                        'published_date': pub_date.isoformat() if pub_date else None,
                        'summary': rss_content,
                        'content': rss_content,  # Use RSS content as main content
                        'source': 'Private Equity Wire'
                    }
                    
                    articles.append(article_data)
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            logger.info(f"Found {len(articles)} recent PE Wire articles")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching PE Wire RSS feed: {e}")
            return []

    def extract_article_content(self, article_url: str) -> Dict:
        """
        Extract full article content from PE Wire article URL
        """
        try:
            logger.info(f"Extracting content from: {article_url}")
            
            # Add rate limiting
            time.sleep(self.rate_limit_delay)
            
            response = self.session.get(article_url, timeout=30)
            
            if response.status_code == 403:
                logger.warning(f"403 Forbidden for {article_url}, trying with different headers...")
                # Try with a different user agent
                alt_headers = self.headers.copy()
                alt_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                response = requests.get(article_url, headers=alt_headers, timeout=30)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article content - PE Wire specific selectors
            content_selectors = [
                'div.article-content',
                'div.post-content',
                'div.entry-content',
                'article .content',
                'div.content',
                'main article',
                'article'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style", "nav", "footer", "aside"]):
                        script.decompose()
                    
                    content_text = content_elem.get_text(separator=' ', strip=True)
                    if len(content_text) > 500:  # Ensure we have substantial content
                        break
            
            # If no specific content found, try to get all text from body
            if not content_text or len(content_text) < 500:
                body = soup.find('body')
                if body:
                    for script in body(["script", "style", "nav", "footer", "aside", "header"]):
                        script.decompose()
                    content_text = body.get_text(separator=' ', strip=True)
            
            # Clean up the content
            content_text = re.sub(r'\s+', ' ', content_text)  # Normalize whitespace
            content_text = content_text.strip()
            
            # Extract additional metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Extract author if available
            author = None
            author_selectors = [
                'span.author',
                '.author-name',
                '.byline',
                'meta[name="author"]'
            ]
            
            for selector in author_selectors:
                author_elem = soup.select_one(selector)
                if author_elem:
                    if author_elem.name == 'meta':
                        author = author_elem.get('content', '').strip()
                    else:
                        author = author_elem.get_text().strip()
                    if author:
                        break
            
            # Extract publication date if available
            pub_date = None
            date_selectors = [
                'time[datetime]',
                '.publish-date',
                '.date',
                'meta[property="article:published_time"]'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    if date_elem.name == 'meta':
                        pub_date = date_elem.get('content', '').strip()
                    else:
                        pub_date = date_elem.get('datetime') or date_elem.get_text().strip()
                    if pub_date:
                        break
            
            return {
                'title': title_text,
                'content': content_text,
                'author': author,
                'published_date': pub_date,
                'url': article_url,
                'word_count': len(content_text.split()) if content_text else 0
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {article_url}: {e}")
            return {
                'title': '',
                'content': '',
                'author': None,
                'published_date': None,
                'url': article_url,
                'word_count': 0
            }

    def get_articles_with_content(self, days_back: int = 7, max_articles: int = 5) -> List[Dict]:
        """
        Get recent articles with content from RSS feed
        """
        try:
            # Get articles directly from RSS (content is already included)
            articles = self.get_recent_articles(days_back, max_articles)
            
            if not articles:
                return []
            
            # Filter articles with sufficient content
            articles_with_content = []
            
            for article in articles:
                try:
                    # Calculate word count from RSS content
                    word_count = len(article.get('content', '').split())
                    
                    # Add word count to article data
                    article['word_count'] = word_count
                    
                    # Only include articles with substantial content (at least 100 words)
                    if word_count >= 100:
                        articles_with_content.append(article)
                        logger.info(f"Successfully processed {word_count} words from: {article['title'][:50]}...")
                    else:
                        logger.warning(f"Insufficient content ({word_count} words) from: {article['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing article {article.get('url', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(articles_with_content)} PE Wire articles with content")
            return articles_with_content
            
        except Exception as e:
            logger.error(f"Error in get_articles_with_content: {e}")
            return []

    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()
