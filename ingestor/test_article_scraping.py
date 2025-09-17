"""
Test script for article scraping and rewriting
"""
import logging
from article_scraper import ArticleScraper
from content_rewriter import ContentRewriter
from database import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_article_scraping():
    """Test the full article scraping and rewriting pipeline"""
    
    # Test URL - using a Bloomberg article
    test_url = "https://www.bloomberg.com/news/articles/2025-09-16/argentine-assets-rebound-after-milei-strikes-more-moderate-tone"
    
    scraper = ArticleScraper()
    rewriter = ContentRewriter()
    db = DatabaseManager()
    
    try:
        logger.info("=== Testing Article Scraping & Rewriting ===")
        
        # Step 1: Scrape the article
        logger.info("Step 1: Scraping article...")
        article_data = scraper.scrape_article(test_url)
        
        if not article_data:
            logger.error("Failed to scrape article")
            return
        
        logger.info(f"Scraped article: {article_data['title']}")
        logger.info(f"Content length: {len(article_data['content'])} characters")
        
        # Step 2: Rewrite the article
        logger.info("Step 2: Rewriting article...")
        rewritten_data = rewriter.rewrite_article(article_data)
        
        if not rewritten_data:
            logger.error("Failed to rewrite article")
            return
        
        logger.info(f"Rewritten title: {rewritten_data['rewritten_title']}")
        logger.info(f"Rewritten content length: {len(rewritten_data['rewritten_content'])} characters")
        
        # Step 3: Create summary
        logger.info("Step 3: Creating summary...")
        summary = rewriter.create_summary(rewritten_data['rewritten_content'])
        logger.info(f"Summary: {summary}")
        
        # Step 4: Store in database (test)
        logger.info("Step 4: Storing in database...")
        
        # Create post data for database
        post_data = {
            'title': rewritten_data['rewritten_title'],
            'summary': summary,
            'excerpt': rewritten_data['rewritten_content'][:300] + "...",
            'source_name': rewritten_data['domain'],
            'source_url': rewritten_data['source_url'],
            'section_slug': 'cap',  # Capital markets
            'tags': ['test', 'scraped', 'rewritten'],
            'status': 'published',
            'origin_type': 'SCRAPED',
            'image_url': None,
            'scraped_content': rewritten_data['rewritten_content'],
            'article_slug': rewritten_data['slug']
        }
        
        # Store in database
        result = db.upsert_post(post_data)
        if result:
            logger.info("Successfully stored rewritten article in database")
        else:
            logger.error("Failed to store article in database")
        
        # Print results
        print("\n" + "="*80)
        print("SCRAPING & REWRITING TEST RESULTS")
        print("="*80)
        print(f"Original Title: {article_data['title']}")
        print(f"Rewritten Title: {rewritten_data['rewritten_title']}")
        print(f"Article Slug: {rewritten_data['slug']}")
        print(f"Summary: {summary}")
        print(f"Content Length: {len(rewritten_data['rewritten_content'])} characters")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    
    finally:
        scraper.close()
        db.close()

if __name__ == "__main__":
    test_article_scraping()
