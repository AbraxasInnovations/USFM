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
                    'tags': [tag.get('term', '') for tag in entry.get('tags', [])]
                }
                
                entries.append(entry_data)
                
            except Exception as e:
                logger.error(f"Error processing entry: {e}")
                continue
        
        return entries
    
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
