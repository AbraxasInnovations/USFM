#!/usr/bin/env python3
"""
Main news ingestor script
Fetches financial news from RSS feeds and stores in Supabase
"""
import logging
import sys
import time
from datetime import datetime
from typing import List, Dict

from config import CONTENT_SOURCES, BATCH_SIZE
from database import DatabaseManager
from feed_reader import FeedReader
from content_processor import ContentProcessor
from delivery_manager import DeliveryManager
from scraped_content_processor import ScrapedContentProcessor
from sec_content_processor import SECContentProcessor
from smart_content_manager import SmartContentManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ingestor.log')
    ]
)

logger = logging.getLogger(__name__)

class NewsIngestor:
    def __init__(self):
        self.db = DatabaseManager()
        self.feed_reader = FeedReader()
        self.content_processor = ContentProcessor()
        self.delivery_manager = DeliveryManager()
        self.scraped_processor = ScrapedContentProcessor()
        self.sec_processor = SECContentProcessor()
        self.smart_content_manager = SmartContentManager()
        
        # Statistics
        self.stats = {
            'feeds_processed': 0,
            'entries_fetched': 0,
            'posts_created': 0,
            'posts_skipped': 0,
            'scraped_articles': 0,
            'sec_filings': 0,
            'fallback_articles_used': 0,
            'errors': 0
        }
    
    def get_all_sources(self) -> List[Dict]:
        """Get all configured content sources"""
        all_sources = []
        for category, sources in CONTENT_SOURCES.items():
            all_sources.extend(sources)
        return all_sources
    
    def process_feeds(self) -> List[Dict]:
        """Process all RSS feeds and return entries"""
        logger.info("Starting feed processing...")
        
        sources = self.get_all_sources()
        logger.info(f"Processing {len(sources)} sources")
        
        entries = self.feed_reader.fetch_all_feeds(sources)
        self.stats['feeds_processed'] = len(sources)
        self.stats['entries_fetched'] = len(entries)
        
        logger.info(f"Fetched {len(entries)} entries from {len(sources)} sources")
        return entries
    
    def process_entries(self, entries: List[Dict]) -> List[Dict]:
        """Process feed entries into post data"""
        logger.info("Processing entries into posts...")
        
        posts = []
        for entry in entries:
            try:
                source_config = entry.get('source_config', {})
                post_data = self.content_processor.process_feed_item(entry, source_config)
                
                if post_data:
                    posts.append(post_data)
                else:
                    self.stats['posts_skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                self.stats['errors'] += 1
                continue
        
        logger.info(f"Processed {len(posts)} posts from {len(entries)} entries")
        return posts
    
    def store_posts(self, posts: List[Dict]) -> List[str]:
        """Store posts in database and create deliveries"""
        logger.info(f"Storing {len(posts)} posts in database...")
        
        stored_posts = []
        
        # Process posts in batches
        for i in range(0, len(posts), BATCH_SIZE):
            batch = posts[i:i + BATCH_SIZE]
            logger.info(f"Processing batch {i//BATCH_SIZE + 1}/{(len(posts) + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            for post_data in batch:
                try:
                    # Insert post
                    post_id = self.db.insert_post(post_data)
                    
                    if post_id:
                        stored_posts.append(post_id)
                        self.stats['posts_created'] += 1
                        
                        # Create deliveries
                        deliveries = self.delivery_manager.process_deliveries(post_id, post_data)
                        
                        for delivery in deliveries:
                            self.db.insert_delivery(
                                post_id=post_id,
                                channel=delivery['channel'],
                                payload=delivery['payload']
                            )
                    else:
                        self.stats['posts_skipped'] += 1
                        
                except Exception as e:
                    logger.error(f"Error storing post: {e}")
                    self.stats['errors'] += 1
                    continue
            
            # Small delay between batches
            time.sleep(1)
        
        logger.info(f"Successfully stored {len(stored_posts)} posts")
        return stored_posts
    
    def process_content_with_smart_fallback(self, all_posts: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Process all posts and organize them by section with smart fallback logic
        """
        try:
            # Group posts by section
            posts_by_section = {}
            for post in all_posts:
                section = post.get('section_slug', 'cap')
                if section not in posts_by_section:
                    posts_by_section[section] = []
                posts_by_section[section].append(post)
            
            # Apply smart content management to each section
            smart_content = {}
            for section_slug, posts in posts_by_section.items():
                smart_posts = self.smart_content_manager.get_smart_content_for_section(section_slug, posts)
                smart_content[section_slug] = smart_posts
                
                # Count fallback articles used
                if len(smart_posts) > len(posts):
                    self.stats['fallback_articles_used'] += len(smart_posts) - len(posts)
            
            # Handle homepage content
            all_posts_for_homepage = [post for posts in smart_content.values() for post in posts]
            smart_content['homepage'] = self.smart_content_manager.get_smart_homepage_content(all_posts_for_homepage)
            
            logger.info(f"Smart content distribution: {[(section, len(posts)) for section, posts in smart_content.items()]}")
            return smart_content
            
        except Exception as e:
            logger.error(f"Error processing content with smart fallback: {e}")
            # Fallback to original logic
            return {'homepage': all_posts[:30]}
    
    def cleanup_old_data(self):
        """Clean up old data to manage storage"""
        logger.info("Cleaning up old data...")
        
        try:
            # Clean up posts older than 30 days
            deleted_count = self.db.cleanup_old_posts(days_to_keep=30)
            logger.info(f"Cleaned up {deleted_count} old posts")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def print_stats(self):
        """Print ingestion statistics"""
        logger.info("=== INGESTION STATISTICS ===")
        logger.info(f"Feeds processed: {self.stats['feeds_processed']}")
        logger.info(f"Entries fetched: {self.stats['entries_fetched']}")
        logger.info(f"Posts created: {self.stats['posts_created']}")
        logger.info(f"Posts skipped: {self.stats['posts_skipped']}")
        logger.info(f"Scraped articles: {self.stats['scraped_articles']}")
        logger.info(f"SEC S-4 filings: {self.stats['sec_filings']}")
        logger.info(f"Fallback articles used: {self.stats['fallback_articles_used']}")
        logger.info(f"Errors: {self.stats['errors']}")
        
        # Get recent posts count
        recent_count = self.db.get_recent_posts_count(hours=24)
        logger.info(f"Total posts in last 24h: {recent_count}")
    
    def run(self):
        """Main ingestion process"""
        start_time = datetime.now()
        logger.info(f"Starting news ingestion at {start_time}")
        
        try:
            # Process feeds
            entries = self.process_feeds()
            
            if not entries:
                logger.warning("No entries fetched from feeds")
                return
            
            # Process entries into posts
            posts = self.process_entries(entries)
            
            if not posts:
                logger.warning("No posts created from entries")
                return
            
            # Process scraped content (WealthSpire)
            logger.info("Processing scraped content from WealthSpire...")
            scraped_posts = self.scraped_processor.process_wealthspire_articles(max_articles=2)
            
            if scraped_posts:
                logger.info(f"Successfully processed {len(scraped_posts)} scraped articles")
                posts.extend(scraped_posts)
                self.stats['scraped_articles'] = len(scraped_posts)
            else:
                logger.warning("No scraped articles processed")
            
            # Process SEC S-4 filings
            logger.info("Processing SEC S-4 filings...")
            sec_posts = self.sec_processor.process_s4_filings(max_filings=2) # Process 2 S-4 filings
            
            if sec_posts:
                logger.info(f"Successfully processed {len(sec_posts)} SEC S-4 filings")
                posts.extend(sec_posts) # Add SEC posts to the main list
                self.stats['sec_filings'] = len(sec_posts)
            else:
                logger.warning("No SEC S-4 filings processed")
            
            # Store posts in database
            stored_posts = self.store_posts(posts)
            
            # Cleanup old data
            self.cleanup_old_data()
            
            # Print statistics
            self.print_stats()
            
            end_time = datetime.now()
            duration = end_time - start_time
            logger.info(f"Ingestion completed in {duration}")
            
        except Exception as e:
            logger.error(f"Fatal error during ingestion: {e}")
            self.stats['errors'] += 1
            raise
        
        finally:
            # Clean up resources
            self.db.close()
            self.feed_reader.close()
            self.content_processor.close()
            self.scraped_processor.close()
            self.sec_processor.close()
            self.smart_content_manager.close()

def main():
    """Main entry point"""
    try:
        ingestor = NewsIngestor()
        ingestor.run()
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
