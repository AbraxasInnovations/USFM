"""
RSS feed reader for the news ingestor
"""
import feedparser
import requests
import logging
import time
from typing import List, Dict, Optional
from config import REQUEST_DELAY, TIMEOUT, MAX_POSTS_PER_SOURCE

logger = logging.getLogger(__name__)

class FeedReader:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'US Financial Moves News Ingestor/1.0 (https://usfinancialmoves.com)'
        })
    
    def fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse an RSS feed"""
        try:
            logger.info(f"Fetching feed: {url}")
            
            response = self.session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"Feed parsing warnings for {url}: {feed.bozo_exception}")
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {url}")
                return None
            
            logger.info(f"Successfully fetched {len(feed.entries)} entries from {url}")
            return feed
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching feed {url}: {e}")
            return None
    
    def get_recent_entries(self, feed: feedparser.FeedParserDict, max_entries: int = None) -> List[Dict]:
        """Get recent entries from a feed"""
        if not feed or not feed.entries:
            return []
        
        if max_entries is None:
            max_entries = MAX_POSTS_PER_SOURCE
        
        entries = []
        
        for entry in feed.entries[:max_entries]:
            try:
                # Extract entry data
                entry_data = {
                    'title': entry.get('title', ''),
                    'description': entry.get('description', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'published_parsed': entry.get('published_parsed'),
                    'author': entry.get('author', ''),
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])],
                    'image_url': self._extract_image_url(entry)
                }
                
                entries.append(entry_data)
                
            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                continue
        
        return entries
    
    def _extract_image_url(self, entry) -> Optional[str]:
        """Extract image URL from RSS entry"""
        try:
            # Try different common image fields in RSS feeds
            image_fields = [
                'media_content',  # Media RSS
                'media_thumbnail',  # Media RSS thumbnail
                'enclosures',  # Standard RSS enclosures
                'image',  # Some feeds use this
                'thumbnail'  # Some feeds use this
            ]
            
            # Check media_content (Media RSS)
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        return media.get('url')
            
            # Check media_thumbnail (Media RSS)
            if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                return entry.media_thumbnail[0].get('url')
            
            # Check enclosures (standard RSS)
            if hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        return enclosure.get('href')
            
            # Check for image field
            if hasattr(entry, 'image') and entry.image:
                return entry.image
            
            # Check for thumbnail field
            if hasattr(entry, 'thumbnail') and entry.thumbnail:
                return entry.thumbnail
            
            # Try to extract from description HTML (fallback)
            description = entry.get('description', '') or entry.get('summary', '')
            if description:
                import re
                # Look for img tags
                img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', description, re.IGNORECASE)
                if img_match:
                    return img_match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting image URL: {e}")
            return None
    
    def fetch_all_feeds(self, sources: List[Dict]) -> List[Dict]:
        """Fetch all configured feeds"""
        all_entries = []
        
        for source in sources:
            try:
                feed = self.fetch_feed(source['url'])
                if feed:
                    entries = self.get_recent_entries(feed)
                    
                    # Add source configuration to each entry
                    for entry in entries:
                        entry['source_config'] = source
                    
                    all_entries.extend(entries)
                    logger.info(f"Added {len(entries)} entries from {source['name']}")
                
                # Add delay between requests to be respectful
                time.sleep(REQUEST_DELAY)
                
            except Exception as e:
                logger.error(f"Error processing source {source['name']}: {e}")
                continue
        
        logger.info(f"Total entries fetched: {len(all_entries)}")
        return all_entries
    
    def close(self):
        """Close the session"""
        self.session.close()
