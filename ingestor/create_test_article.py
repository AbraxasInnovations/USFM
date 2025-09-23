"""
Create a test rewritten article and show what the page will look like
"""
import os
import logging
from dotenv import load_dotenv
from article_scraper import ArticleScraper
from content_rewriter import ContentRewriter

# Load environment variables
load_dotenv('../.env.local')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_article():
    """Create a test rewritten article"""
    
    # Test URL - using a Bloomberg article
    test_url = "https://www.bloomberg.com/news/articles/2025-09-16/argentine-assets-rebound-after-milei-strikes-more-moderate-tone"
    
    scraper = ArticleScraper()
    rewriter = ContentRewriter()
    
    try:
        logger.info("=== Creating Test Article ===")
        
        # Step 1: Scrape the article
        article_data = scraper.scrape_article(test_url)
        if not article_data:
            logger.error("Failed to scrape article")
            return
        
        # Step 2: Rewrite the article
        rewritten_data = rewriter.rewrite_article(article_data)
        if not rewritten_data:
            logger.error("Failed to rewrite article")
            return
        
        # Step 3: Create summary
        summary = rewriter.create_summary(rewritten_data['rewritten_content'])
        
        # Print the article page preview
        print("\n" + "="*80)
        print("📄 ARTICLE PAGE PREVIEW")
        print("="*80)
        print(f"URL: /article/{rewritten_data['slug']}")
        print(f"Title: {rewritten_data['rewritten_title']}")
        print(f"Category: {rewritten_data['domain'].upper()}")
        print(f"Author: {rewritten_data.get('author', 'Bloomberg')}")
        print(f"Date: {rewritten_data.get('publish_date', 'Today')}")
        print(f"Summary: {summary}")
        print("\n" + "-"*40)
        print("FULL ARTICLE CONTENT:")
        print("-"*40)
        print(rewritten_data['rewritten_content'])
        print("\n" + "-"*40)
        print("FOOTER:")
        print("-"*40)
        print(f"Originally published by {rewritten_data['domain']}")
        print(f"View original article → {rewritten_data['source_url']}")
        print("Tags: #test #scraped #rewritten #argentina #milei")
        print("="*80)
        
        # Show where to find the section
        print("\n" + "="*80)
        print("🔍 WHERE TO FIND THE NEW SECTION")
        print("="*80)
        print("The '📰 Rewritten Articles' section appears on your homepage")
        print("BUT only when there are articles with scraped_content in the database")
        print("\nTo see it:")
        print("1. Run the GitHub Actions to create rewritten articles")
        print("2. Or manually add a test article to your Supabase database")
        print("3. The section will appear below the main news grid")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    create_test_article()
