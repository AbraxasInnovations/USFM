#!/usr/bin/env python3
"""
Debug SEC content extraction to see what we're actually getting
"""
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestor.sec_scraper import SECScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def debug_sec_content():
    """Debug what content we're actually extracting from SEC filings"""
    try:
        logger.info("Debugging SEC content extraction...")
        
        sec_scraper = SECScraper()
        
        # Get one recent S-4 filing
        filings = sec_scraper.get_recent_s4_filings(days_back=30, max_filings=1)
        
        if not filings:
            logger.warning("No S-4 filings found")
            return
        
        filing = filings[0]
        logger.info(f"Debugging filing: {filing['company_name']}")
        logger.info(f"Document URL: {filing['document_url']}")
        
        # Get the raw content first
        import requests
        response = requests.get(filing['document_url'], timeout=30)
        logger.info(f"Raw content length: {len(response.text)} characters")
        logger.info(f"Raw content preview: {response.text[:1000]}...")
        
        # Now test our extraction
        filing_content = sec_scraper.scrape_filing_content(filing)
        
        if filing_content:
            logger.info(f"Extracted content length: {len(filing_content['content'])} characters")
            logger.info(f"Extracted content: {filing_content['content']}")
        else:
            logger.error("Failed to extract content")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
    finally:
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    debug_sec_content()
