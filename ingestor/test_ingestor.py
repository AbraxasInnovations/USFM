#!/usr/bin/env python3
"""
Test script for the news ingestor
"""
import logging
import sys
from datetime import datetime

from config import CONTENT_SOURCES
from feed_reader import FeedReader
from content_processor import ContentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_feed_reading():
    """Test RSS feed reading functionality"""
    logger.info("Testing feed reading...")
    
    feed_reader = FeedReader()
    
    # Test with a single source
    test_source = CONTENT_SOURCES['financial_news'][0]
    logger.info(f"Testing with source: {test_source['name']}")
    
    feed = feed_reader.fetch_feed(test_source['url'])
    
    if feed and feed.entries:
        logger.info(f"Successfully fetched {len(feed.entries)} entries")
        
        # Test processing a few entries
        entries = feed_reader.get_recent_entries(feed, max_entries=3)
        
        content_processor = ContentProcessor()
        
        for i, entry in enumerate(entries):
            logger.info(f"Processing entry {i+1}: {entry.get('title', 'No title')[:50]}...")
            
            post_data = content_processor.process_feed_item(entry, test_source)
            
            if post_data:
                logger.info(f"  - Title: {post_data['title']}")
                logger.info(f"  - Section: {post_data['section_slug']}")
                logger.info(f"  - Tags: {post_data['tags']}")
                logger.info(f"  - Excerpt length: {len(post_data['excerpt'])} chars")
            else:
                logger.warning(f"  - Failed to process entry")
        
        feed_reader.close()
        return True
    else:
        logger.error("Failed to fetch feed or no entries found")
        feed_reader.close()
        return False

def test_content_processing():
    """Test content processing functionality"""
    logger.info("Testing content processing...")
    
    processor = ContentProcessor()
    
    # Test data
    test_content = """
    This is a test article about a major merger between two technology companies. 
    The deal is worth $2.3 billion and involves artificial intelligence technology. 
    The acquisition will help the company expand its market presence and compete 
    with other tech giants in the AI space. The transaction is expected to close 
    in the second quarter of 2024, subject to regulatory approvals.
    """
    
    # Test excerpt extraction
    excerpt = processor.extract_excerpt(test_content, max_words=20)
    logger.info(f"Excerpt (20 words): {excerpt}")
    
    # Test section classification
    section = processor.classify_section("Tech Merger Deal", test_content, [])
    logger.info(f"Classified section: {section}")
    
    # Test tag extraction
    tags = processor.extract_tags("Tech Merger Deal", test_content, [])
    logger.info(f"Extracted tags: {tags}")
    
    return True

def main():
    """Run all tests"""
    logger.info("Starting ingestor tests...")
    
    tests = [
        ("Feed Reading", test_feed_reading),
        ("Content Processing", test_content_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n=== Running {test_name} Test ===")
        try:
            result = test_func()
            results.append((test_name, result))
            logger.info(f"{test_name} test: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            logger.error(f"{test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Print summary
    logger.info("\n=== Test Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("All tests passed! ✅")
        sys.exit(0)
    else:
        logger.error("Some tests failed! ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
