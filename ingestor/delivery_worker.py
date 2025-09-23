"""
Delivery worker for processing queued posts to Twitter/X
"""
import logging
import sys
import time
from datetime import datetime
from typing import List, Dict

from database import DatabaseManager
from delivery_manager import DeliveryManager
from config import X_ENABLED

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

class DeliveryWorker:
    def __init__(self):
        self.db = DatabaseManager()
        self.delivery_manager = DeliveryManager()
        
    def process_queued_deliveries(self, limit: int = 5) -> int:
        """Process queued deliveries for Twitter/X"""
        if not X_ENABLED:
            logger.info("X posting is disabled, skipping delivery processing")
            return 0
        
        try:
            # Get queued X deliveries
            response = self.db.supabase.table('deliveries').select('*').eq('channel', 'x').eq('status', 'queued').limit(limit).execute()
            
            if not response.data:
                logger.info("No queued X deliveries found")
                return 0
            
            processed_count = 0
            
            for delivery in response.data:
                try:
                    delivery_id = delivery['id']
                    payload = delivery['payload']
                    text = payload.get('text', '')
                    
                    if not text:
                        logger.warning(f"Delivery {delivery_id} has no text, skipping")
                        continue
                    
                    logger.info(f"Processing X delivery {delivery_id}: {text[:50]}...")
                    
                    # Attempt to post to Twitter
                    success = self.delivery_manager.send_x_post(text)
                    
                    if success:
                        # Update delivery status to completed
                        self.db.supabase.table('deliveries').update({
                            'status': 'completed',
                            'completed_at': datetime.now().isoformat()
                        }).eq('id', delivery_id).execute()
                        
                        processed_count += 1
                        logger.info(f"Successfully processed delivery {delivery_id}")
                        
                    else:
                        # Update delivery status to failed and increment attempts
                        attempts = delivery.get('attempts', 0) + 1
                        max_attempts = 5
                        
                        if attempts >= max_attempts:
                            status = 'failed'
                            logger.error(f"Delivery {delivery_id} failed after {max_attempts} attempts")
                        else:
                            status = 'queued'  # Retry later
                            logger.warning(f"Delivery {delivery_id} failed (attempt {attempts}/{max_attempts}), will retry")
                        
                        self.db.supabase.table('deliveries').update({
                            'status': status,
                            'attempts': attempts,
                            'last_attempt': datetime.now().isoformat()
                        }).eq('id', delivery_id).execute()
                    
                    # Add delay between posts to respect rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing delivery {delivery.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Processed {processed_count} X deliveries")
            return processed_count
            
        except Exception as e:
            logger.error(f"Error in delivery processing: {e}")
            return 0
    
    def run(self):
        """Main worker loop"""
        logger.info("Starting delivery worker...")
        
        try:
            # Test Twitter connection
            if X_ENABLED and self.delivery_manager.twitter_client:
                if not self.delivery_manager.twitter_client.test_connection():
                    logger.error("Twitter API connection test failed")
                    return
            
            # Process queued deliveries
            processed = self.process_queued_deliveries(limit=10)  # Process up to 10 at a time
            
            if processed > 0:
                logger.info(f"Successfully processed {processed} deliveries")
            else:
                logger.info("No deliveries to process")
                
        except Exception as e:
            logger.error(f"Error in delivery worker: {e}")

if __name__ == "__main__":
    worker = DeliveryWorker()
    worker.run()