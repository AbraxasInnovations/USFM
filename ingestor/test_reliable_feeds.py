#!/usr/bin/env python3
"""
Test script with more reliable RSS feeds
"""
import logging
import sys

from feed_reader import FeedReader
from content_processor import ContentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_reliable_feeds():
    """Test with more reliable RSS feeds"""
    logger.info("Testing with reliable RSS feeds...")
    
    feed_reader = FeedReader()
    
    # Test with different RSS feeds
    test_feeds = [
        {
            'name': 'Reuters Business',
            'url': 'https://feeds.reuters.com/reuters/businessNews',
            'section': 'cap',
            'tags': ['business', 'finance']
        },
        {
            'name': 'MarketWatch',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'cap', 
            'tags': ['markets', 'finance']
        }
    ]
    
    all_entries = []
    
    for feed_config in test_feeds:
        logger.info(f"Testing {feed_config['name']}: {feed_config['url']}")
        
        feed = feed_reader.fetch_feed(feed_config['url'])
        
        if feed and feed.entries:
            logger.info(f"✅ Successfully fetched {len(feed.entries)} entries from {feed_config['name']}")
            
            # Get a few entries
            entries = feed_reader.get_recent_entries(feed, max_entries=2)
            
            # Add source config to entries
            for entry in entries:
                entry['source_config'] = feed_config
            
            all_entries.extend(entries)
        else:
            logger.warning(f"❌ Failed to fetch from {feed_config['name']}")
    
    feed_reader.close()
    
    if all_entries:
        logger.info(f"Total entries collected: {len(all_entries)}")
        
        # Test content processing
        content_processor = ContentProcessor()
        
        for i, entry in enumerate(all_entries):
            logger.info(f"\nProcessing entry {i+1}:")
            logger.info(f"  Title: {entry.get('title', 'No title')[:60]}...")
            
            post_data = content_processor.process_feed_item(entry, entry['source_config'])
            
            if post_data:
                logger.info(f"  ✅ Processed successfully:")
                logger.info(f"    - Section: {post_data['section_slug']}")
                logger.info(f"    - Tags: {post_data['tags']}")
                logger.info(f"    - Excerpt: {post_data['excerpt'][:100]}...")
                logger.info(f"    - Source: {post_data['source_name']}")
            else:
                logger.warning(f"  ❌ Failed to process entry")
        
        return True
    else:
        logger.error("No entries were successfully fetched from any feed")
        return False

def main():
    """Run the test"""
    logger.info("Starting reliable feed tests...")
    
    try:
        result = test_reliable_feeds()
        
        if result:
            logger.info("\n✅ All tests passed! The ingestor system is working correctly.")
            sys.exit(0)
        else:
            logger.error("\n❌ Tests failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
