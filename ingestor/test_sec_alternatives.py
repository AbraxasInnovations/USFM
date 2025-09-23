#!/usr/bin/env python3
"""
Test different ways to access SEC filing content
"""
import logging
import sys
import os
import requests
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def test_different_approaches():
    """Test different approaches to access SEC content"""
    
    # Test 1: Try with different User-Agent
    logger.info("=== Test 1: Different User-Agent ===")
    headers1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    
    # Test 2: Try with SEC-compliant User-Agent
    logger.info("=== Test 2: SEC-compliant User-Agent ===")
    headers2 = {
        'User-Agent': 'US Financial Moves (contact@usfinancemoves.com)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    # Test 3: Try with minimal headers
    logger.info("=== Test 3: Minimal headers ===")
    headers3 = {
        'User-Agent': 'Mozilla/5.0 (compatible; SEC-EDGAR-Bot/1.0)',
    }
    
    # Test URL (using a recent S-4 filing)
    test_url = "https://www.sec.gov/Archives/edgar/data/932781/000155278125000294/0001552781-25-000294.txt"
    
    for i, headers in enumerate([headers1, headers2, headers3], 1):
        try:
            logger.info(f"Testing approach {i}...")
            response = requests.get(test_url, headers=headers, timeout=30)
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Content length: {len(response.text)}")
            
            if response.status_code == 200:
                logger.info("✅ SUCCESS! Got content")
                if 'pb bankshares' in response.text.lower() or 'norwood' in response.text.lower():
                    logger.info("✅ Found specific company names in content")
                logger.info(f"Content preview: {response.text[:200]}...")
                break
            else:
                logger.warning(f"❌ Failed with status {response.status_code}")
                if "Your Request Originates from an Undeclared Automated Tool" in response.text:
                    logger.warning("Still getting blocked")
                
        except Exception as e:
            logger.error(f"Error with approach {i}: {e}")
        
        time.sleep(2)  # Be respectful
    
    # Test 4: Try the HTML version instead of .txt
    logger.info("=== Test 4: Try HTML version ===")
    html_url = test_url.replace('.txt', '-index.htm')
    try:
        response = requests.get(html_url, headers=headers2, timeout=30)
        logger.info(f"HTML version status: {response.status_code}")
        if response.status_code == 200:
            logger.info("✅ HTML version works!")
            logger.info(f"Content preview: {response.text[:200]}...")
    except Exception as e:
        logger.error(f"HTML version error: {e}")

if __name__ == "__main__":
    test_different_approaches()
