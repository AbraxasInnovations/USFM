"""
Simple test for web scraping with a more accessible financial news site
"""
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_simple_scraping():
    """Test scraping with a simpler financial news site"""
    
    # Try a few different financial news sites
    test_sites = [
        "https://www.reuters.com/business/",
        "https://www.cnbc.com/finance/",
        "https://finance.yahoo.com/",
        "https://www.marketwatch.com/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    for site in test_sites:
        try:
            logger.info(f"Testing {site}...")
            response = requests.get(site, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Successfully accessed {site}")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for article links
                links = soup.find_all('a', href=True)
                article_links = []
                
                for link in links:
                    href = link.get('href', '')
                    if any(keyword in href.lower() for keyword in ['/article/', '/news/', '/story/', '/post/']):
                        if href.startswith('/'):
                            href = site.rstrip('/') + href
                        article_links.append(href)
                
                logger.info(f"Found {len(article_links)} potential article links")
                
                if article_links:
                    # Test scraping one article
                    test_url = article_links[0]
                    logger.info(f"Testing article scraping: {test_url}")
                    
                    article_response = requests.get(test_url, headers=headers, timeout=10)
                    if article_response.status_code == 200:
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        title = article_soup.find('h1')
                        if title:
                            logger.info(f"✅ Successfully scraped article: {title.get_text().strip()[:50]}...")
                            return site, test_url
                        else:
                            logger.warning(f"⚠️ No title found in article")
                    else:
                        logger.warning(f"⚠️ Article request failed: {article_response.status_code}")
                
            else:
                logger.warning(f"⚠️ Site returned {response.status_code}: {site}")
                
        except Exception as e:
            logger.error(f"❌ Error testing {site}: {e}")
    
    return None, None

if __name__ == "__main__":
    working_site, working_article = test_simple_scraping()
    
    if working_site:
        print(f"\n🎉 Found working site: {working_site}")
        print(f"Sample article: {working_article}")
    else:
        print("\n❌ No accessible financial news sites found")
