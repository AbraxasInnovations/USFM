#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# This script checks the delivery status via the API
# We'll check if there are any Twitter deliveries in the system

try:
    print("=== CHECKING DELIVERY STATUS ===")
    print(f"Check time: {datetime.now()}")
    print()
    
    # Check if there are any recent articles that should have deliveries
    response = requests.get('https://usfinancemoves.com/api/smart-content')
    
    if response.status_code == 200:
        data = response.json()
        
        print("=== ARTICLES THAT SHOULD HAVE TWITTER DELIVERIES ===")
        tweetable_articles = []
        
        for section, posts in data.get('smartContent', {}).items():
            for post in posts:
                if (post.get('article_slug') and 
                    post['origin_type'] in ['SCRAPED', 'PEWIRE']):
                    tweetable_articles.append({
                        'title': post['title'],
                        'origin_type': post['origin_type'],
                        'article_slug': post['article_slug'],
                        'created_at': post['created_at']
                    })
        
        if tweetable_articles:
            print(f"Found {len(tweetable_articles)} articles that should be tweeted:")
            for article in tweetable_articles:
                print(f"  - {article['title'][:60]}...")
                print(f"    Origin: {article['origin_type']}")
                print(f"    Slug: {article['article_slug']}")
                print(f"    Created: {article['created_at']}")
                print()
        else:
            print("No articles found that should be tweeted")
        
        print("=== DIAGNOSIS ===")
        if tweetable_articles:
            print("❌ PROBLEM: There are articles that should be tweeted but aren't being tweeted")
            print("Possible causes:")
            print("1. X_ENABLED is set to false in GitHub Actions")
            print("2. Twitter API credentials are missing or invalid")
            print("3. Delivery worker is not creating Twitter deliveries")
            print("4. Twitter deliveries are being created but failing to post")
        else:
            print("✅ No articles found that should be tweeted")
            
    else:
        print(f"API Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
