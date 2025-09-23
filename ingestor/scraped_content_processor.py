"""
Content processor for scraped articles that combines web scraping with AI rewriting
"""
import logging
import hashlib
from typing import Dict, Optional, List
from datetime import datetime
from web_scraper import WebScraper
from article_rewriter import ArticleRewriter
from content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class ScrapedContentProcessor:
    def __init__(self):
        self.web_scraper = WebScraper()
        self.article_rewriter = ArticleRewriter()
        self.content_processor = ContentProcessor()

    def process_wealthspire_articles(self, max_articles: int = 3) -> List[Dict]:
        """
        Scrape articles from wealthspire.com and process them with AI rewriting
        """
        try:
            logger.info(f"Starting WealthSpire scraping and processing (max {max_articles} articles)")
            
            # Scrape articles from wealthspire.com
            scraped_articles = self.web_scraper.scrape_wealthspire(max_articles)
            
            if not scraped_articles:
                logger.warning("No articles scraped from WealthSpire")
                return []
            
            processed_articles = []
            
            for i, article in enumerate(scraped_articles):
                try:
                    logger.info(f"Processing article {i+1}/{len(scraped_articles)}: {article['title'][:50]}...")
                    
                    # Rewrite the article content
                    rewritten_content = self.article_rewriter.rewrite_article(
                        title=article['title'],
                        content=article['content']
                    )
                    
                    if not rewritten_content:
                        logger.warning(f"Failed to rewrite article: {article['title']}")
                        continue
                    
                    # Generate slug from title
                    article_slug = self._generate_slug(article['title'])
                    
                    # Create content hash for deduplication
                    content_hash = self._create_content_hash(article['title'], rewritten_content)
                    
                    # Process into post format
                    post_data = {
                        'title': article['title'],
                        'summary': self._extract_summary(rewritten_content),
                        'excerpt': self._extract_excerpt(rewritten_content),
                        'source_name': article['source_name'],
                        'source_url': article['url'],
                        'section_slug': self._classify_section(article['title'], rewritten_content),
                        'tags': self._extract_tags(article['title'], rewritten_content),
                        'status': 'published',
                        'origin_type': 'SCRAPED',
                        'image_url': article.get('image_url'),
                        'scraped_content': rewritten_content,
                        'article_slug': article_slug,
                        'content_hash': content_hash
                    }
                    
                    processed_articles.append(post_data)
                    logger.info(f"✅ Successfully processed: {article['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing article {article['title']}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_articles)} articles from WealthSpire")
            return processed_articles
            
        except Exception as e:
            logger.error(f"Error in WealthSpire processing: {e}")
            return []

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
        slug = slug.strip('-')                # Remove leading/trailing hyphens
        
        # Limit length
        if len(slug) > 80:
            slug = slug[:80].rstrip('-')
        
        return slug

    def _create_content_hash(self, title: str, content: str) -> str:
        """Create hash for content deduplication"""
        combined = f"{title}|{content}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _extract_summary(self, content: str) -> str:
        """Extract a brief summary from the rewritten content"""
        # Take first 2-3 sentences as summary
        sentences = content.split('. ')
        if len(sentences) >= 2:
            summary = '. '.join(sentences[:2]) + '.'
        else:
            summary = content[:200] + '...' if len(content) > 200 else content
        
        return summary.strip()

    def _extract_excerpt(self, content: str) -> str:
        """Extract a 75-word excerpt from the content"""
        words = content.split()
        if len(words) <= 75:
            return content
        
        excerpt = ' '.join(words[:75])
        # Make sure it ends with a complete sentence
        if not excerpt.endswith('.'):
            last_period = excerpt.rfind('.')
            if last_period > 0:
                excerpt = excerpt[:last_period + 1]
            else:
                excerpt += '...'
        
        return excerpt

    def _classify_section(self, title: str, content: str) -> str:
        """Classify article into appropriate section"""
        text = f"{title} {content}".lower()
        
        # Section classification logic
        if any(word in text for word in ['merger', 'acquisition', 'buyout', 'deal', 'takeover']):
            return 'ma'
        elif any(word in text for word in ['private equity', 'lbo', 'leveraged buyout', 'pe firm']):
            return 'lbo'
        elif any(word in text for word in ['sec', 'doj', 'ftc', 'antitrust', 'regulatory', 'compliance']):
            return 'reg'
        elif any(word in text for word in ['ipo', 'stock', 'bond', 'capital', 'funding', 'investment']):
            return 'cap'
        else:
            return 'cap'  # Default to capital markets

    def _extract_tags(self, title: str, content: str) -> List[str]:
        """Extract relevant tags from title and content"""
        text = f"{title} {content}".lower()
        tags = []
        
        # Financial terms
        financial_terms = {
            'merger': ['merger', 'acquisition', 'ma'],
            'private equity': ['private equity', 'pe', 'lbo'],
            'investment': ['investment', 'investor', 'funding'],
            'regulatory': ['regulatory', 'compliance', 'sec', 'doj'],
            'capital markets': ['ipo', 'stock', 'bond', 'capital'],
            'banking': ['bank', 'banking', 'financial institution'],
            'insurance': ['insurance', 'insurer', 'coverage'],
            'real estate': ['real estate', 'property', 'reit'],
            'technology': ['tech', 'technology', 'digital', 'fintech'],
            'cryptocurrency': ['crypto', 'bitcoin', 'blockchain', 'digital currency']
        }
        
        for category, terms in financial_terms.items():
            if any(term in text for term in terms):
                tags.append(category.replace(' ', '_'))
        
        # Add some general tags
        if 'breaking' in text or 'urgent' in text:
            tags.append('breaking')
        
        if 'analysis' in text or 'report' in text:
            tags.append('analysis')
        
        # Limit to 5 tags
        return tags[:5]

    def close(self):
        """Close all resources"""
        if hasattr(self, 'web_scraper'):
            self.web_scraper.close()
        if hasattr(self, 'content_processor'):
            self.content_processor.close()
