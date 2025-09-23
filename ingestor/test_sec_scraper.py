"""
Test script for SEC S-4 filing scraper
"""
import logging
import sys
import os
from datetime import datetime

# Add the ingestor directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sec_scraper import SECScraper
from sec_content_processor import SECContentProcessor
from database import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sec_scraper():
    """Test the SEC scraper components"""
    
    logger.info("=== Testing SEC S-4 Filing Scraper ===")
    
    try:
        # Test 1: Basic SEC scraper
        logger.info("\n1. Testing SEC scraper...")
        scraper = SECScraper()
        
        # Test getting recent S-4 filings
        filings = scraper.get_recent_s4_filings(days_back=30, max_filings=3)
        
        if filings:
            logger.info(f"✅ Found {len(filings)} S-4 filings")
            for i, filing in enumerate(filings):
                logger.info(f"  {i+1}. {filing['company_name']} - {filing['filing_date']}")
                logger.info(f"     URL: {filing['document_url']}")
        else:
            logger.warning("⚠️ No S-4 filings found")
        
        # Test 2: SEC content processor
        logger.info("\n2. Testing SEC content processor...")
        processor = SECContentProcessor()
        
        # Process S-4 filings
        processed_filings = processor.process_s4_filings(max_filings=2)
        
        if processed_filings:
            logger.info(f"✅ Successfully processed {len(processed_filings)} S-4 filings")
            for i, filing in enumerate(processed_filings):
                logger.info(f"\n--- Processed Filing {i+1} ---")
                logger.info(f"Title: {filing['title']}")
                logger.info(f"Section: {filing['section_slug']}")
                logger.info(f"Tags: {filing['tags']}")
                logger.info(f"Summary: {filing['summary'][:100]}...")
                logger.info(f"Excerpt: {filing['excerpt'][:100]}...")
                logger.info(f"Slug: {filing['article_slug']}")
                logger.info(f"Company: {filing.get('company_name', 'N/A')}")
                logger.info(f"Filing Type: {filing.get('filing_type', 'N/A')}")
        else:
            logger.warning("⚠️ No S-4 filings were processed")
        
        # Test 3: Database insertion
        logger.info("\n3. Testing database insertion...")
        if processed_filings:
            db = DatabaseManager()
            
            for filing in processed_filings:
                try:
                    result = db.insert_post(filing)
                    if result:
                        logger.info(f"✅ Successfully inserted: {filing['title'][:50]}...")
                    else:
                        logger.warning(f"⚠️ Failed to insert: {filing['title'][:50]}...")
                except Exception as e:
                    logger.error(f"❌ Error inserting filing: {e}")
        
        logger.info("\n=== SEC S-4 Scraper Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ SEC scraper test failed: {e}")
        return False
    
    finally:
        # Clean up
        try:
            if 'scraper' in locals():
                scraper.close()
            if 'processor' in locals():
                processor.close()
            if 'db' in locals():
                db.close()
        except:
            pass

def test_sec_api_access():
    """Test basic SEC API access"""
    
    logger.info("\n=== Testing SEC API Access ===")
    
    try:
        import requests
        
        # Test basic SEC API access
        headers = {
            'User-Agent': 'US Financial Moves (contact@usfinancemoves.com)',
            'Accept': 'application/json'
        }
        
        # Test the company facts endpoint (which we know works)
        test_url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
        
        logger.info(f"Testing SEC API access to: {test_url}")
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ SEC API access successful")
            data = response.json()
            logger.info(f"Company: {data.get('entityName', 'N/A')}")
            logger.info(f"CIK: {data.get('cik', 'N/A')}")
            logger.info(f"Ticker: {data.get('tickers', ['N/A'])[0] if data.get('tickers') else 'N/A'}")
            
            return True
        else:
            logger.warning(f"⚠️ SEC API returned status {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ SEC API access test failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting SEC S-4 filing scraper test...")
    
    # Test SEC API access first
    api_success = test_sec_api_access()
    
    if api_success:
        # Test the full scraper
        scraper_success = test_sec_scraper()
        
        if scraper_success:
            print("\n🎉 SEC S-4 scraper test completed successfully!")
            print("📝 The scraper can fetch and process SEC S-4 filings.")
            print("🔄 S-4 filings are automatically rewritten and categorized as M&A news.")
        else:
            print("\n❌ SEC S-4 scraper test failed. Check the logs above.")
    else:
        print("\n❌ SEC API access test failed. Check your internet connection and SEC API availability.")
