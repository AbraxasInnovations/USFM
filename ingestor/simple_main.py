"""
Simplified news ingestor using direct API calls
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any

from simple_database import SimpleDatabaseManager
from feed_reader import FeedReader
from content_processor import ContentProcessor
from delivery_manager import DeliveryManager
from config import CONTENT_SOURCES, MAX_POSTS_PER_SOURCE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_ingestion():
    logger.info("Starting simplified news ingestion process...")

    db_manager = SimpleDatabaseManager()
    feed_reader = FeedReader()
    delivery_manager = DeliveryManager()

    # Fetch sections for content classification
    sections = db_manager.get_sections()
    if not sections:
        logger.error("No sections found in the database. Exiting ingestion.")
        return
    content_processor = ContentProcessor(sections)

    all_raw_entries = feed_reader.fetch_all_feeds(CONTENT_SOURCES)
    logger.info(f"Collected {len(all_raw_entries)} raw entries from all sources.")

    processed_count = 0
    for entry in all_raw_entries:
        title = entry.get('title')
        link = entry.get('link')
        summary_html = entry.get('summary', entry.get('description', ''))
        published_date = entry.get('published')
        source_name = entry.get('source_name', 'Unknown Source')
        section_slug_hint = entry.get('section_slug_hint')
        tags_hint = entry.get('tags_hint', [])

        if not all([title, link, summary_html, published_date]):
            logger.warning(f"Skipping entry due to missing data: {entry.get('title', 'N/A')}")
            continue

        # Clean and process content
        summary = content_processor.clean_html(summary_html)
        excerpt = content_processor.truncate_excerpt(summary)
        content_hash = content_processor.generate_content_hash(link, title)
        
        # Extract tags and classify section
        extracted_tags = content_processor.extract_tags(title, summary, excerpt)
        # Combine hints with extracted tags, ensuring uniqueness
        final_tags = sorted(list(set(tags_hint + extracted_tags)))

        # Use hint for section if available, otherwise classify
        section_slug = section_slug_hint if section_slug_hint in content_processor.sections else content_processor.classify_section(title, summary, final_tags)

        # Convert published_date to ISO format if not already
        try:
            # feedparser often provides a parsed_parsed tuple
            if isinstance(published_date, time.struct_time):
                created_at = datetime.fromtimestamp(time.mktime(published_date)).isoformat() + "Z"
            else: # Assume it's a string, try to parse
                created_at = datetime.fromisoformat(published_date.replace('Z', '+00:00')).isoformat() + "Z"
        except Exception:
            created_at = datetime.now().isoformat() + "Z" # Fallback to now

        post_data = {
            'title': title,
            'summary': summary,
            'excerpt': excerpt,
            'source_name': source_name,
            'source_url': link,
            'section_slug': section_slug,
            'tags': final_tags,
            'content_hash': content_hash,
            'created_at': created_at,
            'origin_type': 'MEDIA' # Assuming RSS feeds are media for now
        }

        # Upsert post and queue deliveries
        new_post = db_manager.upsert_post(post_data)
        if new_post:
            processed_count += 1
            post_id = new_post['id']
            
            # Queue web revalidation
            db_manager.queue_delivery(post_id, 'web', {'action': 'revalidate', 'path': '/', 'tags': final_tags, 'section_slug': section_slug})
            
            # Prepare and queue X post
            x_payload = delivery_manager.prepare_x_post(title, summary, link)
            db_manager.queue_delivery(post_id, 'x', x_payload)
        
        if processed_count >= MAX_POSTS_PER_SOURCE * len(CONTENT_SOURCES):
            logger.info(f"Reached maximum posts per ingestion run ({MAX_POSTS_PER_SOURCE * len(CONTENT_SOURCES)}). Stopping.")
            break

    logger.info(f"News ingestion process finished. Processed {processed_count} new/updated posts.")
    
    # Trigger revalidation for homepage and all sections/tags after ingestion
    delivery_manager.revalidate_web(path='/')
    for section in sections:
        delivery_manager.revalidate_web(path=f'/section/{section["slug"]}')

if __name__ == "__main__":
    run_ingestion()
