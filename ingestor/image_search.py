"""
Image search module for finding relevant images based on content
Uses Unsplash API for high-quality, free images
"""
import requests
import logging
import re
from typing import Optional, List
from config import UNSPLASH_ACCESS_KEY

logger = logging.getLogger(__name__)

class ImageSearcher:
    def __init__(self):
        self.access_key = UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Client-ID {self.access_key}',
            'User-Agent': 'US Financial Moves News Ingestor/1.0'
        })
    
    def extract_keywords(self, title: str, description: str) -> List[str]:
        """Extract relevant keywords from title and description for image search"""
        text = f"{title} {description}".lower()
        
        # Remove common words and clean up
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
        keywords = [word for word in words if word not in stop_words]
        
        # Prioritize financial and business terms
        financial_terms = {
            'merger', 'acquisition', 'ipo', 'stock', 'market', 'trading', 'investment', 'finance',
            'banking', 'economy', 'revenue', 'profit', 'earnings', 'quarterly', 'annual',
            'cryptocurrency', 'bitcoin', 'ethereum', 'blockchain', 'fintech', 'startup',
            'venture', 'capital', 'private', 'equity', 'hedge', 'fund', 'analyst', 'ceo',
            'company', 'corporation', 'business', 'deal', 'partnership', 'agreement'
        }
        
        # Score keywords by relevance
        scored_keywords = []
        for keyword in keywords:
            score = 1
            if keyword in financial_terms:
                score = 3
            if len(keyword) > 5:  # Longer words are usually more specific
                score += 1
            scored_keywords.append((keyword, score))
        
        # Sort by score and return top keywords
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in scored_keywords[:5]]  # Top 5 keywords
    
    def search_image(self, title: str, description: str) -> Optional[str]:
        """Search for a relevant image based on title and description"""
        try:
            keywords = self.extract_keywords(title, description)
            if not keywords:
                return None
            
            # Create search query
            query = " ".join(keywords[:3])  # Use top 3 keywords
            query += " finance business"  # Add context
            
            # Search Unsplash
            params = {
                'query': query,
                'per_page': 10,
                'orientation': 'landscape',
                'content_filter': 'high'
            }
            
            response = self.session.get(f"{self.base_url}/search/photos", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                logger.warning(f"No images found for query: {query}")
                return None
            
            # Select the best image (first result is usually most relevant)
            image = results[0]
            image_url = image['urls']['regular']  # Use 'regular' size (1080px)
            
            logger.info(f"Found image for '{title[:50]}...': {image_url}")
            return image_url
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching for image: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in image search: {e}")
            return None
    
    def get_fallback_image(self, section: str) -> str:
        """Get a fallback image based on section"""
        fallback_images = {
            'ma': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=600&fit=crop',  # Handshake
            'lbo': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=600&fit=crop',  # Money
            'reg': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&h=600&fit=crop',  # Legal
            'cap': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600&fit=crop',  # Stock market
            'rumor': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop',  # Analysis
        }
        return fallback_images.get(section, fallback_images['cap'])
    
    def close(self):
        """Close the session"""
        self.session.close()
