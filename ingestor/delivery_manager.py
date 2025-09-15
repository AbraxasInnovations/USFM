"""
Delivery management for fan-out processing
"""
import requests
import logging
from typing import Dict, List
from config import REVALIDATE_URL, REVALIDATE_SECRET, X_ENABLED, X_BEARER

logger = logging.getLogger(__name__)

class DeliveryManager:
    def __init__(self):
        self.revalidate_url = REVALIDATE_URL
        self.revalidate_secret = REVALIDATE_SECRET
        self.x_enabled = X_ENABLED
        self.x_bearer = X_BEARER
    
    def create_web_delivery(self, post_data: Dict) -> Dict:
        """Create a web revalidation delivery"""
        return {
            'action': 'revalidate',
            'paths': ['/', f"/section/{post_data['section_slug']}"]
        }
    
    def create_x_delivery(self, post_data: Dict) -> Dict:
        """Create an X/Twitter delivery"""
        # Format the post for X/Twitter
        title = post_data['title']
        summary = post_data['summary']
        url = post_data['source_url']
        
        # Create the tweet text (X has a 280 character limit)
        tweet_text = f"{title}"
        if summary and len(summary) < 100:
            tweet_text += f" — {summary}"
        
        # Add URL (shortened URLs are typically 23 characters)
        if len(tweet_text) + 25 < 280:  # Leave room for URL and spaces
            tweet_text += f" {url}"
        
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
        
        # X delivery (if enabled or for future use)
        x_payload = self.create_x_delivery(post_data)
        deliveries.append({
            'channel': 'x',
            'payload': x_payload
        })
        
        return deliveries
    
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
        """Send X/Twitter post (placeholder for future implementation)"""
        if not self.x_enabled:
            logger.info("X posting is disabled")
            return False
        
        if not self.x_bearer:
            logger.warning("X bearer token not configured")
            return False
        
        # TODO: Implement X API posting
        logger.info(f"Would post to X: {text}")
        return False
