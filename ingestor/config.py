"""
Configuration settings for the news ingestor
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Revalidation Configuration
REVALIDATE_URL = os.getenv('REVALIDATE_URL')
REVALIDATE_SECRET = os.getenv('REVALIDATE_SECRET')

# Social Media Configuration (for future use)
X_ENABLED = os.getenv('X_ENABLED', 'false').lower() == 'true'
X_BEARER = os.getenv('X_BEARER')

# Content Sources Configuration
CONTENT_SOURCES = {
    'financial_news': [
        {
            'name': 'MarketWatch - Top Stories',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'cap',
            'tags': ['markets', 'finance']
        },
        {
            'name': 'MarketWatch - Business',
            'url': 'https://feeds.marketwatch.com/marketwatch/business/',
            'section': 'cap',
            'tags': ['business', 'finance']
        }
    ],
    'mergers_acquisitions': [
        {
            'name': 'MarketWatch - M&A News',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'ma',
            'tags': ['mergers', 'acquisitions', 'ma']
        }
    ],
    'regulatory': [
        {
            'name': 'MarketWatch - Regulatory',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'reg',
            'tags': ['antitrust', 'regulatory', 'doj']
        }
    ]
}

# Content Processing Configuration
MAX_EXCERPT_WORDS = 75
MAX_POSTS_PER_SOURCE = 10  # Limit posts per source to stay within Supabase limits
REQUEST_DELAY = 2  # Delay between requests in seconds
TIMEOUT = 30  # Request timeout in seconds

# Database Configuration
BATCH_SIZE = 5  # Process posts in batches to avoid overwhelming the database
