"""
Content processing utilities for the news ingestor
"""
import re
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from config import MAX_EXCERPT_WORDS
from image_search import ImageSearcher

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        self.max_excerpt_words = MAX_EXCERPT_WORDS
        self.image_searcher = ImageSearcher()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        return text
    
    def extract_excerpt(self, content: str, max_words: int = None) -> str:
        """Extract and limit excerpt to specified word count"""
        if not content:
            return ""
        
        if max_words is None:
            max_words = self.max_excerpt_words
        
        # Clean the content
        content = self.clean_text(content)
        
        # Split into words
        words = content.split()
        
        # Truncate if necessary
        if len(words) > max_words:
            excerpt = ' '.join(words[:max_words])
            # Add ellipsis if truncated
            if not excerpt.endswith(('.', '!', '?')):
                excerpt += '...'
        else:
            excerpt = content
        
        return excerpt
    
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content"""
        if not html_content:
            return ""
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up the text
            text = self.clean_text(text)
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return html_content
    
    def generate_summary(self, title: str, content: str) -> str:
        """Generate a summary from title and content"""
        # For now, we'll use a simple approach
        # In the future, this could be enhanced with AI summarization
        
        if not content:
            return title
        
        # Try to extract the first sentence or two
        sentences = re.split(r'[.!?]+', content)
        
        if sentences and len(sentences[0]) > 10:
            summary = sentences[0].strip()
            if not summary.endswith(('.', '!', '?')):
                summary += '.'
            return summary
        
        # Fallback to title
        return title
    
    def classify_section(self, title: str, content: str, source_tags: List[str]) -> str:
        """Classify content into appropriate section based on keywords"""
        text = f"{title} {content}".lower()
        
        # M&A keywords
        ma_keywords = ['merger', 'acquisition', 'acquire', 'merge', 'takeover', 'buyout', 'deal']
        if any(keyword in text for keyword in ma_keywords):
            return 'ma'
        
        # LBO/PE keywords
        lbo_keywords = ['private equity', 'lbo', 'leveraged buyout', 'pe firm', 'private equity firm', 'kohlberg', 'kkr', 'blackstone', 'carlyle', 'apollo', 'bain capital', 'tpg', 'warburg pincus', 'general atlantic', 'silver lake', 'thoma bravo', 'buyout', 'going private', 'take private']
        if any(keyword in text for keyword in lbo_keywords):
            return 'lbo'
        
        # Regulatory keywords
        reg_keywords = ['antitrust', 'ftc', 'doj', 'regulatory', 'approval', 'investigation', 'settlement', 'federal trade commission', 'department of justice', 'sec filing', 'regulatory approval', 'antitrust review', 'merger review', 'competition', 'monopoly', 'oligopoly', 'regulatory compliance', 'government approval']
        if any(keyword in text for keyword in reg_keywords):
            return 'reg'
        
        # Crypto/Altcoin keywords
        crypto_keywords = ['crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'altcoin', 'blockchain', 'defi', 'nft', 'token', 'digital asset']
        if any(keyword in text for keyword in crypto_keywords):
            return 'rumor'
        
        # Capital markets keywords
        cap_keywords = ['ipo', 'public offering', 'stock', 'equity', 'debt', 'bond', 'securities', 'trading']
        if any(keyword in text for keyword in cap_keywords):
            return 'cap'
        
        # Default to capital markets for general financial news
        return 'cap'
    
    def extract_tags(self, title: str, content: str, source_tags: List[str]) -> List[str]:
        """Extract relevant tags from content"""
        text = f"{title} {content}".lower()
        tags = set(source_tags)  # Start with source tags
        
        # Common financial tags
        tag_keywords = {
            'ai': ['artificial intelligence', 'ai', 'machine learning', 'ml'],
            'tech': ['technology', 'tech', 'software', 'digital', 'cyber'],
            'healthcare': ['healthcare', 'medical', 'pharmaceutical', 'biotech'],
            'energy': ['energy', 'oil', 'gas', 'renewable', 'solar', 'wind'],
            'finance': ['banking', 'financial', 'finance', 'investment'],
            'retail': ['retail', 'consumer', 'e-commerce', 'shopping'],
            'automotive': ['automotive', 'auto', 'car', 'vehicle'],
            'real-estate': ['real estate', 'property', 'housing', 'commercial'],
            'acquisition': ['acquisition', 'acquire', 'buyout'],
            'merger': ['merger', 'merge', 'consolidation'],
            'ipo': ['ipo', 'public offering', 'going public'],
            'antitrust': ['antitrust', 'competition', 'monopoly'],
            'regulatory': ['regulatory', 'regulation', 'compliance'],
            'crypto': ['crypto', 'cryptocurrency', 'bitcoin', 'ethereum', 'altcoin', 'blockchain'],
            'defi': ['defi', 'decentralized finance', 'yield farming', 'liquidity'],
            'nft': ['nft', 'non-fungible token', 'digital collectible'],
            'trading': ['trading', 'exchange', 'market', 'price', 'pump', 'rally']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.add(tag)
        
        # Limit to 5 tags to keep it manageable
        return list(tags)[:5]
    
    def process_feed_item(self, item: Dict, source_config: Dict) -> Optional[Dict]:
        """Process a single RSS feed item into a post"""
        try:
            # Extract basic information
            title = self.clean_text(item.get('title', ''))
            if not title:
                logger.warning("No title found in feed item")
                return None
            
            # Extract content
            content = item.get('description', '') or item.get('summary', '')
            if content:
                content = self.extract_text_from_html(content)
            
            # Extract excerpt
            excerpt = self.extract_excerpt(content)
            
            # Generate summary
            summary = self.generate_summary(title, content)
            
            # Classify section
            section = self.classify_section(title, content, source_config.get('tags', []))
            
            # Extract tags
            tags = self.extract_tags(title, content, source_config.get('tags', []))
            
            # Get source information
            source_name = source_config.get('name', 'Unknown Source')
            source_url = item.get('link', '')
            
            if not source_url:
                logger.warning(f"No source URL found for item: {title}")
                return None
            
            # Get image URL - try RSS first, then search if not available
            image_url = item.get('image_url')
            
            if not image_url:
                # Search for relevant image based on content
                image_url = self.image_searcher.search_image(title, content)
                
                if not image_url:
                    # Use fallback image based on section
                    image_url = self.image_searcher.get_fallback_image(section)
            
            # Determine origin type based on source
            origin_type = 'RSS'
            if 'cointelegraph' in source_name.lower() or 'crypto' in source_name.lower() or 'altcoin' in source_name.lower():
                origin_type = 'CRYPTO'
            elif 'sec' in source_name.lower() or 'edgar' in source_name.lower():
                origin_type = 'SEC'
            elif 'doj' in source_name.lower() or 'ftc' in source_name.lower():
                origin_type = 'USGOV'
            
            # Create post data
            post_data = {
                'title': title,
                'summary': summary,
                'excerpt': excerpt,
                'source_name': source_name,
                'source_url': source_url,
                'section_slug': section,
                'tags': tags,
                'status': 'published',
                'origin_type': origin_type,
                'image_url': image_url
            }
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error processing feed item: {e}")
            return None
    
    def close(self):
        """Close resources"""
        if hasattr(self, 'image_searcher'):
            self.image_searcher.close()
