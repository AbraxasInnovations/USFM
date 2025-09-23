"""
Test script for full database integration with scraping and rewriting
"""
import os
import logging
from dotenv import load_dotenv
from article_scraper import ArticleScraper
from content_rewriter import ContentRewriter
from database import DatabaseManager

# Load environment variables
load_dotenv('../.env.local')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_pipeline():
    """Test the complete pipeline: scrape → rewrite → store in database"""
    
    # Test URL - using a Bloomberg article
    test_url = "https://www.bloomberg.com/news/articles/2025-09-16/argentine-assets-rebound-after-milei-strikes-more-moderate-tone"
    
    scraper = ArticleScraper()
    rewriter = ContentRewriter()
    db = DatabaseManager()
    
    try:
        logger.info("=== Testing Full Pipeline ===")
        
        # Step 1: Scrape the article
        logger.info("Step 1: Scraping article...")
        article_data = scraper.scrape_article(test_url)
        
        if not article_data:
            logger.error("Failed to scrape article")
            return
        
        logger.info(f"Scraped article: {article_data['title']}")
        
        # Step 2: Rewrite the article
        logger.info("Step 2: Rewriting article...")
        rewritten_data = rewriter.rewrite_article(article_data)
        
        if not rewritten_data:
            logger.error("Failed to rewrite article")
            return
        
        logger.info(f"Rewritten title: {rewritten_data['rewritten_title']}")
        
        # Step 3: Create summary
        logger.info("Step 3: Creating summary...")
        summary = rewriter.create_summary(rewritten_data['rewritten_content'])
        
        # Step 4: Store in database
        logger.info("Step 4: Storing in database...")
        
        # Create post data for database
        post_data = {
            'title': rewritten_data['rewritten_title'],
            'summary': summary,
            'excerpt': rewritten_data['rewritten_content'][:300] + "...",
            'source_name': rewritten_data['domain'],
            'source_url': rewritten_data['source_url'],
            'section_slug': 'cap',  # Capital markets
            'tags': ['test', 'scraped', 'rewritten', 'argentina', 'milei'],
            'status': 'published',
            'origin_type': 'SCRAPED',
            'image_url': None,
            'scraped_content': rewritten_data['rewritten_content'],
            'article_slug': rewritten_data['slug']
        }
        
        # Store in database
        result = db.upsert_post(post_data)
        if result:
            logger.info("✅ Successfully stored rewritten article in database!")
            logger.info(f"Article slug: {rewritten_data['slug']}")
            logger.info(f"Article URL: /article/{rewritten_data['slug']}")
        else:
            logger.error("❌ Failed to store article in database")
        
        # Print results
        print("\n" + "="*80)
        print("FULL PIPELINE TEST RESULTS")
        print("="*80)
        print(f"✅ Original Title: {article_data['title']}")
        print(f"✅ Rewritten Title: {rewritten_data['rewritten_title']}")
        print(f"✅ Article Slug: {rewritten_data['slug']}")
        print(f"✅ Article URL: /article/{rewritten_data['slug']}")
        print(f"✅ Summary: {summary}")
        print(f"✅ Content Length: {len(rewritten_data['rewritten_content'])} characters")
        print(f"✅ Database Status: {'SUCCESS' if result else 'FAILED'}")
        print("="*80)
        
        if result:
            print("\n🎉 SUCCESS! The rewritten article is now in your database!")
            print("📱 Check your live site - you should see the '📰 Rewritten Articles' section")
            print(f"🔗 Article URL: https://usfinancemoves.com/article/{rewritten_data['slug']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    
    finally:
        scraper.close()
        db.close()

if __name__ == "__main__":
    test_full_pipeline()
