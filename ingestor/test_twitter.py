"""
Test script for Twitter/X integration
"""
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestor.twitter_client import TwitterClient
from ingestor.delivery_manager import DeliveryManager
from ingestor.config import X_ENABLED, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

def test_twitter_connection():
    """Test Twitter API connection"""
    logger.info("=== Testing Twitter API Connection ===")
    
    if not X_ENABLED:
        logger.error("❌ X_ENABLED is not set to 'true'")
        return False
    
    if not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        logger.error("❌ OAuth 1.0a credentials are not configured")
        return False
    
    try:
        client = TwitterClient(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        
        # Test connection
        if client.test_connection():
            logger.info("✅ Twitter API connection successful!")
            return True
        else:
            logger.error("❌ Twitter API connection failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing Twitter connection: {e}")
        return False

def test_tweet_creation():
    """Test creating a tweet"""
    logger.info("\n=== Testing Tweet Creation ===")
    
    if not X_ENABLED or not all([X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET]):
        logger.error("❌ Twitter not configured, skipping tweet test")
        return False
    
    try:
        client = TwitterClient(X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        
        # Create a test tweet
        test_text = f"🧪 Test tweet from US Financial Moves - {datetime.now().strftime('%H:%M:%S')}"
        
        logger.info(f"Creating test tweet: {test_text}")
        result = client.create_tweet(test_text)
        
        if result:
            tweet_id = result.get('data', {}).get('id')
            logger.info(f"✅ Test tweet created successfully! Tweet ID: {tweet_id}")
            return True
        else:
            logger.warning("⚠️ Test tweet creation failed (likely rate limited)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error creating test tweet: {e}")
        return False

def test_delivery_manager():
    """Test delivery manager tweet formatting"""
    logger.info("\n=== Testing Delivery Manager ===")
    
    try:
        delivery_manager = DeliveryManager()
        
        # Test post data
        test_post = {
            'title': 'Test Financial News Article',
            'summary': 'This is a test summary for the financial news article.',
            'source_url': 'https://example.com/test-article',
            'section_slug': 'ma',
            'tags': ['merger', 'acquisition']
        }
        
        # Create X delivery
        x_delivery = delivery_manager.create_x_delivery(test_post)
        
        logger.info("✅ Delivery manager created X delivery:")
        logger.info(f"Tweet text: {x_delivery['text']}")
        logger.info(f"Status: {x_delivery['status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing delivery manager: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("Starting Twitter integration tests...")
    
    # Test 1: Connection
    connection_ok = test_twitter_connection()
    
    # Test 2: Delivery Manager
    delivery_ok = test_delivery_manager()
    
    # Test 3: Tweet Creation (only if connection is OK)
    tweet_ok = False
    if connection_ok:
        tweet_ok = test_tweet_creation()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Connection Test: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    logger.info(f"Delivery Manager: {'✅ PASS' if delivery_ok else '❌ FAIL'}")
    logger.info(f"Tweet Creation: {'✅ PASS' if tweet_ok else '❌ FAIL'}")
    
    if connection_ok and delivery_ok:
        logger.info("\n🎉 Twitter integration is ready!")
        logger.info("Next steps:")
        logger.info("1. Set X_ENABLED=true in your environment")
        logger.info("2. Deploy the delivery worker GitHub Action")
        logger.info("3. Monitor the delivery logs")
    else:
        logger.error("\n❌ Twitter integration needs attention")
        logger.error("Check your X_BEARER token and API permissions")

if __name__ == "__main__":
    main()
