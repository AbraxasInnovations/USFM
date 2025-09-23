"""
Debug script to see what URLs are being found and why scraping fails
"""
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_wealthspire():
    """Debug WealthSpire scraping"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        logger.info("Fetching WealthSpire homepage...")
        url = "https://www.wealthspire.com/"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch homepage: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for all links
        all_links = soup.find_all('a', href=True)
        logger.info(f"Found {len(all_links)} total links")
        
        # Check for article-like links
        article_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Look for various patterns
            if any(pattern in href.lower() for pattern in ['/article/', '/news/', '/story/', '/post/', '/blog/', '/insights/']):
                article_links.append((href, text))
        
        logger.info(f"Found {len(article_links)} potential article links:")
        for i, (href, text) in enumerate(article_links[:10]):  # Show first 10
            logger.info(f"  {i+1}. {href} - '{text[:50]}...'")
        
        # Try to find blog/insights section
        logger.info("\nLooking for blog/insights sections...")
        blog_sections = soup.find_all(['section', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['blog', 'insights', 'news', 'article']))
        logger.info(f"Found {len(blog_sections)} potential blog sections")
        
        # Look for specific WealthSpire patterns
        logger.info("\nLooking for WealthSpire-specific content...")
        insights_links = soup.find_all('a', href=lambda x: x and 'insights' in x.lower())
        logger.info(f"Found {len(insights_links)} insights links")
        
        for link in insights_links[:5]:
            href = link.get('href', '')
            text = link.get_text().strip()
            logger.info(f"  Insights: {href} - '{text[:50]}...'")
        
        # Try to access insights page directly
        insights_url = "https://www.wealthspire.com/insights/"
        logger.info(f"\nTrying to access insights page: {insights_url}")
        
        insights_response = requests.get(insights_url, headers=headers, timeout=10)
        if insights_response.status_code == 200:
            logger.info("✅ Successfully accessed insights page")
            insights_soup = BeautifulSoup(insights_response.content, 'html.parser')
            
            # Look for article links on insights page
            insights_article_links = insights_soup.find_all('a', href=True)
            logger.info(f"Found {len(insights_article_links)} links on insights page")
            
            for link in insights_article_links[:5]:
                href = link.get('href', '')
                text = link.get_text().strip()
                if text and len(text) > 10:  # Only show links with meaningful text
                    logger.info(f"  Insights article: {href} - '{text[:50]}...'")
        else:
            logger.warning(f"⚠️ Could not access insights page: {insights_response.status_code}")
        
    except Exception as e:
        logger.error(f"Error debugging WealthSpire: {e}")

if __name__ == "__main__":
    debug_wealthspire()
