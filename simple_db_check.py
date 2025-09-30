#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# This is a simple script to check the database via the API
# We'll use the smart content API to see what's in the database

try:
    print("=== CHECKING DATABASE VIA API ===")
    print(f"Check time: {datetime.now()}")
    print()
    
    # Check the smart content API
    response = requests.get('https://usfinancemoves.com/api/smart-content')
    
    if response.status_code == 200:
        data = response.json()
        
        print("=== SMART CONTENT STATUS ===")
        for section, posts in data.get('smartContent', {}).items():
            print(f"\n{section.upper()} SECTION:")
            for post in posts:
                print(f"  - {post['title'][:60]}...")
                print(f"    Origin: {post['origin_type']}")
                print(f"    Article Slug: {post.get('article_slug', 'None')}")
                print(f"    Should Tweet: {'YES' if post.get('article_slug') and post['origin_type'] in ['SCRAPED', 'PEWIRE'] else 'NO'}")
                print(f"    Created: {post['created_at']}")
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
