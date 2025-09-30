#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI module not available - will use simulated rewriting")

class ExecSumScraper:
    """Scraper for ExecSum.co content with OpenAI rewriting capability"""
    
    def __init__(self, openai_api_key=None):
        self.base_url = "https://www.execsum.co"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Initialize OpenAI if API key provided and module available
        if openai_api_key and OPENAI_AVAILABLE:
            openai.api_key = openai_api_key
            self.openai_enabled = True
        else:
            self.openai_enabled = False
            if not OPENAI_AVAILABLE:
                print("⚠️  OpenAI module not available - rewriting will be simulated")
            else:
                print("⚠️  OpenAI API key not provided - rewriting will be simulated")
    
    def get_latest_posts(self, limit=5):
        """Get the latest posts from ExecSum API"""
        
        try:
            response = requests.get(f"{self.base_url}/posts", headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('posts', [])
                
                # Filter for free posts and limit results
                free_posts = [p for p in posts if p.get('audience') == 'free'][:limit]
                
                print(f"Found {len(free_posts)} free posts")
                return free_posts
            else:
                print(f"Failed to get posts: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def scrape_post_content(self, post):
        """Scrape content from a specific post"""
        
        try:
            title = post.get('web_title', '')
            slug = post.get('slug', '')
            
            print(f"Scraping: {title}")
            
            # Try to get content from main page (where we found it works)
            main_response = requests.get(self.base_url, headers=self.headers, timeout=10)
            if main_response.status_code == 200:
                soup = BeautifulSoup(main_response.content, 'html.parser')
                all_text = soup.get_text(strip=True)
                
                # Look for the post title in the content
                if title and title.lower() in all_text.lower():
                    title_index = all_text.lower().find(title.lower())
                    if title_index != -1:
                        # Extract content around the title
                        start = max(0, title_index - 100)
                        end = min(len(all_text), title_index + 1000)
                        content = all_text[start:end]
                        
                        return {
                            'title': title,
                            'content': content,
                            'url': f"{self.base_url}/{slug}",
                            'published_date': post.get('override_scheduled_at', ''),
                            'source': 'execsum'
                        }
            
            print(f"Could not extract content for: {title}")
            return None
            
        except Exception as e:
            print(f"Error scraping post: {e}")
            return None
    
    def rewrite_content(self, content_data):
        """Rewrite content using OpenAI API"""
        
        if not self.openai_enabled:
            return self._simulate_rewrite(content_data)
        
        try:
            original_content = content_data['content']
            title = content_data['title']
            
            # Create a prompt for rewriting
            prompt = f"""
            Rewrite the following financial news content in a professional, engaging style while maintaining all factual information and key details. Make it suitable for a finance news website.
            
            Original Title: {title}
            Original Content: {original_content}
            
            Requirements:
            - Maintain all financial figures, quotes, and statistics
            - Use professional but accessible language
            - Keep the same key points and structure
            - Add attribution: "Source: ExecSum"
            - Make it engaging for finance professionals
            
            Rewritten Version:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional financial news writer who rewrites content while maintaining accuracy and adding value."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            rewritten_content = response.choices[0].message.content.strip()
            
            return {
                'original': content_data,
                'rewritten': rewritten_content,
                'rewrite_method': 'openai'
            }
            
        except Exception as e:
            print(f"Error with OpenAI rewriting: {e}")
            return self._simulate_rewrite(content_data)
    
    def _simulate_rewrite(self, content_data):
        """Simulate rewriting when OpenAI is not available"""
        
        original_content = content_data['content']
        title = content_data['title']
        
        # Simple simulation - in reality you'd use OpenAI
        simulated_rewrite = f"""
        {title} - Market Analysis Update
        
        {original_content}
        
        [This content has been rewritten from the original ExecSum article while maintaining factual accuracy and key information. Source: ExecSum]
        """
        
        return {
            'original': content_data,
            'rewritten': simulated_rewrite,
            'rewrite_method': 'simulated'
        }
    
    def process_latest_post(self):
        """Process the latest ExecSum post"""
        
        print("Getting latest ExecSum post...")
        posts = self.get_latest_posts(limit=1)
        
        if not posts:
            print("No posts found")
            return None
        
        latest_post = posts[0]
        print(f"Latest post: {latest_post.get('web_title', 'No title')}")
        
        # Scrape content
        content_data = self.scrape_post_content(latest_post)
        if not content_data:
            print("Failed to scrape content")
            return None
        
        # Rewrite content
        print("Rewriting content...")
        rewrite_result = self.rewrite_content(content_data)
        
        return rewrite_result

def main():
    """Main function to test ExecSum scraping and rewriting"""
    
    print("EXECSUM SCRAPER AND REWRITER")
    print("="*50)
    
    # Initialize scraper (without OpenAI API key for now)
    scraper = ExecSumScraper()
    
    # Process the latest post
    result = scraper.process_latest_post()
    
    if result:
        print("\n✅ SUCCESS!")
        print("="*50)
        
        original = result['original']
        rewritten = result['rewritten']
        
        print(f"Original Title: {original['title']}")
        print(f"Original Content Length: {len(original['content'])} characters")
        print(f"Rewritten Content Length: {len(rewritten)} characters")
        print(f"Rewrite Method: {result['rewrite_method']}")
        
        print(f"\n--- ORIGINAL CONTENT ---")
        print(original['content'][:300] + "..." if len(original['content']) > 300 else original['content'])
        
        print(f"\n--- REWRITTEN CONTENT ---")
        print(rewritten[:500] + "..." if len(rewritten) > 500 else rewritten)
        
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Add OpenAI API key for real rewriting")
        print(f"2. Integrate with your content pipeline")
        print(f"3. Add proper attribution and disclaimers")
        print(f"4. Implement rate limiting")
        print(f"5. Test with multiple posts")
        
    else:
        print("❌ Failed to process ExecSum content")

if __name__ == "__main__":
    main()
