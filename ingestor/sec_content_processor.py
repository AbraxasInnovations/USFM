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
from database import DatabaseManager

logger = logging.getLogger(__name__)

class SECContentProcessor:
    def __init__(self):
        self.sec_scraper = SECScraper()
        self.article_rewriter = ArticleRewriter()
        self.content_processor = ContentProcessor()
        self.db = DatabaseManager()

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
            
            # Step 1.5: Deduplicate filings by accession number to avoid processing same deal multiple times
            unique_filings = self._deduplicate_filings_by_accession(filings)
            logger.info(f"After deduplication: {len(unique_filings)} unique filings from {len(filings)} total")
            
            processed_filings = []
            
            for i, filing in enumerate(unique_filings):
                try:
                    logger.info(f"Processing S-4 filing {i+1}/{len(unique_filings)}: {filing['company_name']}")
                    
                    # Step 2: Check if this filing already exists (we'll check after scraping since we need the final URL)
                    # This check will be done after we have the filing content and rewritten title
                    
                    # Step 3: Scrape filing content
                    filing_content = self.sec_scraper.scrape_filing_content(filing)
                    
                    if not filing_content:
                        logger.warning(f"Failed to scrape content for {filing['company_name']}")
                        continue
                    
                    # Step 4: Rewrite with AI
                    rewritten_data = self.article_rewriter.rewrite_article(
                        title=filing_content['title'],
                        content=filing_content['content']
                    )
                    
                    if not rewritten_data:
                        logger.warning(f"Failed to rewrite S-4 filing: {filing_content['title']}")
                        continue
                    
                    # Step 4.5: Check if this rewritten article already exists
                    content_hash = self.db.generate_content_hash(filing_content['url'], rewritten_data['title'])
                    if self.db.post_exists(content_hash):
                        logger.info(f"Rewritten S-4 article already exists, skipping: {rewritten_data['title'][:50]}...")
                        continue
                    
                    # Step 4.6: Check if we've already written about this company recently (within last 24 hours)
                    company_name = filing.get('company_name', '').lower().strip()
                    if company_name and self._has_recent_company_article(company_name, days_back=1):
                        logger.info(f"Already wrote about {company_name} recently, skipping to avoid repetition")
                        continue
                    
                    # Step 4.6.5: Additional check - look for articles with similar titles (more aggressive deduplication)
                    if self._has_similar_article_recently(rewritten_data['title'], days_back=1):
                        logger.info(f"Found similar article recently, skipping: {rewritten_data['title'][:50]}...")
                        continue
                    
                    # Step 4.7: Check if slug already exists (additional safety check)
                    article_slug = self._generate_slug(rewritten_data['title'], filing_content['url'])
                    if self._slug_exists(article_slug):
                        logger.warning(f"Slug already exists, skipping: {article_slug}")
                        continue
                    
                    # Step 5: Process for our system
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
        finally:
            # Close database connection
            self.db.close()

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
            article_slug = self._generate_slug(rewritten_data['title'], filing_content['url'])
            
            # Prepare post data
            post_data = {
                'title': rewritten_data['title'],
                'summary': rewritten_data['summary'],
                'excerpt': excerpt,
                'source_name': 'USFM',
                'source_url': filing_content['url'],
                'section_slug': section_slug,
                'tags': tags,
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

    def _generate_slug(self, title: str, url: str = None) -> str:
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
            slug = f"sec-{slug}-{url_hash}"
        else:
            slug = f"sec-{slug}"
        
        return slug

    def _deduplicate_filings_by_accession(self, filings: List[Dict]) -> List[Dict]:
        """
        Deduplicate filings by accession number to avoid processing the same deal multiple times
        (e.g., multiple Fossil entities filing for the same transaction)
        """
        seen_accessions = set()
        unique_filings = []
        
        for filing in filings:
            accession_number = filing.get('accession_number', '')
            if accession_number and accession_number not in seen_accessions:
                seen_accessions.add(accession_number)
                unique_filings.append(filing)
                logger.info(f"Keeping unique filing: {filing['company_name']} - {accession_number}")
            else:
                logger.info(f"Skipping duplicate filing: {filing['company_name']} - {accession_number}")
        
        return unique_filings

    def _get_sec_image_url(self) -> str:
        """Get a random SEC image URL from our custom images"""
        # Available SEC images (including new ones)
        sec_images = [
            'sec1.jpg', 'sec2.jpg', 'sec3.jpg', 'sec4.jpg', 'sec8.jpg',
            'sec23.jpg', 'sec24.jpg', 'sec25.jpg', 'sec26.jpg', 
            'sec27.jpg', 'sec28.jpg', 'sec29.jpg'
        ]

        # Randomly select one
        selected_image = random.choice(sec_images)

        # Return the full URL path
        return f"/images/sec/{selected_image}"
    
    def _slug_exists(self, slug: str) -> bool:
        """Check if a slug already exists in the database"""
        try:
            result = self.db.supabase.table('posts').select('id').eq('article_slug', slug).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Error checking if slug exists: {e}")
            return False

    def _has_similar_article_recently(self, title: str, days_back: int = 1) -> bool:
        """
        Check if we've already written an article with a similar title recently
        This is more aggressive deduplication for SEC articles
        """
        try:
            from datetime import datetime, timedelta
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Extract key company names from the title for comparison
            title_lower = title.lower()
            
            # Look for articles with similar company names in the title
            # This catches cases where the same companies are mentioned in different ways
            result = self.db.supabase.table('posts').select('id, title').eq('origin_type', 'SCRAPED').gte('created_at', cutoff_date_str).execute()
            
            for article in result.data:
                article_title_lower = article['title'].lower()
                
                # Check if both titles mention the same key companies
                # Extract company names (words that are likely company names)
                title_companies = set()
                article_companies = set()
                
                # Simple heuristic: look for capitalized words that appear in both titles
                import re
                title_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', title)
                article_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', article['title'])
                
                # If there's significant overlap in company names, consider it a duplicate
                overlap = set(title_words) & set(article_words)
                if len(overlap) >= 2:  # At least 2 company names overlap
                    logger.info(f"Found similar article with overlapping companies: {overlap}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for similar articles: {e}")
            return False

    def _has_recent_company_article(self, company_name: str, days_back: int = 7) -> bool:
        """
        Check if we've already written about this company recently
        """
        try:
            from datetime import datetime, timedelta
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_date_str = cutoff_date.strftime('%Y-%m-%d')
            
            # Search for recent SEC articles about this company
            # Look specifically in the company_name field for exact matches
            result = self.db.supabase.table('posts').select('id, title, company_name').eq('origin_type', 'SCRAPED').eq('company_name', company_name).gte('created_at', cutoff_date_str).execute()
            
            has_recent = len(result.data) > 0
            if has_recent:
                logger.info(f"Found {len(result.data)} recent SEC articles about {company_name}")
                for article in result.data:
                    logger.info(f"  - {article['title'][:50]}...")
            
            return has_recent
            
        except Exception as e:
            logger.error(f"Error checking for recent company articles: {e}")
            return False  # If there's an error, don't block the processing
    
    def close(self):
        """Close resources"""
        if hasattr(self.sec_scraper, 'session'):
            self.sec_scraper.close()
        if hasattr(self.article_rewriter, 'client'):
            self.article_rewriter.close()
