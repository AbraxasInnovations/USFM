"""
Private Equity Wire Content Processor
Processes PE Wire articles with AI rewriting and content enhancement
"""
import logging
import hashlib
import random
import re
from typing import Dict, List, Optional
from datetime import datetime
from database import DatabaseManager
from article_rewriter import ArticleRewriter

logger = logging.getLogger(__name__)

class PEWireContentProcessor:
    def __init__(self):
        self.db = DatabaseManager()
        self.rewriter = ArticleRewriter()
        
        # PE Wire specific configuration
        self.section_slug = 'lbo'
        self.origin_type = 'PEWIRE'
        self.source_name = 'Private Equity Wire'
        
        # Content processing settings
        self.min_content_length = 500
        self.max_content_length = 20000

    def process_article(self, article_data: Dict) -> Optional[Dict]:
        """
        Process a single PE Wire article with AI rewriting
        """
        try:
            logger.info(f"Processing PE Wire article: {article_data.get('title', 'Unknown')[:50]}...")
            
            # Validate article data
            if not self._validate_article_data(article_data):
                logger.warning("Invalid article data, skipping")
                return None
            
            # Check for duplicates
            content_hash = self._generate_content_hash(article_data)
            if self._is_duplicate(content_hash):
                logger.info(f"Duplicate article found, skipping: {article_data['title'][:50]}...")
                return None
            
            # Check for recent company coverage
            if self._has_recent_company_article(article_data):
                logger.info(f"Recent coverage of company found, skipping: {article_data['title'][:50]}...")
                return None
            
            # Extract company and deal information
            company_info = self._extract_company_info(article_data)
            
            # Rewrite the article with AI
            rewritten_content = self._rewrite_article(article_data, company_info)
            
            if not rewritten_content:
                logger.warning("Failed to rewrite article, skipping")
                return None
            
            # Generate article slug
            article_slug = self._generate_article_slug(article_data['title'], article_data['url'])
            
            # Check if slug already exists (additional safety check)
            if self._slug_exists(article_slug):
                logger.warning(f"Slug already exists, skipping: {article_slug}")
                return None
            
            # Prepare post data (only include fields that exist in database)
            post_data = {
                'title': rewritten_content.get('title', article_data['title']),
                'summary': rewritten_content.get('summary', ''),
                'excerpt': rewritten_content.get('excerpt', ''),
                'source_name': 'USFM',
                'source_url': article_data['url'],
                'section_slug': self.section_slug,
                'tags': rewritten_content.get('tags', []),
                'content_hash': content_hash,
                'status': 'published',
                'origin_type': self.origin_type,
                'image_url': self._get_pe_wire_image_url(),
                'scraped_content': rewritten_content.get('content', ''),
                'article_slug': article_slug
            }
            
            # Save to database
            post_id = self._save_post(post_data)
            
            if post_id:
                logger.info(f"Successfully processed PE Wire article: {post_data['title'][:50]}...")
                return {
                    'post_id': post_id,
                    'title': post_data['title'],
                    'article_slug': article_slug,
                    'company_name': company_info.get('company_name'),
                    'deal_value': company_info.get('deal_value')
                }
            else:
                logger.error("Failed to save post to database")
                return None
                
        except Exception as e:
            logger.error(f"Error processing PE Wire article: {e}")
            return None

    def _validate_article_data(self, article_data: Dict) -> bool:
        """Validate that article data has required fields"""
        required_fields = ['title', 'url', 'content']
        return all(field in article_data and article_data[field] for field in required_fields)

    def _generate_content_hash(self, article_data: Dict) -> str:
        """Generate content hash for deduplication"""
        # Use URL + title for more robust deduplication
        content = f"{article_data['url']}|{article_data['title']}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _is_duplicate(self, content_hash: str) -> bool:
        """Check if article already exists in database"""
        try:
            return self.db.post_exists(content_hash)
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            return False

    def _slug_exists(self, slug: str) -> bool:
        """Check if article slug already exists in database"""
        try:
            result = self.db.supabase.table('posts').select('id').eq('article_slug', slug).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking if slug exists: {e}")
            return False

    def _has_recent_company_article(self, article_data: Dict) -> bool:
        """Check if we've written about this company recently (within 7 days)"""
        try:
            # For now, skip company-based deduplication to simplify
            # This can be enhanced later with proper database queries
            return False
            
        except Exception as e:
            logger.error(f"Error checking for recent company articles: {e}")
            return False

    def _extract_company_patterns(self, title: str, content: str) -> List[str]:
        """Extract potential company names from title and content"""
        patterns = []
        
        # Common PE deal patterns
        pe_patterns = [
            r'(\w+(?:\s+\w+){0,3})\s+(?:acquires?|buys?|purchases?|takes?\s+over)',
            r'(?:acquires?|buys?|purchases?|takes?\s+over)\s+(\w+(?:\s+\w+){0,3})',
            r'(\w+(?:\s+\w+){0,3})\s+(?:investment|funding|round)',
            r'(\w+(?:\s+\w+){0,3})\s+(?:exits?|sells?|divests?)',
        ]
        
        text = f"{title} {content}"
        
        for pattern in pe_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Clean up the match
                clean_match = re.sub(r'[^\w\s]', '', match).strip()
                if len(clean_match) > 3 and len(clean_match) < 50:
                    patterns.append(clean_match)
        
        return list(set(patterns))  # Remove duplicates

    def _extract_company_info(self, article_data: Dict) -> Dict:
        """Extract company and deal information from article"""
        title = article_data['title']
        content = article_data.get('content', '')
        
        # Extract deal value
        deal_value = self._extract_deal_value(content)
        
        # Extract deal type
        deal_type = self._extract_deal_type(title, content)
        
        # Extract primary company name
        company_name = self._extract_primary_company(title, content)
        
        return {
            'company_name': company_name,
            'deal_value': deal_value,
            'deal_type': deal_type
        }

    def _extract_deal_value(self, content: str) -> Optional[str]:
        """Extract deal value from content"""
        # Look for monetary values
        value_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(?:billion|bn|million|mn|thousand|k)',
            r'(\d+(?:\.\d+)?)\s*(?:billion|bn|million|mn|thousand|k)\s*(?:dollars?|\$)',
            r'valued\s+at\s+\$(\d+(?:\.\d+)?)\s*(?:billion|bn|million|mn)',
            r'worth\s+\$(\d+(?:\.\d+)?)\s*(?:billion|bn|million|mn)'
        ]
        
        for pattern in value_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None

    def _extract_deal_type(self, title: str, content: str) -> Optional[str]:
        """Extract deal type from title and content"""
        text = f"{title} {content}".lower()
        
        deal_types = {
            'acquisition': ['acquires', 'acquisition', 'buys', 'purchase'],
            'investment': ['investment', 'funding', 'round', 'invests'],
            'exit': ['exit', 'sells', 'divests', 'ipo', 'public offering'],
            'merger': ['merger', 'merges', 'combines'],
            'lbo': ['leveraged buyout', 'lbo', 'take private']
        }
        
        for deal_type, keywords in deal_types.items():
            if any(keyword in text for keyword in keywords):
                return deal_type
        
        return None

    def _extract_primary_company(self, title: str, content: str) -> Optional[str]:
        """Extract primary company name from title"""
        # Simple extraction - look for capitalized words at the beginning
        words = title.split()
        if len(words) >= 2:
            # Take first 2-3 capitalized words as company name
            company_words = []
            for word in words[:3]:
                if word[0].isupper() and len(word) > 2:
                    company_words.append(word)
                else:
                    break
            
            if company_words:
                return ' '.join(company_words)
        
        return None

    def _rewrite_article(self, article_data: Dict, company_info: Dict) -> Optional[Dict]:
        """Rewrite article using AI"""
        try:
            # Use the article rewriter with correct arguments
            rewritten = self.rewriter.rewrite_article(
                title=article_data['title'],
                content=article_data['content']
            )
            
            if rewritten and isinstance(rewritten, dict):
                return rewritten
            else:
                logger.error("Article rewriter returned invalid result")
                return None
                
        except Exception as e:
            logger.error(f"Error rewriting article: {e}")
            return None

    def _generate_article_slug(self, title: str, url: str = None) -> str:
        """Generate unique URL-friendly slug from title"""
        # Clean and convert to slug
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        # Limit length
        if len(slug) > 40:  # Reduced to leave room for uniqueness suffix
            slug = slug[:40].rstrip('-')
        
        # Add uniqueness suffix using URL hash if provided
        if url:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            slug = f"{slug}-{url_hash}"
        
        return slug

    def _get_pe_wire_image_url(self) -> str:
        """Get a random SEC image URL (same as SEC scraper)"""
        # Use the same SEC images as the SEC scraper
        sec_images = [
            'sec1.jpg', 'sec2.jpg', 'sec3.jpg', 'sec4.jpg', 'sec8.jpg',
            'sec23.jpg', 'sec24.jpg', 'sec25.jpg', 'sec26.jpg', 
            'sec27.jpg', 'sec28.jpg', 'sec29.jpg'
        ]

        # Randomly select one
        selected_image = random.choice(sec_images)

        # Return the full URL path
        return f"/images/sec/{selected_image}"

    def _save_post(self, post_data: Dict) -> Optional[str]:
        """Save post to database"""
        try:
            # Use the existing database insert method
            return self.db.insert_post(post_data)
                
        except Exception as e:
            logger.error(f"Error saving post to database: {e}")
            return None

    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process multiple articles"""
        processed_articles = []
        
        for article in articles:
            try:
                result = self.process_article(article)
                if result:
                    processed_articles.append(result)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
        
        return processed_articles

    def close(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()
