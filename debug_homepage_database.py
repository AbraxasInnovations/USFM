#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def debug_homepage_database():
    """Debug what data the homepage is receiving from the database"""
    
    try:
        # Simulate the homepage's database query
        # The homepage uses: .limit(100) and .order('created_at', { ascending: false })
        
        # Get all posts from the API to see what's available
        api_response = requests.get("https://www.usfinancemoves.com/api/smart-content")
        if api_response.status_code != 200:
            print(f"API request failed: {api_response.status_code}")
            return
            
        api_data = api_response.json()
        
        # Get all posts from the API (this simulates the database query)
        all_posts = []
        for section, articles in api_data.get('smartContent', {}).items():
            all_posts.extend(articles)
        
        # Sort by created_at descending (like the homepage does)
        all_posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        print(f"Total posts available: {len(all_posts)}")
        
        # Show first 10 posts (to see what the homepage would get with .limit(100))
        print(f"\nFirst 10 posts (what homepage would get with .limit(100)):")
        for i, post in enumerate(all_posts[:10]):
            print(f"  {i+1}. {post['title'][:60]}...")
            print(f"     Section: {post.get('section_slug', 'unknown')}")
            print(f"     Origin: {post.get('origin_type', 'unknown')}")
            print(f"     Created: {post['created_at']}")
        
        # Check if any PE Wire articles are in the first 100 posts
        pe_wire_in_first_100 = [post for post in all_posts[:100] if post.get('origin_type') == 'PEWIRE']
        print(f"\nPE Wire articles in first 100 posts: {len(pe_wire_in_first_100)}")
        
        for post in pe_wire_in_first_100:
            print(f"  - {post['title'][:60]}...")
            print(f"    Section: {post.get('section_slug', 'unknown')}")
            print(f"    Created: {post['created_at']}")
        
        # Check all PE Wire articles regardless of position
        all_pe_wire = [post for post in all_posts if post.get('origin_type') == 'PEWIRE']
        print(f"\nTotal PE Wire articles: {len(all_pe_wire)}")
        
        for post in all_pe_wire:
            position = all_posts.index(post) + 1
            print(f"  - Position {position}: {post['title'][:60]}...")
            print(f"    Section: {post.get('section_slug', 'unknown')}")
            print(f"    Created: {post['created_at']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_homepage_database()
