"""
Database operations for the news ingestor
"""
import hashlib
import logging
from typing import List, Dict, Optional
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Supabase URL and Service Role Key must be provided")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    def generate_content_hash(self, source_url: str, title: str) -> str:
        """Generate a content hash for deduplication"""
        content = f"{source_url}{title}".lower().strip()
        return hashlib.sha256(content.encode()).hexdigest()
    
    def post_exists(self, content_hash: str) -> bool:
        """Check if a post with the given content hash already exists"""
        try:
            result = self.supabase.table('posts').select('id').eq('content_hash', content_hash).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking if post exists: {e}")
            return False
    
    def insert_post(self, post_data: Dict) -> Optional[str]:
        """Insert a new post into the database"""
        try:
            # Generate content hash for deduplication
            content_hash = self.generate_content_hash(post_data['source_url'], post_data['title'])
            
            # Check if post already exists
            if self.post_exists(content_hash):
                logger.info(f"Post already exists, skipping: {post_data['title']}")
                return None
            
            # Add content hash to post data
            post_data['content_hash'] = content_hash
            
            # Insert the post
            result = self.supabase.table('posts').insert(post_data).execute()
            
            if result.data:
                post_id = result.data[0]['id']
                logger.info(f"Successfully inserted post: {post_data['title']} (ID: {post_id})")
                return post_id
            else:
                logger.error(f"Failed to insert post: {post_data['title']}")
                return None
                
        except Exception as e:
            logger.error(f"Error inserting post: {e}")
            return None
    
    def insert_delivery(self, post_id: str, channel: str, payload: Dict) -> bool:
        """Insert a delivery record for fan-out processing"""
        try:
            delivery_data = {
                'post_id': post_id,
                'channel': channel,
                'payload': payload,
                'status': 'queued'
            }
            
            result = self.supabase.table('deliveries').insert(delivery_data).execute()
            
            if result.data:
                logger.info(f"Successfully queued delivery for post {post_id} to {channel}")
                return True
            else:
                logger.error(f"Failed to queue delivery for post {post_id} to {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error inserting delivery: {e}")
            return False
    
    def get_recent_posts_count(self, hours: int = 24) -> int:
        """Get count of posts created in the last N hours"""
        try:
            from datetime import datetime, timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = self.supabase.table('posts').select('id', count='exact').gte('created_at', cutoff_time.isoformat()).execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error getting recent posts count: {e}")
            return 0
    
    def cleanup_old_posts(self, days_to_keep: int = 30) -> int:
        """Clean up posts older than specified days to manage storage"""
        try:
            from datetime import datetime, timedelta
            cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Get posts to delete
            result = self.supabase.table('posts').select('id').lt('created_at', cutoff_time.isoformat()).execute()
            
            if result.data:
                post_ids = [post['id'] for post in result.data]
                
                # Delete posts (cascade will handle deliveries)
                delete_result = self.supabase.table('posts').delete().in_('id', post_ids).execute()
                
                deleted_count = len(delete_result.data) if delete_result.data else 0
                logger.info(f"Cleaned up {deleted_count} old posts")
                return deleted_count
            
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up old posts: {e}")
            return 0
    
    def close(self):
        """Close database connections (Supabase client doesn't need explicit closing)"""
        # Supabase client doesn't require explicit closing
        # This method exists for consistency with other classes
        pass
