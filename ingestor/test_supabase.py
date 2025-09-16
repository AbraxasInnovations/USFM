#!/usr/bin/env python3
"""
Simple test script to verify Supabase connection
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env.local
load_dotenv('.env.local')

def test_supabase_connection():
    print("Testing Supabase connection...")
    
    # Get environment variables
    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_SERVICE_ROLE_KEY: {supabase_key[:20]}..." if supabase_key else "None")
    
    if not supabase_url or not supabase_key:
        print("❌ ERROR: Missing Supabase credentials")
        print("Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set")
        return False
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client created successfully")
        
        # Test a simple query
        result = supabase.table('sections').select('*').limit(1).execute()
        print(f"✅ Test query successful: {len(result.data)} sections found")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
