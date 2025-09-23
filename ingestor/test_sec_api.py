#!/usr/bin/env python3
"""
Test the new SEC API-based scraper
"""
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestor.sec_api_scraper import SECAPIScraper
from ingestor.article_rewriter import ArticleRewriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_sec_api_scraper():
    """Test the new SEC API scraper"""
    try:
        logger.info("Testing SEC API scraper...")
        
        # Initialize components
        sec_scraper = SECAPIScraper()
        rewriter = ArticleRewriter()
        
        # Get recent S-4 filings
        logger.info("Fetching recent S-4 filings...")
        filings = sec_scraper.get_recent_s4_filings(days_back=30, max_filings=1)
        
        if not filings:
            logger.warning("No S-4 filings found")
            return False
        
        filing = filings[0]
        logger.info(f"Testing with filing: {filing['company_name']}")
        
        # Scrape the content
        logger.info("Scraping filing content...")
        filing_content = sec_scraper.scrape_filing_content(filing)
        
        if not filing_content:
            logger.error("Failed to scrape filing content")
            return False
        
        logger.info(f"Content length: {len(filing_content['content'])} characters")
        logger.info(f"Content preview: {filing_content['content'][:500]}...")
        
        # Test AI rewriting
        if rewriter.is_enabled():
            logger.info("Testing AI rewriting...")
            rewritten = rewriter.rewrite_article(
                filing_content['title'],
                filing_content['content']
            )
            
            if rewritten:
                logger.info("✅ AI rewriting successful!")
                logger.info(f"Rewritten title: {rewritten['title']}")
                logger.info(f"Rewritten summary: {rewritten['summary']}")
                logger.info(f"Rewritten content preview: {rewritten['content'][:300]}...")
                
                # Check if it mentions specific companies
                content_lower = rewritten['content'].lower()
                if 'acquiring' in content_lower or 'merger' in content_lower or 'acquisition' in content_lower:
                    logger.info("✅ Content mentions acquisition/merger details")
                else:
                    logger.warning("⚠️ Content doesn't mention acquisition/merger details")
                
                return True
            else:
                logger.error("❌ AI rewriting failed")
                return False
        else:
            logger.warning("AI rewriting disabled - no OpenAI API key")
            return True
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Clean up
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    logger.info("Starting SEC API scraper test...")
    
    if test_sec_api_scraper():
        logger.info("🎉 Test completed successfully!")
    else:
        logger.error("❌ Test failed")
