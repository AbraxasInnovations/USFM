#!/usr/bin/env python3

import requests
import json
from datetime import datetime, timedelta

def debug_homepage_data():
    """Debug what data the homepage is receiving vs the API"""
    
    try:
        # Get data from the API (what the API returns)
        api_response = requests.get("https://www.usfinancemoves.com/api/smart-content")
        if api_response.status_code != 200:
            print(f"API request failed: {api_response.status_code}")
            return
            
        api_data = api_response.json()
        
        # Check LBO section in API
        api_lbo = api_data.get('smartContent', {}).get('lbo', [])
        print(f"API LBO section: {len(api_lbo)} articles")
        
        if api_lbo:
            for article in api_lbo:
                print(f"  - {article['title'][:50]}...")
                print(f"    Origin: {article['origin_type']}")
                print(f"    Created: {article['created_at']}")
        
        # Get the actual homepage HTML to see what's rendered
        homepage_response = requests.get("https://www.usfinancemoves.com/")
        if homepage_response.status_code != 200:
            print(f"Homepage request failed: {homepage_response.status_code}")
            return
            
        # Check if LBO section is empty in the HTML
        html_content = homepage_response.text
        
        # Look for LBO section in HTML
        if 'LBO/PE' in html_content:
            # Find the LBO section
            lbo_start = html_content.find('LBO/PE')
            if lbo_start != -1:
                # Get the next 500 characters to see the articles-grid
                lbo_section = html_content[lbo_start:lbo_start+1000]
                print(f"\nLBO section in HTML:")
                print(lbo_section)
                
                # Check if articles-grid is empty
                if '<div class="articles-grid"></div>' in lbo_section:
                    print("\n❌ LBO section articles-grid is empty in HTML!")
                else:
                    print("\n✅ LBO section has articles in HTML")
        
        # Check all PE Wire articles in API
        all_pe_wire = []
        for section, articles in api_data.get('smartContent', {}).items():
            for article in articles:
                if article.get('origin_type') == 'PEWIRE':
                    all_pe_wire.append(article)
        
        print(f"\nTotal PE Wire articles in API: {len(all_pe_wire)}")
        for article in all_pe_wire:
            print(f"  - {article['title'][:50]}...")
            print(f"    Section: {article.get('section_slug', 'unknown')}")
            print(f"    Created: {article['created_at']}")
            
            # Check if it's recent (within 6 hours)
            created_time = datetime.fromisoformat(article['created_at'].replace('Z', '+00:00'))
            cutoff_time = datetime.now(created_time.tzinfo) - timedelta(hours=6)
            is_recent = created_time > cutoff_time
            print(f"    Recent (within 6h): {is_recent}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_homepage_data()
