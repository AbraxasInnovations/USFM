#!/usr/bin/env python3
"""
Simple test script to verify Supabase connection using direct API calls
"""
import os
import requests
import json

def test_supabase_api():
    print("Testing Supabase API connection...")
    
    # Get environment variables
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL') or "https://hznynbqpfsyddkdhsfak.supabase.co"
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {supabase_key[:20]}..." if supabase_key else "None")
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Missing Supabase credentials")
        return False
    
    try:
        # Test API endpoint
        api_url = f"{supabase_url}/rest/v1/sections"
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json'
        }
        
        print(f"Testing API endpoint: {api_url}")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API connection successful: {len(data)} sections found")
            return True
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_api()
    exit(0 if success else 1)
