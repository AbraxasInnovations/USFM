"""
Simplified database operations using direct API calls instead of Supabase client
"""
import hashlib
import logging
import requests
from typing import List, Dict, Optional
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

logger = logging.getLogger(__name__)

class SimpleDatabaseManager:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Supabase URL and Service Role Key must be provided")
        
        self.base_url = f"{SUPABASE_URL}/rest/v1"
        self.headers = {
            'apikey': SUPABASE_SERVICE_ROLE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
    
    def generate_content_hash(self, source_url: str, title: str) -> str:
        """Generate a content hash for deduplication"""
        content = f"{source_url}{title}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def post_exists(self, content_hash: str) -> bool:
        """Check if a post with the given content hash already exists"""
        try:
            url = f"{self.base_url}/posts"
            params = {'content_hash': f'eq.{content_hash}'}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return len(response.json()) > 0
        except Exception as e:
            logger.error(f"Error checking if post exists: {e}")
            return False
    
    def insert_post(self, post_data: Dict) -> Optional[Dict]:
        """Insert a new post"""
        try:
            url = f"{self.base_url}/posts"
            response = requests.post(url, headers=self.headers, json=post_data, timeout=10)
            response.raise_for_status()
            return response.json()[0] if response.json() else None
        except Exception as e:
            logger.error(f"Error inserting post: {e}")
            return None
    
    def upsert_post(self, post_data: Dict) -> Optional[Dict]:
        """Upsert a post (insert or update)"""
        try:
            # First check if post exists
            if self.post_exists(post_data.get('content_hash', '')):
                logger.info(f"Post already exists (content_hash: {post_data.get('content_hash')}), skipped.")
                return None
            
            # Insert new post
            return self.insert_post(post_data)
        except Exception as e:
            logger.error(f"Error upserting post: {e}")
            return None
    
    def get_sections(self) -> List[Dict]:
        """Get all sections"""
        try:
            url = f"{self.base_url}/sections"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching sections: {e}")
            return []
    
    def queue_delivery(self, post_id: str, channel: str, payload: Dict):
        """Queue a delivery for a given post and channel"""
        try:
            delivery_data = {
                'post_id': post_id,
                'channel': channel,
                'payload': payload,
                'status': 'queued' if channel == 'web' else 'held'
            }
            url = f"{self.base_url}/deliveries"
            response = requests.post(url, headers=self.headers, json=delivery_data, timeout=10)
            response.raise_for_status()
            logger.info(f"Queued delivery for post {post_id} to {channel}")
        except Exception as e:
            logger.error(f"Error queuing delivery for post {post_id} to {channel}: {e}")
    
    def get_queued_deliveries(self, channel: str = 'web', limit: int = 10) -> List[Dict]:
        """Get queued deliveries for a specific channel"""
        try:
            url = f"{self.base_url}/deliveries"
            params = {
                'channel': f'eq.{channel}',
                'status': 'eq.queued',
                'limit': limit
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching queued deliveries for channel {channel}: {e}")
            return []
    
    def update_delivery_status(self, delivery_id: str, status: str, error_message: str = None):
        """Update the status of a delivery"""
        try:
            update_data = {'status': status}
            if error_message:
                update_data['last_error'] = error_message
            
            url = f"{self.base_url}/deliveries"
            params = {'id': f'eq.{delivery_id}'}
            response = requests.patch(url, headers=self.headers, json=update_data, params=params, timeout=10)
            response.raise_for_status()
            logger.info(f"Updated delivery {delivery_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating delivery {delivery_id} status to {status}: {e}")
