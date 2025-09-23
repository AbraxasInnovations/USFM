"""
Twitter/X API client with rate limiting using OAuth 1.0a
"""
import requests
from requests_oauthlib import OAuth1
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        self.base_url = "https://api.twitter.com/2"
        self.oauth = OAuth1(
            api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        # Rate limiting tracking for FREE TIER
        self.rate_limits = {
            'tweets': {
                'limit': 1500,  # Free tier: 1,500 tweets per month
                'remaining': 1500,
                'reset_time': datetime.now() + timedelta(days=30)
            }
        }
        
        # Posting schedule (to stay within FREE TIER limits)
        self.posts_per_hour = 1  # Very conservative: 1 tweet per hour max
        self.posts_per_day = 2   # Maximum 2 tweets per day
        self.last_post_time = None
        self.posts_this_hour = 0
        self.posts_today = 0
        self.hour_start = datetime.now()
        self.day_start = datetime.now()
    
    def check_rate_limits(self) -> bool:
        """Check if we can post without hitting rate limits (FREE TIER)"""
        now = datetime.now()
        
        # Reset daily counter if new day
        if now.date() != self.day_start.date():
            self.posts_today = 0
            self.day_start = now
        
        # Reset hourly counter if new hour
        if now.hour != self.hour_start.hour:
            self.posts_this_hour = 0
            self.hour_start = now
        
        # Check daily limit (most restrictive for free tier)
        if self.posts_today >= self.posts_per_day:
            logger.warning(f"Daily limit reached ({self.posts_per_day} posts/day) - FREE TIER LIMIT")
            return False
        
        # Check hourly limit
        if self.posts_this_hour >= self.posts_per_hour:
            logger.warning(f"Hourly limit reached ({self.posts_per_hour} posts/hour)")
            return False
        
        # Check monthly rate limit
        if self.rate_limits['tweets']['remaining'] <= 0:
            reset_time = self.rate_limits['tweets']['reset_time']
            if now < reset_time:
                wait_time = (reset_time - now).total_seconds()
                logger.warning(f"Monthly rate limit reached. Reset in {wait_time:.0f} seconds")
                return False
        
        return True
    
    def update_rate_limits(self, response_headers: Dict):
        """Update rate limit tracking from API response headers"""
        if 'x-rate-limit-remaining' in response_headers:
            self.rate_limits['tweets']['remaining'] = int(response_headers['x-rate-limit-remaining'])
        
        if 'x-rate-limit-reset' in response_headers:
            reset_timestamp = int(response_headers['x-rate-limit-reset'])
            self.rate_limits['tweets']['reset_time'] = datetime.fromtimestamp(reset_timestamp)
    
    def create_tweet(self, text: str) -> Optional[Dict]:
        """Create a tweet with rate limiting"""
        if not self.check_rate_limits():
            return None
        
        try:
            # Ensure text is within character limit
            if len(text) > 280:
                text = text[:277] + "..."
            
            payload = {
                'text': text
            }
            
            response = requests.post(
                f"{self.base_url}/tweets",
                auth=self.oauth,
                json=payload,
                timeout=30
            )
            
            # Update rate limits from response
            self.update_rate_limits(response.headers)
            
            if response.status_code == 201:
                tweet_data = response.json()
                self.posts_this_hour += 1
                self.posts_today += 1
                self.last_post_time = datetime.now()
                
                logger.info(f"Successfully posted tweet: {tweet_data.get('data', {}).get('id')} (Daily: {self.posts_today}/{self.posts_per_day})")
                return tweet_data
            
            elif response.status_code == 429:
                # Rate limit exceeded
                logger.warning("Rate limit exceeded. Tweet not posted.")
                return None
            
            else:
                logger.error(f"Failed to post tweet. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Get authenticated user information"""
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                auth=self.oauth,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user info. Status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Twitter API connection"""
        try:
            user_info = self.get_user_info()
            if user_info:
                username = user_info.get('data', {}).get('username', 'Unknown')
                logger.info(f"Twitter API connection successful. Authenticated as: @{username}")
                return True
            return False
        except Exception as e:
            logger.error(f"Twitter API connection test failed: {e}")
            return False
