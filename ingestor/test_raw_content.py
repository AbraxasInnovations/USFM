#!/usr/bin/env python3
"""
Test what raw content we're actually getting from SEC
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

def test_raw_content():
    """Test what raw content we're getting from SEC"""
    try:
        logger.info("Testing raw SEC content...")
        
        sec_scraper = SECScraper()
        
        # Get recent S-4 filings
        filings = sec_scraper.get_recent_s4_filings(days_back=30, max_filings=1)
        
        if not filings:
            logger.warning("No S-4 filings found")
            return
        
        filing = filings[0]
        logger.info(f"Testing with filing: {filing['company_name']}")
        logger.info(f"Document URL: {filing['document_url']}")
        
        # Make direct request to see what we get
        import requests
        response = sec_scraper.session.get(filing['document_url'], timeout=30)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        logger.info(f"Content length: {len(response.text)}")
        
        # Check if we got blocked
        if "Your Request Originates from an Undeclared Automated Tool" in response.text:
            logger.warning("❌ SEC blocked our request")
            logger.info("Blocking page preview:")
            logger.info(response.text[:500])
        else:
            logger.info("✅ Got real content!")
            logger.info("Content preview:")
            logger.info(response.text[:1000])
            
            # Check for specific company names
            if 'pb bankshares' in response.text.lower():
                logger.info("✅ Found 'PB Bankshares' in raw content")
            if 'norwood' in response.text.lower():
                logger.info("✅ Found 'Norwood' in raw content")
            if 'acquisition' in response.text.lower():
                logger.info("✅ Found 'acquisition' in raw content")
                
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    test_raw_content()
