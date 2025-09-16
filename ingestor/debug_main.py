"""
Debug version of the news ingestor with comprehensive logging
"""
import logging
import sys
import os
from datetime import datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def debug_environment():
    """Debug environment variables and dependencies"""
    logger.info("=== ENVIRONMENT DEBUG ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Check environment variables
    env_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY', 
        'REVALIDATE_URL',
        'REVALIDATE_SECRET',
        'X_ENABLED',
        'X_BEARER'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'SECRET' in var or 'BEARER' in var:
                logger.info(f"{var}: {value[:20]}... (hidden)")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.warning(f"{var}: NOT SET")
    
    logger.info("=== DEPENDENCY DEBUG ===")
    
    # Check package versions
    packages = ['supabase', 'httpx', 'requests', 'feedparser', 'beautifulsoup4']
    for package in packages:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            logger.info(f"{package}: {version}")
        except ImportError as e:
            logger.error(f"{package}: NOT INSTALLED - {e}")
        except Exception as e:
            logger.error(f"{package}: ERROR - {e}")

def debug_supabase_connection():
    """Debug Supabase connection step by step"""
    logger.info("=== SUPABASE CONNECTION DEBUG ===")
    
    try:
        logger.info("Step 1: Importing supabase...")
        from supabase import create_client, Client
        logger.info("✅ Supabase import successful")
        
        logger.info("Step 2: Getting environment variables...")
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url:
            logger.error("❌ SUPABASE_URL not set")
            return False
        if not supabase_key:
            logger.error("❌ SUPABASE_SERVICE_ROLE_KEY not set")
            return False
            
        logger.info(f"✅ Environment variables loaded")
        logger.info(f"URL: {supabase_url}")
        logger.info(f"Key: {supabase_key[:20]}...")
        
        logger.info("Step 3: Creating Supabase client...")
        supabase = create_client(supabase_url, supabase_key)
        logger.info("✅ Supabase client created successfully")
        
        logger.info("Step 4: Testing database connection...")
        result = supabase.table('sections').select('*').limit(1).execute()
        logger.info(f"✅ Database connection successful: {len(result.data)} sections found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase connection failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def debug_feed_reading():
    """Debug feed reading functionality"""
    logger.info("=== FEED READING DEBUG ===")
    
    try:
        from feed_reader import FeedReader
        logger.info("✅ FeedReader import successful")
        
        feed_reader = FeedReader()
        logger.info("✅ FeedReader instance created")
        
        # Test with a simple feed
        test_url = "https://feeds.marketwatch.com/marketwatch/topstories/"
        logger.info(f"Testing feed: {test_url}")
        
        entries = feed_reader.fetch_feed(test_url)
        logger.info(f"✅ Feed fetch successful: {len(entries)} entries")
        
        if entries:
            first_entry = entries[0]
            logger.info(f"Sample entry title: {first_entry.get('title', 'No title')}")
            logger.info(f"Sample entry link: {first_entry.get('link', 'No link')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Feed reading failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main debug function"""
    logger.info("🚀 Starting comprehensive debug session...")
    
    # Debug environment
    debug_environment()
    
    # Debug Supabase connection
    supabase_ok = debug_supabase_connection()
    
    # Debug feed reading
    feed_ok = debug_feed_reading()
    
    # Summary
    logger.info("=== DEBUG SUMMARY ===")
    logger.info(f"Supabase connection: {'✅ OK' if supabase_ok else '❌ FAILED'}")
    logger.info(f"Feed reading: {'✅ OK' if feed_ok else '❌ FAILED'}")
    
    if supabase_ok and feed_ok:
        logger.info("🎉 All systems operational!")
        return 0
    else:
        logger.error("💥 Some systems failed - check logs above")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
