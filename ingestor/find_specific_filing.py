#!/usr/bin/env python3
"""
Find the specific filing that contains PB Bankshares and Norwood
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

def find_specific_filing():
    """Find the filing that contains PB Bankshares and Norwood"""
    try:
        logger.info("Searching for filings with PB Bankshares and Norwood...")
        
        sec_scraper = SECScraper()
        
        # Get more S-4 filings to search through
        filings = sec_scraper.get_recent_s4_filings(days_back=60, max_filings=10)
        
        if not filings:
            logger.warning("No S-4 filings found")
            return
        
        logger.info(f"Found {len(filings)} S-4 filings to check")
        
        for i, filing in enumerate(filings):
            logger.info(f"\n=== Checking filing {i+1}/{len(filings)} ===")
            logger.info(f"Company: {filing['company_name']}")
            logger.info(f"URL: {filing['document_url']}")
            
            # Scrape the content
            filing_content = sec_scraper.scrape_filing_content(filing)
            
            if filing_content:
                content_lower = filing_content['content'].lower()
                
                # Check for specific company names
                if 'pb bankshares' in content_lower:
                    logger.info("✅ Found 'PB Bankshares' in this filing!")
                    logger.info(f"Content preview: {filing_content['content'][:500]}...")
                    return filing_content
                    
                if 'norwood' in content_lower:
                    logger.info("✅ Found 'Norwood' in this filing!")
                    logger.info(f"Content preview: {filing_content['content'][:500]}...")
                    return filing_content
                    
                logger.info("❌ No specific company names found in this filing")
            else:
                logger.warning("Failed to scrape content for this filing")
        
        logger.info("No filings found with PB Bankshares or Norwood")
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
    finally:
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    find_specific_filing()
