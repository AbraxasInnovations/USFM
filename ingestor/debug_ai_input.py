#!/usr/bin/env python3
"""
Debug what content the AI rewriter is actually receiving
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

def debug_ai_input():
    """Debug what content the AI rewriter is receiving"""
    try:
        logger.info("Debugging AI rewriter input...")
        
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
        
        logger.info("=== CONTENT BEING SENT TO AI ===")
        logger.info(f"Title: {filing_content['title']}")
        logger.info(f"Content length: {len(filing_content['content'])} characters")
        logger.info(f"Content preview (first 1000 chars):")
        logger.info(f"{filing_content['content'][:1000]}...")
        
        # Check if specific company names are in the content
        content_lower = filing_content['content'].lower()
        if 'pb bankshares' in content_lower:
            logger.info("✅ Found 'PB Bankshares' in content")
        else:
            logger.warning("❌ 'PB Bankshares' NOT found in content")
            
        if 'norwood' in content_lower:
            logger.info("✅ Found 'Norwood' in content")
        else:
            logger.warning("❌ 'Norwood' NOT found in content")
            
        if 'acquisition' in content_lower:
            logger.info("✅ Found 'acquisition' in content")
        else:
            logger.warning("❌ 'acquisition' NOT found in content")
        
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
                if 'pb bankshares' in rewritten_lower:
                    logger.info("✅ AI included 'PB Bankshares'")
                else:
                    logger.warning("❌ AI did NOT include 'PB Bankshares'")
                    
                if 'norwood' in rewritten_lower:
                    logger.info("✅ AI included 'Norwood'")
                else:
                    logger.warning("❌ AI did NOT include 'Norwood'")
            else:
                logger.error("AI rewriting failed")
        else:
            logger.warning("AI rewriting disabled")
            
    except Exception as e:
        logger.error(f"Debug failed: {e}")
    finally:
        if hasattr(sec_scraper, 'session'):
            sec_scraper.close()

if __name__ == "__main__":
    debug_ai_input()
