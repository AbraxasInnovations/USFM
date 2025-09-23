"""
Test script for smart content management system
"""
import logging
import sys
import os
from datetime import datetime

# Add the ingestor directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_content_manager import SmartContentManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_smart_content_management():
    """Test the smart content management system"""
    
    logger.info("=== Testing Smart Content Management ===")
    
    try:
        # Initialize smart content manager
        manager = SmartContentManager()
        
        # Test 1: Get content summary
        logger.info("\n1. Getting current content summary...")
        summary = manager.get_content_summary()
        logger.info(f"Current content distribution: {summary}")
        
        # Test 2: Simulate different scenarios
        logger.info("\n2. Testing different content scenarios...")
        
        # Scenario 1: Plenty of new articles
        logger.info("\n--- Scenario 1: Plenty of new articles ---")
        new_articles_plenty = [
            {'id': '1', 'title': 'New M&A Article 1', 'section_slug': 'ma'},
            {'id': '2', 'title': 'New M&A Article 2', 'section_slug': 'ma'},
            {'id': '3', 'title': 'New M&A Article 3', 'section_slug': 'ma'},
            {'id': '4', 'title': 'New M&A Article 4', 'section_slug': 'ma'},
            {'id': '5', 'title': 'New M&A Article 5', 'section_slug': 'ma'},
        ]
        
        smart_content = manager.get_smart_content_for_section('ma', new_articles_plenty)
        logger.info(f"M&A section with 5 new articles: {len(smart_content)} articles returned")
        for i, article in enumerate(smart_content):
            logger.info(f"  {i+1}. {article['title']}")
        
        # Scenario 2: Some new articles (need fallbacks)
        logger.info("\n--- Scenario 2: Some new articles (need fallbacks) ---")
        new_articles_some = [
            {'id': '6', 'title': 'New LBO Article 1', 'section_slug': 'lbo'},
            {'id': '7', 'title': 'New LBO Article 2', 'section_slug': 'lbo'},
        ]
        
        smart_content = manager.get_smart_content_for_section('lbo', new_articles_some)
        logger.info(f"LBO section with 2 new articles: {len(smart_content)} articles returned")
        for i, article in enumerate(smart_content):
            logger.info(f"  {i+1}. {article['title']}")
        
        # Scenario 3: No new articles (all fallbacks)
        logger.info("\n--- Scenario 3: No new articles (all fallbacks) ---")
        new_articles_none = []
        
        smart_content = manager.get_smart_content_for_section('reg', new_articles_none)
        logger.info(f"Regulatory section with 0 new articles: {len(smart_content)} articles returned")
        for i, article in enumerate(smart_content):
            logger.info(f"  {i+1}. {article['title']}")
        
        # Test 3: Homepage content management
        logger.info("\n3. Testing homepage content management...")
        homepage_articles = [
            {'id': '8', 'title': 'Homepage Article 1', 'section_slug': 'cap'},
            {'id': '9', 'title': 'Homepage Article 2', 'section_slug': 'ma'},
            {'id': '10', 'title': 'Homepage Article 3', 'section_slug': 'lbo'},
        ]
        
        smart_homepage = manager.get_smart_homepage_content(homepage_articles)
        logger.info(f"Homepage with 3 new articles: {len(smart_homepage)} articles returned")
        
        # Test 4: Section thresholds
        logger.info("\n4. Testing section thresholds...")
        logger.info("Current section thresholds:")
        for section, threshold in manager.section_thresholds.items():
            logger.info(f"  {section}: {threshold} articles")
        
        logger.info("\n=== Smart Content Management Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Smart content management test failed: {e}")
        return False
    
    finally:
        # Clean up
        try:
            manager.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting smart content management test...")
    
    success = test_smart_content_management()
    
    if success:
        print("\n🎉 Smart content management test completed!")
        print("📝 This system ensures sections always stay populated with content.")
        print("🔄 New articles replace old ones, but fallbacks keep sections full.")
    else:
        print("\n❌ Smart content management test failed. Check the logs above.")
