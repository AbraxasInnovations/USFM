"""
SEC S-4 Filing Content Processor
Processes SEC S-4 filings using our existing scraping and rewriting pipeline
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re
import hashlib
import random

from sec_scraper import SECScraper
from article_rewriter import ArticleRewriter
from content_processor import ContentProcessor

logger = logging.getLogger(__name__)

class SECContentProcessor:
    def __init__(self):
        self.sec_scraper = SECScraper()
        self.article_rewriter = ArticleRewriter()
        self.content_processor = ContentProcessor()

    def process_s4_filings(self, max_filings: int = 3) -> List[Dict]:
        """
        Process recent S-4 filings with AI rewriting
        """
        try:
            logger.info(f"Starting S-4 filing processing (max {max_filings} filings)")
            
            # Step 1: Get recent S-4 filings
            filings = self.sec_scraper.get_recent_s4_filings(days_back=30, max_filings=max_filings)
            
            if not filings:
                logger.warning("No S-4 filings found")
                return []
            
            processed_filings = []
            
            for i, filing in enumerate(filings):
                try:
                    logger.info(f"Processing S-4 filing {i+1}/{len(filings)}: {filing['company_name']}")
                    
                    # Step 2: Scrape filing content
                    filing_content = self.sec_scraper.scrape_filing_content(filing)
                    
                    if not filing_content:
                        logger.warning(f"Failed to scrape content for {filing['company_name']}")
                        continue
                    
                    # Step 3: Rewrite with AI
                    rewritten_data = self.article_rewriter.rewrite_article(
                        title=filing_content['title'],
                        content=filing_content['content']
                    )
                    
                    if not rewritten_data:
                        logger.warning(f"Failed to rewrite S-4 filing: {filing_content['title']}")
                        continue
                    
                    # Step 4: Process for our system
                    processed_filing = self._process_filing_data(
                        original_filing=filing,
                        filing_content=filing_content,
                        rewritten_data=rewritten_data
                    )
                    
                    if processed_filing:
                        processed_filings.append(processed_filing)
                        logger.info(f"✅ Successfully processed S-4 filing: {processed_filing['title'][:50]}...")
                    
                except Exception as e:
                    logger.error(f"Error processing S-4 filing {filing['company_name']}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_filings)} S-4 filings")
            return processed_filings
            
        except Exception as e:
            logger.error(f"Error in S-4 filing processing: {e}")
            return []

    def _process_filing_data(self, original_filing: Dict, filing_content: Dict, rewritten_data: Dict) -> Optional[Dict]:
        """
        Process filing data into our standard post format
        """
        try:
            # Generate excerpt
            excerpt = self.content_processor.extract_excerpt(rewritten_data['content'])
            
            # Classify section (S-4 filings are typically M&A)
            section_slug = 'ma'  # Mergers & Acquisitions
            
            # Extract tags
            tags = self.content_processor.extract_tags(
                rewritten_data['title'], 
                rewritten_data['content'], 
                []
            )
            
            # Ensure SEC-specific tags
            if 'sec' not in tags:
                tags.append('sec')
            if 's-4' not in tags:
                tags.append('s-4')
            if 'filing' not in tags:
                tags.append('filing')
            if 'merger' not in tags:
                tags.append('merger')
            
            # Generate slug
            article_slug = self._generate_slug(rewritten_data['title'])
            
            # Prepare post data
            post_data = {
                'title': rewritten_data['title'],
                'summary': rewritten_data['summary'],
                'excerpt': excerpt,
                'source_name': 'SEC EDGAR',
                'source_url': filing_content['url'],
                'section_slug': section_slug,
                'tags': tags,
                'content_hash': hashlib.sha256(
                    f"{filing_content['url']}_{rewritten_data['title']}".encode('utf-8')
                ).hexdigest(),
                'status': 'published',
                'origin_type': 'SCRAPED',
                'image_url': self._get_sec_image_url(),  # Use custom SEC images
                'scraped_content': rewritten_data['content'],
                'article_slug': article_slug,
                'company_name': original_filing.get('company_name', ''),
                'filing_type': 'S-4',
                'filing_date': original_filing.get('filing_date', '')
            }
            
            return post_data
            
        except Exception as e:
            logger.error(f"Error processing filing data: {e}")
            return None

    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        # Convert to lowercase
        slug = title.lower()
        # Replace non-alphanumeric characters with hyphens
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spaces and multiple hyphens with a single hyphen
        slug = re.sub(r'[\s-]+', '-', slug).strip('-')
        # Add sec prefix to make it unique
        slug = f"sec-{slug}"
        return slug

    def _get_sec_image_url(self) -> str:
        """Get a random SEC image URL from our custom images"""
        # Available SEC images
        sec_images = ['sec1.jpg', 'sec2.jpg', 'sec3.jpg', 'sec4.jpg']
        
        # Randomly select one
        selected_image = random.choice(sec_images)
        
        # Return the full URL path
        return f"/images/sec/{selected_image}"
    
    def close(self):
        """Close resources"""
        if hasattr(self.sec_scraper, 'session'):
            self.sec_scraper.close()
        if hasattr(self.article_rewriter, 'client'):
            self.article_rewriter.close()
