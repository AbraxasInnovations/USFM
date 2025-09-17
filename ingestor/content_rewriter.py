"""
AI-powered content rewriter for news articles
"""
import openai
import logging
from typing import Optional, Dict
import re
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class ContentRewriter:
    def __init__(self):
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
        else:
            logger.warning("OPENAI_API_KEY not set. Content rewriting will be disabled.")
    
    def rewrite_article(self, article_data: Dict) -> Optional[Dict]:
        """
        Rewrite an article using AI while maintaining factual accuracy
        Returns dict with rewritten title and content
        """
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not available. Skipping content rewriting.")
            return None
        
        try:
            logger.info(f"Rewriting article: {article_data['title'][:50]}...")
            
            # Create a slug for the article
            slug = self._create_slug(article_data['title'])
            
            # Rewrite the title
            rewritten_title = self._rewrite_title(article_data['title'])
            
            # Rewrite the content
            rewritten_content = self._rewrite_content(article_data['content'])
            
            if rewritten_title and rewritten_content:
                return {
                    'original_title': article_data['title'],
                    'rewritten_title': rewritten_title,
                    'original_content': article_data['content'],
                    'rewritten_content': rewritten_content,
                    'slug': slug,
                    'source_url': article_data['url'],
                    'author': article_data.get('author', ''),
                    'publish_date': article_data.get('publish_date', ''),
                    'domain': article_data.get('domain', '')
                }
            else:
                logger.error("Failed to rewrite article content")
                return None
                
        except Exception as e:
            logger.error(f"Error rewriting article: {e}")
            return None
    
    def _create_slug(self, title: str) -> str:
        """Create a URL-friendly slug from title"""
        # Convert to lowercase and replace spaces with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:100]  # Limit length
    
    def _rewrite_title(self, original_title: str) -> str:
        """Rewrite the article title"""
        try:
            prompt = f"""
            Rewrite this news headline to be more engaging and clear while maintaining the same factual meaning:
            
            Original: "{original_title}"
            
            Requirements:
            - Keep the same core facts and meaning
            - Make it more engaging and readable
            - Use active voice when possible
            - Keep it concise (under 80 characters)
            - Don't add sensationalism or clickbait
            
            Rewritten headline:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            rewritten_title = response.choices[0].message.content.strip()
            # Remove quotes if present
            rewritten_title = rewritten_title.strip('"\'')
            
            return rewritten_title
            
        except Exception as e:
            logger.error(f"Error rewriting title: {e}")
            return original_title
    
    def _rewrite_content(self, original_content: str) -> str:
        """Rewrite the article content"""
        try:
            # Truncate content if too long for API
            content_to_rewrite = original_content[:3000] if len(original_content) > 3000 else original_content
            
            prompt = f"""
            Rewrite this financial news article to be more engaging and accessible while maintaining all factual accuracy:
            
            Original article:
            {content_to_rewrite}
            
            Requirements:
            - Maintain 100% factual accuracy
            - Make it more engaging and readable
            - Use clear, concise language
            - Add context where helpful
            - Keep the same key information and quotes
            - Write in a professional but accessible tone
            - Length should be similar to original (500-800 words)
            
            Rewritten article:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            rewritten_content = response.choices[0].message.content.strip()
            return rewritten_content
            
        except Exception as e:
            logger.error(f"Error rewriting content: {e}")
            return original_content
    
    def create_summary(self, content: str) -> str:
        """Create a brief summary of the rewritten content"""
        try:
            prompt = f"""
            Create a brief 2-3 sentence summary of this financial news article:
            
            {content[:1000]}
            
            Summary:
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            return content[:200] + "..." if len(content) > 200 else content
