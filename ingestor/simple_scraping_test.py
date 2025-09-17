"""
Simple test script for article scraping and rewriting (without database)
"""
import os
import logging
from dotenv import load_dotenv
from article_scraper import ArticleScraper
from content_rewriter import ContentRewriter

# Load environment variables from .env.local
load_dotenv('../.env.local')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraping_only():
    """Test just the scraping part without database"""
    
    # Test URL - using a Bloomberg article
    test_url = "https://www.bloomberg.com/news/articles/2025-09-16/argentine-assets-rebound-after-milei-strikes-more-moderate-tone"
    
    scraper = ArticleScraper()
    
    try:
        logger.info("=== Testing Article Scraping ===")
        
        # Step 1: Scrape the article
        logger.info("Step 1: Scraping article...")
        article_data = scraper.scrape_article(test_url)
        
        if not article_data:
            logger.error("Failed to scrape article")
            return
        
        logger.info(f"Scraped article: {article_data['title']}")
        logger.info(f"Content length: {len(article_data['content'])} characters")
        logger.info(f"Author: {article_data['author']}")
        logger.info(f"Publish date: {article_data['publish_date']}")
        
        # Print first 500 characters of content
        print("\n" + "="*80)
        print("SCRAPING TEST RESULTS")
        print("="*80)
        print(f"Title: {article_data['title']}")
        print(f"Author: {article_data['author']}")
        print(f"Publish Date: {article_data['publish_date']}")
        print(f"Content Length: {len(article_data['content'])} characters")
        print(f"Domain: {article_data['domain']}")
        print("\nFirst 500 characters of content:")
        print("-" * 40)
        print(article_data['content'][:500] + "...")
        print("="*80)
        
        return article_data
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return None
    
    finally:
        scraper.close()

def test_rewriting_only(article_data):
    """Test just the rewriting part"""
    
    if not article_data:
        logger.error("No article data to rewrite")
        return
    
    rewriter = ContentRewriter()
    
    try:
        logger.info("=== Testing Article Rewriting ===")
        
        # Step 1: Rewrite the article
        logger.info("Step 1: Rewriting article...")
        rewritten_data = rewriter.rewrite_article(article_data)
        
        if not rewritten_data:
            logger.error("Failed to rewrite article")
            return
        
        logger.info(f"Rewritten title: {rewritten_data['rewritten_title']}")
        logger.info(f"Rewritten content length: {len(rewritten_data['rewritten_content'])} characters")
        
        # Step 2: Create summary
        logger.info("Step 2: Creating summary...")
        summary = rewriter.create_summary(rewritten_data['rewritten_content'])
        logger.info(f"Summary: {summary}")
        
        # Print results
        print("\n" + "="*80)
        print("REWRITING TEST RESULTS")
        print("="*80)
        print(f"Original Title: {article_data['title']}")
        print(f"Rewritten Title: {rewritten_data['rewritten_title']}")
        print(f"Article Slug: {rewritten_data['slug']}")
        print(f"Summary: {summary}")
        print(f"Content Length: {len(rewritten_data['rewritten_content'])} characters")
        print("\nFirst 500 characters of rewritten content:")
        print("-" * 40)
        print(rewritten_data['rewritten_content'][:500] + "...")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Rewriting test failed: {e}")

if __name__ == "__main__":
    # Test scraping first
    article_data = test_scraping_only()
    
    # Test rewriting if scraping succeeded
    if article_data:
        test_rewriting_only(article_data)
