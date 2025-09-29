"""
Delivery management for fan-out processing
"""
import requests
import logging
from typing import Dict, List
from config import REVALIDATE_URL, REVALIDATE_SECRET, X_ENABLED, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
from twitter_client import TwitterClient

logger = logging.getLogger(__name__)

class DeliveryManager:
    def __init__(self):
        self.revalidate_url = REVALIDATE_URL
        self.revalidate_secret = REVALIDATE_SECRET
        self.x_enabled = X_ENABLED
        
        # Initialize Twitter client if enabled
        self.twitter_client = None
        if self.x_enabled and X_API_KEY and X_API_SECRET and X_ACCESS_TOKEN and X_ACCESS_TOKEN_SECRET:
            self.twitter_client = TwitterClient(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
    
    def create_web_delivery(self, post_data: Dict) -> Dict:
        """Create a web revalidation delivery"""
        return {
            'action': 'revalidate',
            'paths': ['/', f"/section/{post_data['section_slug']}"]
        }
    
    def create_x_delivery(self, post_data: Dict) -> Dict:
        """Create an X/Twitter delivery (FREE TIER - very selective)"""
        # Only tweet high-priority content due to free tier limits
        if not self._should_tweet_post(post_data):
            return None
            
        # Format the post for X/Twitter
        title = post_data['title']
        summary = post_data.get('summary', '')
        section = post_data.get('section_slug', '').upper()
        origin_type = post_data.get('origin_type', '').upper()
        
        # Determine the URL to use
        if post_data.get('article_slug'):
            # For rewritten articles (SEC and PE Wire), link to our website
            url = f"https://www.usfinancemoves.com/article/{post_data['article_slug']}"
        else:
            # For other content, use original source URL
            url = post_data['source_url']
        
        # Fixed hashtags as requested
        hashtags = "#specialsituations #MA #PE #news #viral #finance"
        
        # Create the tweet text (X has a 280 character limit)
        tweet_text = f"📈 {title}"
        
        # Add summary if it fits
        if summary and len(summary) < 80:
            tweet_text += f"\n\n{summary}"
        
        # Add hashtags
        if len(tweet_text) + len(hashtags) + 25 < 280:  # Leave room for URL
            tweet_text += f"\n\n{hashtags}"
        
        # Add URL (shortened URLs are typically 23 characters)
        if len(tweet_text) + 25 < 280:  # Leave room for URL and spaces
            tweet_text += f"\n\n{url}"
        
        # Ensure we don't exceed character limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
        
        return {
            'text': tweet_text,
            'status': 'held' if not self.x_enabled else 'queued'
        }
    
    def process_deliveries(self, post_id: str, post_data: Dict) -> List[Dict]:
        """Process all deliveries for a post"""
        deliveries = []
        
        # Web delivery
        web_payload = self.create_web_delivery(post_data)
        deliveries.append({
            'channel': 'web',
            'payload': web_payload
        })
        
        # X delivery (if enabled and post qualifies)
        x_payload = self.create_x_delivery(post_data)
        if x_payload:  # Only add if post qualifies for tweeting
            deliveries.append({
                'channel': 'x',
                'payload': x_payload
            })
        
        return deliveries
    
    def _should_tweet_post(self, post_data: Dict) -> bool:
        """Determine if a post should be tweeted (FREE TIER - very selective)"""
        if not self.x_enabled:
            return False
            
        origin_type = post_data.get('origin_type', '').upper()
        article_slug = post_data.get('article_slug')
        
        # Only tweet rewritten articles with article_slug (not RSS feeds):
        # 1. SEC rewritten articles (SCRAPED origin type with article_slug)
        if origin_type == 'SCRAPED' and article_slug:
            return True
            
        # 2. PE Wire rewritten articles (PEWIRE origin type with article_slug)
        if origin_type == 'PEWIRE' and article_slug:
            return True
            
        # Skip everything else (RSS feeds, articles without slugs, etc.)
        return False
    
    def send_web_revalidation(self, paths: List[str]) -> bool:
        """Send web revalidation request"""
        if not self.revalidate_url or not self.revalidate_secret:
            logger.warning("Revalidation URL or secret not configured")
            return False
        
        try:
            payload = {
                'paths': paths,
                'secret': self.revalidate_secret
            }
            
            response = requests.post(
                self.revalidate_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully revalidated paths: {paths}")
                return True
            else:
                logger.error(f"Revalidation failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending revalidation request: {e}")
            return False
    
    def send_x_post(self, text: str) -> bool:
        """Send X/Twitter post"""
        if not self.x_enabled:
            logger.info("X posting is disabled")
            return False
        
        if not self.twitter_client:
            logger.warning("Twitter client not initialized")
            return False
        
        try:
            result = self.twitter_client.create_tweet(text)
            if result:
                logger.info("Successfully posted to X/Twitter")
                return True
            else:
                logger.warning("Failed to post to X/Twitter (likely rate limited)")
                return False
        except Exception as e:
            logger.error(f"Error posting to X/Twitter: {e}")
            return False
