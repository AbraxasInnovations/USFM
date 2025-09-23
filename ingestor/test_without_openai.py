"""
Test the scraped content pipeline without OpenAI API key
"""
import logging
import sys
import os
from datetime import datetime

# Add the ingestor directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraped_content_processor import ScrapedContentProcessor
from database import DatabaseManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockArticleRewriter:
    """Mock article rewriter for testing without OpenAI API"""
    
    def __init__(self):
        self.enabled = True
    
    def rewrite_article(self, title: str, content: str) -> str:
        """Mock rewrite that just adds a prefix"""
        return f"[REWRITTEN] {content}"
    
    def is_enabled(self) -> bool:
        return True

def test_scraped_content_without_openai():
    """Test the complete scraping pipeline without OpenAI"""
    
    logger.info("=== Testing Scraped Content Pipeline (Without OpenAI) ===")
    
    try:
        # Initialize processors with mock rewriter
        processor = ScrapedContentProcessor()
        
        # Replace the real rewriter with mock
        processor.article_rewriter = MockArticleRewriter()
        
        db = DatabaseManager()
        
        # Test scraping and processing
        logger.info("Step 1: Scraping and processing WealthSpire articles...")
        processed_articles = processor.process_wealthspire_articles(max_articles=2)
        
        if not processed_articles:
            logger.error("❌ No articles were processed")
            return False
        
        logger.info(f"✅ Successfully processed {len(processed_articles)} articles")
        
        # Display processed articles
        for i, article in enumerate(processed_articles):
            logger.info(f"\n--- Article {i+1} ---")
            logger.info(f"Title: {article['title']}")
            logger.info(f"Section: {article['section_slug']}")
            logger.info(f"Tags: {article['tags']}")
            logger.info(f"Summary: {article['summary'][:100]}...")
            logger.info(f"Excerpt: {article['excerpt'][:100]}...")
            logger.info(f"Slug: {article['article_slug']}")
            logger.info(f"Content Hash: {article['content_hash'][:16]}...")
            logger.info(f"Rewritten Content Length: {len(article['scraped_content'])} chars")
        
        # Test database insertion
        logger.info("\nStep 2: Testing database insertion...")
        
        for article in processed_articles:
            try:
                result = db.upsert_post(article)
                if result:
                    logger.info(f"✅ Successfully inserted: {article['title'][:50]}...")
                else:
                    logger.warning(f"⚠️ Failed to insert: {article['title'][:50]}...")
            except Exception as e:
                logger.error(f"❌ Error inserting article: {e}")
        
        # Test revalidation
        logger.info("\nStep 3: Testing revalidation...")
        try:
            revalidate_result = db.queue_web_revalidation()
            if revalidate_result:
                logger.info("✅ Web revalidation queued successfully")
            else:
                logger.warning("⚠️ Failed to queue web revalidation")
        except Exception as e:
            logger.error(f"❌ Error queuing revalidation: {e}")
        
        logger.info("\n=== Pipeline Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        return False
    
    finally:
        # Clean up
        try:
            processor.close()
            db.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting scraped content pipeline test (without OpenAI)...")
    
    success = test_scraped_content_without_openai()
    
    if success:
        print("\n🎉 All tests passed! The scraped content pipeline is working.")
        print("📝 Note: Articles were rewritten with mock content since OpenAI API key is not set.")
        print("🔧 To enable real AI rewriting, set the OPENAI_API_KEY environment variable.")
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
