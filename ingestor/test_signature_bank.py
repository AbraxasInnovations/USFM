#!/usr/bin/env python3
"""
Test if the AI correctly extracts Signature Bank of Georgia from the First Community Corp filing
"""
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestor.sec_scraper import SECScraper
from ingestor.article_rewriter import ArticleRewriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_signature_bank_extraction():
    """Test if AI extracts Signature Bank of Georgia correctly"""
    try:
        logger.info("Testing Signature Bank of Georgia extraction...")
        
        sec_scraper = SECScraper()
        rewriter = ArticleRewriter()
        
        # Get recent S-4 filings
        filings = sec_scraper.get_recent_s4_filings(days_back=30, max_filings=1)
        
        if not filings:
            logger.warning("No S-4 filings found")
            return
        
        filing = filings[0]
        logger.info(f"Testing with filing: {filing['company_name']}")
        
        # Scrape the content
        filing_content = sec_scraper.scrape_filing_content(filing)
        
        if not filing_content:
            logger.error("Failed to scrape filing content")
            return
        
        logger.info("=== CHECKING RAW CONTENT ===")
        content_lower = filing_content['content'].lower()
        
        if 'signature bank' in content_lower:
            logger.info("✅ Found 'Signature Bank' in raw content")
        else:
            logger.warning("❌ 'Signature Bank' NOT found in raw content")
            
        if 'georgia' in content_lower:
            logger.info("✅ Found 'Georgia' in raw content")
        else:
            logger.warning("❌ 'Georgia' NOT found in raw content")
            
        if 'first community' in content_lower:
            logger.info("✅ Found 'First Community' in raw content")
        else:
            logger.warning("❌ 'First Community' NOT found in raw content")
        
        logger.info(f"Content preview: {filing_content['content'][:500]}...")
        
        # Test AI rewriting
        if rewriter.is_enabled():
            logger.info("\n=== TESTING AI REWRITING ===")
            rewritten = rewriter.rewrite_article(
                filing_content['title'],
                filing_content['content']
            )
            
            if rewritten:
                logger.info("AI Rewritten Title:")
                logger.info(rewritten['title'])
                logger.info("\nAI Rewritten Summary:")
                logger.info(rewritten['summary'])
                logger.info("\nAI Rewritten Content (first 500 chars):")
                logger.info(rewritten['content'][:500])
                
                # Check if AI included specific companies
                rewritten_lower = rewritten['content'].lower()
                if 'signature bank' in rewritten_lower:
                    logger.info("✅ AI included 'Signature Bank'")
                else:
                    logger.warning("❌ AI did NOT include 'Signature Bank'")
                    
                if 'georgia' in rewritten_lower:
                    logger.info("✅ AI included 'Georgia'")
                else:
                    logger.warning("❌ AI did NOT include 'Georgia'")
                    
                if 'first community' in rewritten_lower:
                    logger.info("✅ AI included 'First Community'")
                else:
                    logger.warning("❌ AI did NOT include 'First Community'")
                    
                # Check for acquisition language
                if 'acquiring' in rewritten_lower or 'acquisition' in rewritten_lower:
                    logger.info("✅ AI mentioned acquisition/acquisition")
                else:
                    logger.warning("❌ AI did NOT mention acquisition")
            else:
                logger.error("AI rewriting failed")
        else:
            logger.warning("AI rewriting disabled")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    test_signature_bank_extraction()
