"""
Simple database test using direct HTTP requests to Supabase
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

def test_database_connection():
    """Test database connection using direct HTTP requests"""
    
    # Get environment variables
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    print(f"✅ Supabase URL: {supabase_url}")
    print(f"✅ Service Role Key: {supabase_key[:20]}...")
    
    # Test connection by querying posts table
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test query
        response = requests.get(
            f"{supabase_url}/rest/v1/posts?select=id,title&limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database connection successful!")
            print(f"✅ Found {len(data)} posts in database")
            if data:
                print(f"✅ Sample post: {data[0]['title'][:50]}...")
            return True
        else:
            print(f"❌ Database connection failed: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def create_test_article():
    """Create a test rewritten article in the database"""
    
    # Get environment variables
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return False
    
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    # Test article data
    test_article = {
        'title': 'Test: Argentine Assets Rise as Milei Shifts to Moderate Tone',
        'summary': 'Argentina\'s dollar bonds are rebounding as President Milei adopts a more cooperative approach, boosting optimism for the upcoming elections.',
        'excerpt': 'Argentina\'s dollar bonds are bouncing back from a recent slump after President Javier Milei took a more cooperative approach...',
        'source_name': 'www.bloomberg.com',
        'source_url': 'https://www.bloomberg.com/news/articles/2025-09-16/argentine-assets-rebound-after-milei-strikes-more-moderate-tone',
        'section_slug': 'cap',
        'tags': ['test', 'scraped', 'rewritten', 'argentina', 'milei'],
        'status': 'published',
        'origin_type': 'SCRAPED',
        'image_url': None,
        'scraped_content': 'Argentina\'s dollar bonds are bouncing back from a recent slump after President Javier Milei took a more cooperative approach while presenting next year\'s budget. This shift in tone has raised optimism that he may garner more support leading up to the upcoming midterm elections in the country. Investors were relieved to see Milei adopting a more conciliatory stance, which has helped ease concerns about the stability of Argentina\'s economy.',
        'article_slug': 'test-argentine-assets-rise-as-milei-shifts-to-moderate-tone',
        'content_hash': 'test_hash_12345'
    }
    
    try:
        response = requests.post(
            f"{supabase_url}/rest/v1/posts",
            headers=headers,
            data=json.dumps(test_article)
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Test article created successfully!")
            print(f"✅ Article ID: {data[0]['id']}")
            print(f"✅ Article URL: /article/{test_article['article_slug']}")
            return True
        else:
            print(f"❌ Failed to create test article: {response.status_code}")
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test article: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Database Connection ===")
    if test_database_connection():
        print("\n=== Creating Test Article ===")
        create_test_article()
    else:
        print("❌ Cannot create test article - database connection failed")
