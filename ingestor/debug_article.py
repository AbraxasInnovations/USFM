"""
Debug script to test scraping a specific WealthSpire article
"""
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_specific_article():
    """Debug scraping a specific WealthSpire article"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Test with a specific article
    test_url = "https://www.wealthspire.com/blog/sell-or-stay-thinking-strategically-about-vested-rsus/"
    
    try:
        logger.info(f"Testing article: {test_url}")
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch article: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Test title extraction
        logger.info("Testing title extraction...")
        title_selectors = [
            'h1.article-title',
            'h1.headline',
            'h1.entry-title',
            'h1.post-title',
            'h1',
            '.article-header h1',
            '.story-header h1',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                logger.info(f"Found title with '{selector}': {title[:100]}...")
                break
        else:
            logger.warning("No title found with any selector")
        
        # Test content extraction
        logger.info("Testing content extraction...")
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        content_selectors = [
            '.article-content',
            '.article-body',
            '.story-content',
            '.entry-content',
            '.post-content',
            '.content',
            'article',
            '.article-text'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                paragraphs = element.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
                
                if content and len(content) > 100:
                    logger.info(f"Found content with '{selector}': {len(content)} chars")
                    logger.info(f"Content preview: {content[:200]}...")
                    break
        else:
            logger.warning("No content found with any selector")
            
            # Try to find any paragraphs
            all_paragraphs = soup.find_all('p')
            logger.info(f"Found {len(all_paragraphs)} total paragraphs")
            
            if all_paragraphs:
                # Show first few paragraphs
                for i, p in enumerate(all_paragraphs[:3]):
                    text = p.get_text().strip()
                    if text and len(text) > 20:
                        logger.info(f"Paragraph {i+1}: {text[:100]}...")
        
        # Test author extraction
        logger.info("Testing author extraction...")
        author_selectors = [
            '.author-name',
            '.byline',
            '.article-author',
            '.story-author',
            '[rel="author"]',
            '.author',
            'meta[name="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    author = element.get('content', '').strip()
                else:
                    author = element.get_text().strip()
                if author:
                    logger.info(f"Found author with '{selector}': {author}")
                    break
        else:
            logger.info("No author found")
        
        # Test date extraction
        logger.info("Testing date extraction...")
        date_selectors = [
            '.publish-date',
            '.article-date',
            '.story-date',
            '.entry-date',
            'time[datetime]',
            'meta[property="article:published_time"]',
            'meta[name="date"]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    date_text = element.get('content', '').strip()
                elif element.name == 'time':
                    date_text = element.get('datetime', '').strip()
                else:
                    date_text = element.get_text().strip()
                if date_text:
                    logger.info(f"Found date with '{selector}': {date_text}")
                    break
        else:
            logger.info("No date found")
        
    except Exception as e:
        logger.error(f"Error debugging article: {e}")

if __name__ == "__main__":
    debug_specific_article()
