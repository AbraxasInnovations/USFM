#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta

# Add the ingestor directory to the path
sys.path.append('ingestor')

try:
    from database import DatabaseManager
    
    db = DatabaseManager()
    
    print("=== DATABASE STATUS CHECK ===")
    print(f"Check time: {datetime.now()}")
    print()
    
    # Check recent PE Wire articles
    print("=== RECENT PE WIRE ARTICLES ===")
    result = db.supabase.table('posts').select('*').eq('origin_type', 'PEWIRE').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for post in result.data:
            print(f"Title: {post['title'][:60]}...")
            print(f"Created: {post['created_at']}")
            print(f"Section: {post['section_slug']}")
            print(f"Article Slug: {post.get('article_slug', 'None')}")
            print("---")
    else:
        print("No PE Wire articles found")
    
    print()
    
    # Check recent deliveries
    print("=== RECENT TWITTER DELIVERIES ===")
    result = db.supabase.table('deliveries').select('*').eq('channel', 'x').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for delivery in result.data:
            print(f"Status: {delivery['status']}")
            print(f"Created: {delivery['created_at']}")
            print(f"Payload: {delivery['payload'][:100]}...")
            print("---")
    else:
        print("No Twitter deliveries found")
    
    print()
    
    # Check LBO section articles
    print("=== LBO SECTION ARTICLES ===")
    result = db.supabase.table('posts').select('*').eq('section_slug', 'lbo').order('created_at', {'ascending': False}).limit(10).execute()
    if result.data:
        for post in result.data:
            print(f"Title: {post['title'][:60]}...")
            print(f"Origin: {post['origin_type']}")
            print(f"Created: {post['created_at']}")
            print("---")
    else:
        print("No LBO section articles found")
    
    print()
    
    # Check recent SEC articles
    print("=== RECENT SEC ARTICLES ===")
    result = db.supabase.table('posts').select('*').eq('origin_type', 'SCRAPED').order('created_at', {'ascending': False}).limit(5).execute()
    if result.data:
        for post in result.data:
            print(f"Title: {post['title'][:60]}...")
            print(f"Created: {post['created_at']}")
            print(f"Section: {post['section_slug']}")
            print(f"Article Slug: {post.get('article_slug', 'None')}")
            print("---")
    else:
        print("No SEC articles found")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
