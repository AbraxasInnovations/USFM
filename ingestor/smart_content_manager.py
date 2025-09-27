"""
Smart content management system to ensure sections always stay populated
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from database import DatabaseManager

logger = logging.getLogger(__name__)

class SmartContentManager:
    def __init__(self):
        self.db = DatabaseManager()
        
        # Content thresholds - minimum articles to keep in each section
        self.section_thresholds = {
            'ma': 3,      # Mergers & Acquisitions
            'lbo': 3,     # LBO/Private Equity  
            'reg': 3,     # Regulatory/Antitrust
            'cap': 5,     # Capital Markets (most important)
            'rumor': 2,   # DeFi/Crypto
            'all': 30     # Homepage total
        }
        
        # How long to keep articles as fallbacks (days)
        self.fallback_retention_days = 7

    def get_smart_content_for_section(self, section_slug: str, new_articles: List[Dict]) -> List[Dict]:
        """
        Get smart content mix for a section, ensuring it's always populated
        """
        try:
            # Get existing articles in this section
            existing_articles = self._get_existing_section_articles(section_slug)
            
            # Get the target count for this section
            target_count = self.section_thresholds.get(section_slug, 3)
            
            # If we have enough new articles, use them
            if len(new_articles) >= target_count:
                logger.info(f"Section {section_slug}: Using {len(new_articles)} new articles")
                return new_articles[:target_count]
            
            # If we have some new articles, mix with existing
            if new_articles:
                needed_from_existing = target_count - len(new_articles)
                fallback_articles = existing_articles[:needed_from_existing]
                
                # Combine new articles with fallbacks
                smart_content = new_articles + fallback_articles
                logger.info(f"Section {section_slug}: Using {len(new_articles)} new + {len(fallback_articles)} fallback articles")
                return smart_content
            
            # If no new articles, use existing as fallbacks
            if existing_articles:
                logger.info(f"Section {section_slug}: No new articles, using {len(existing_articles)} fallback articles")
                return existing_articles[:target_count]
            
            # If no articles at all, return empty (shouldn't happen in practice)
            logger.warning(f"Section {section_slug}: No articles available at all")
            return []
            
        except Exception as e:
            logger.error(f"Error getting smart content for section {section_slug}: {e}")
            return new_articles[:self.section_thresholds.get(section_slug, 3)]

    def get_smart_homepage_content(self, new_articles: List[Dict]) -> List[Dict]:
        """
        Get smart content for homepage, ensuring it's always full
        """
        try:
            target_count = self.section_thresholds['all']
            
            # If we have enough new articles, use them
            if len(new_articles) >= target_count:
                logger.info(f"Homepage: Using {len(new_articles)} new articles")
                return new_articles[:target_count]
            
            # Get recent articles as fallbacks
            needed_from_existing = target_count - len(new_articles)
            fallback_articles = self._get_recent_fallback_articles(needed_from_existing)
            
            # Combine new articles with fallbacks
            smart_content = new_articles + fallback_articles
            logger.info(f"Homepage: Using {len(new_articles)} new + {len(fallback_articles)} fallback articles")
            return smart_content
            
        except Exception as e:
            logger.error(f"Error getting smart homepage content: {e}")
            return new_articles[:target_count]

    def _get_existing_section_articles(self, section_slug: str) -> List[Dict]:
        """Get existing articles for a specific section"""
        try:
            # Get articles from the last 7 days, excluding very recent ones (last 2 hours)
            cutoff_time = datetime.now() - timedelta(hours=2)
            fallback_cutoff = datetime.now() - timedelta(days=self.fallback_retention_days)
            
            # Query for existing articles in this section
            response = self.db.supabase.table('posts').select('*').eq('section_slug', section_slug).eq('status', 'published').lt('created_at', cutoff_time.isoformat()).gte('created_at', fallback_cutoff.isoformat()).order('created_at', desc=True).limit(10).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Error getting existing section articles for {section_slug}: {e}")
            return []

    def _get_recent_fallback_articles(self, count: int) -> List[Dict]:
        """Get recent articles as fallbacks for homepage"""
        try:
            # Get articles from the last 7 days, excluding very recent ones (last 2 hours)
            cutoff_time = datetime.now() - timedelta(hours=2)
            fallback_cutoff = datetime.now() - timedelta(days=self.fallback_retention_days)
            
            # Query for recent articles
            response = self.db.supabase.table('posts').select('*').eq('status', 'published').lt('created_at', cutoff_time.isoformat()).gte('created_at', fallback_cutoff.isoformat()).order('created_at', desc=True).limit(count).execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent fallback articles: {e}")
            return []

    def update_section_content(self, section_slug: str, new_articles: List[Dict]) -> List[Dict]:
        """
        Update section content with smart fallback logic
        """
        return self.get_smart_content_for_section(section_slug, new_articles)

    def get_content_summary(self) -> Dict[str, int]:
        """Get summary of current content distribution"""
        try:
            summary = {}
            for section in self.section_thresholds.keys():
                if section == 'all':
                    continue
                    
                # Count current articles in each section
                response = self.db.supabase.table('posts').select('id', count='exact').eq('section_slug', section).eq('status', 'published').execute()
                summary[section] = response.count if response.count else 0
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting content summary: {e}")
            return {}

    def close(self):
        """Close database connection"""
        self.db.close()
