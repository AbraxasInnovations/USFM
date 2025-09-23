"""
Configuration settings for the news ingestor
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Revalidation Configuration
REVALIDATE_URL = os.getenv('REVALIDATE_URL')
REVALIDATE_SECRET = os.getenv('REVALIDATE_SECRET')

# Social Media Configuration (for future use)
X_ENABLED = os.getenv('X_ENABLED', 'false').lower() == 'true'
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')

# Image Search Configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

# AI Content Rewriting Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
            'name': 'Bloomberg Markets',
            'url': 'https://feeds.bloomberg.com/markets/news.rss',
            'section': 'cap',
            'tags': ['markets', 'finance', 'bloomberg']
        }
    ],
    'mergers_acquisitions': [
        {
            'name': 'MarketWatch - Business',
            'url': 'https://feeds.marketwatch.com/marketwatch/business/',
            'section': 'ma',
            'tags': ['mergers', 'acquisitions', 'ma', 'business']
        }
    ],
    'regulatory': [
        {
            'name': 'MarketWatch - Top Stories',
            'url': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'section': 'reg',
            'tags': ['antitrust', 'regulatory', 'doj', 'sec']
        }
    ],
    'altcoin_news': [
        {
            'name': 'Cointelegraph - Altcoin News',
            'url': 'https://cointelegraph.com/rss/tag/altcoin',
            'section': 'rumor',
            'tags': ['crypto', 'altcoin', 'blockchain', 'digital-assets']
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
