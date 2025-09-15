#!/usr/bin/env python3
"""
Delivery worker for processing fan-out deliveries
"""
import logging
import sys
import time
from typing import List, Dict

from database import DatabaseManager
from delivery_manager import DeliveryManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('delivery_worker.log')
    ]
)

logger = logging.getLogger(__name__)

class DeliveryWorker:
    def __init__(self):
        self.db = DatabaseManager()
        self.delivery_manager = DeliveryManager()
        
        # Statistics
        self.stats = {
            'deliveries_processed': 0,
            'deliveries_sent': 0,
            'deliveries_failed': 0,
            'deliveries_held': 0
        }
    
    def get_queued_deliveries(self) -> List[Dict]:
        """Get all queued deliveries"""
        try:
            result = self.db.supabase.table('deliveries').select('*').eq('status', 'queued').execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Error fetching queued deliveries: {e}")
            return []
    
    def process_web_delivery(self, delivery: Dict) -> bool:
        """Process a web delivery"""
        try:
            payload = delivery['payload']
            paths = payload.get('paths', [])
            
            if not paths:
                logger.warning(f"No paths specified for web delivery {delivery['id']}")
                return False
            
            success = self.delivery_manager.send_web_revalidation(paths)
            return success
            
        except Exception as e:
            logger.error(f"Error processing web delivery {delivery['id']}: {e}")
            return False
    
    def process_x_delivery(self, delivery: Dict) -> bool:
        """Process an X delivery"""
        try:
            payload = delivery['payload']
            text = payload.get('text', '')
            
            if not text:
                logger.warning(f"No text specified for X delivery {delivery['id']}")
                return False
            
            success = self.delivery_manager.send_x_post(text)
            return success
            
        except Exception as e:
            logger.error(f"Error processing X delivery {delivery['id']}: {e}")
            return False
    
    def update_delivery_status(self, delivery_id: str, status: str, error_message: str = None):
        """Update delivery status in database"""
        try:
            update_data = {
                'status': status,
                'attempts': self.db.supabase.table('deliveries').select('attempts').eq('id', delivery_id).execute().data[0]['attempts'] + 1
            }
            
            if error_message:
                update_data['last_error'] = error_message
            
            self.db.supabase.table('deliveries').update(update_data).eq('id', delivery_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating delivery status: {e}")
    
    def process_delivery(self, delivery: Dict) -> bool:
        """Process a single delivery"""
        delivery_id = delivery['id']
        channel = delivery['channel']
        
        logger.info(f"Processing {channel} delivery {delivery_id}")
        
        try:
            success = False
            
            if channel == 'web':
                success = self.process_web_delivery(delivery)
            elif channel == 'x':
                success = self.process_x_delivery(delivery)
            else:
                logger.warning(f"Unknown delivery channel: {channel}")
                return False
            
            if success:
                self.update_delivery_status(delivery_id, 'sent')
                self.stats['deliveries_sent'] += 1
                logger.info(f"Successfully processed {channel} delivery {delivery_id}")
            else:
                # Check if we should retry or mark as failed
                attempts = delivery.get('attempts', 0)
                if attempts >= 5:
                    self.update_delivery_status(delivery_id, 'failed', 'Max retries exceeded')
                    self.stats['deliveries_failed'] += 1
                else:
                    self.update_delivery_status(delivery_id, 'queued', 'Retry scheduled')
                    self.stats['deliveries_held'] += 1
                
                logger.warning(f"Failed to process {channel} delivery {delivery_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing delivery {delivery_id}: {e}")
            self.update_delivery_status(delivery_id, 'failed', str(e))
            self.stats['deliveries_failed'] += 1
            return False
    
    def process_all_deliveries(self):
        """Process all queued deliveries"""
        logger.info("Starting delivery processing...")
        
        deliveries = self.get_queued_deliveries()
        logger.info(f"Found {len(deliveries)} queued deliveries")
        
        for delivery in deliveries:
            try:
                self.process_delivery(delivery)
                self.stats['deliveries_processed'] += 1
                
                # Small delay between deliveries
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing delivery {delivery['id']}: {e}")
                continue
        
        logger.info("Delivery processing completed")
    
    def print_stats(self):
        """Print delivery statistics"""
        logger.info("=== DELIVERY STATISTICS ===")
        logger.info(f"Deliveries processed: {self.stats['deliveries_processed']}")
        logger.info(f"Deliveries sent: {self.stats['deliveries_sent']}")
        logger.info(f"Deliveries failed: {self.stats['deliveries_failed']}")
        logger.info(f"Deliveries held: {self.stats['deliveries_held']}")
    
    def run(self):
        """Main delivery worker process"""
        logger.info("Starting delivery worker...")
        
        try:
            self.process_all_deliveries()
            self.print_stats()
            
        except Exception as e:
            logger.error(f"Fatal error in delivery worker: {e}")
            raise

def main():
    """Main entry point"""
    try:
        worker = DeliveryWorker()
        worker.run()
        
        # Exit with success code
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
