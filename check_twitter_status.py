#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta

# Set up environment variables for local testing
os.environ['SUPABASE_URL'] = 'https://your-project.supabase.co'  # Replace with actual URL
os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'your-service-role-key'  # Replace with actual key

# Add the ingestor directory to the path
sys.path.append('ingestor')

try:
    from database import DatabaseManager
    
    db = DatabaseManager()
    
    print("=== TWITTER STATUS INVESTIGATION ===")
    print(f"Check time: {datetime.now()}")
    print()
    
    # Check recent SEC articles (should be tweeted)
    print("=== RECENT SEC ARTICLES (Should be tweeted) ===")
    result = db.supabase.table('posts').select('*').eq('origin_type', 'SCRAPED').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for post in result.data:
            print(f"Title: {post['title'][:60]}...")
            print(f"Created: {post['created_at']}")
            print(f"Article Slug: {post.get('article_slug', 'None')}")
            print(f"Should Tweet: {'YES' if post.get('article_slug') else 'NO'}")
            print("---")
    else:
        print("No SEC articles found")
    
    print()
    
    # Check recent PE Wire articles (should be tweeted)
    print("=== RECENT PE WIRE ARTICLES (Should be tweeted) ===")
    result = db.supabase.table('posts').select('*').eq('origin_type', 'PEWIRE').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for post in result.data:
            print(f"Title: {post['title'][:60]}...")
            print(f"Created: {post['created_at']}")
            print(f"Article Slug: {post.get('article_slug', 'None')}")
            print(f"Should Tweet: {'YES' if post.get('article_slug') else 'NO'}")
            print("---")
    else:
        print("No PE Wire articles found")
    
    print()
    
    # Check all Twitter deliveries
    print("=== ALL TWITTER DELIVERIES ===")
    result = db.supabase.table('deliveries').select('*').eq('channel', 'x').order('created_at', {'ascending': False}).limit(20).execute()
    if result.data:
        for delivery in result.data:
            print(f"ID: {delivery['id']}")
            print(f"Status: {delivery['status']}")
            print(f"Created: {delivery['created_at']}")
            print(f"Attempts: {delivery.get('attempts', 0)}")
            print(f"Text: {delivery['payload'].get('text', '')[:100]}...")
            print("---")
    else:
        print("No Twitter deliveries found")
    
    print()
    
    # Check queued deliveries specifically
    print("=== QUEUED TWITTER DELIVERIES ===")
    result = db.supabase.table('deliveries').select('*').eq('channel', 'x').eq('status', 'queued').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for delivery in result.data:
            print(f"ID: {delivery['id']}")
            print(f"Created: {delivery['created_at']}")
            print(f"Text: {delivery['payload'].get('text', '')[:100]}...")
            print("---")
    else:
        print("No queued Twitter deliveries found")
    
    print()
    
    # Check failed deliveries
    print("=== FAILED TWITTER DELIVERIES ===")
    result = db.supabase.table('deliveries').select('*').eq('channel', 'x').eq('status', 'failed').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for delivery in result.data:
            print(f"ID: {delivery['id']}")
            print(f"Created: {delivery['created_at']}")
            print(f"Attempts: {delivery.get('attempts', 0)}")
            print(f"Text: {delivery['payload'].get('text', '')[:100]}...")
            print("---")
    else:
        print("No failed Twitter deliveries found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
