"""
AI-powered article rewriter using OpenAI API
"""
import logging
import openai
from typing import Optional
from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

class ArticleRewriter:
    def __init__(self):
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. Article rewriting will be disabled.")
            self.enabled = False
        else:
            openai.api_key = OPENAI_API_KEY
            self.enabled = True

    def rewrite_article(self, title: str, content: str) -> Optional[str]:
        """
        Rewrite an article using OpenAI API to create original content
        """
        if not self.enabled:
            logger.warning("Article rewriting is disabled - no OpenAI API key")
            return None

        if not content or len(content.strip()) < 50:
            logger.warning("Content too short to rewrite")
            return None

        try:
            logger.info(f"Rewriting article: {title[:50]}...")
            
            # Create a prompt for rewriting
            prompt = f"""
            You are a senior financial journalist specializing in mergers, acquisitions, and corporate actions. 
            You excel at translating complex SEC filings into clear, comprehensive articles.
            
            CRITICAL: The SEC filing content below contains key information in the beginning sections. 
            Pay special attention to the "Filing Overview" section which typically contains the most important details.
            
            Rewrite the following SEC filing content into a comprehensive, informative article that explains:
            
            1. **What is happening**: The specific corporate action or transaction (merger, acquisition, etc.)
            2. **Who is involved**: The EXACT company names involved in the transaction - this information is usually in the first few paragraphs
            3. **Financial implications**: Deal value, exchange ratios, stock prices, or other financial terms
            4. **Strategic rationale**: Why this deal makes sense for the companies
            5. **Timeline and next steps**: When the deal is expected to close and what happens next
            6. **Market impact**: Potential effects on shareholders, employees, and the broader market
            7. **Regulatory considerations**: Any antitrust or regulatory approvals needed
            
            IMPORTANT INSTRUCTIONS:
            - Extract ALL specific company names mentioned in the filing
            - Look for acquisition targets, merger partners, and subsidiary names
            - Include exact financial figures, dates, and transaction terms
            - If the filing mentions "acquiring" or "merging with" a specific company, include that company's name
            - Don't say "it's unclear" or "not specified" - the information should be in the filing content
            - Focus on the most important details from the beginning of the filing
            - Be specific about what type of transaction this is (merger, acquisition, business combination)
            - Highlight the strategic rationale and expected benefits
            - Include information about regulatory requirements and timeline
            - Make the article informative and engaging for financial news readers
            
            Make the content engaging and accessible while maintaining journalistic accuracy.
            Use a professional but readable tone suitable for financial news.
            
            Title: {title}

            Original SEC Filing Content:
            {content}

            Please provide the response in the following JSON format:
            {{
                "title": "Engaging headline that captures the key deal details including company names",
                "summary": "2-3 sentence summary highlighting the most important aspects including who is acquiring whom",
                "content": "Comprehensive article covering all the key points above with specific details from the filing"
            }}
            """

            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a senior financial journalist specializing in mergers, acquisitions, and corporate actions. You excel at translating complex SEC filings into clear, comprehensive articles that explain the business implications and market impact of corporate transactions."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1500,
                temperature=0.7
            )

            rewritten_content = response.choices[0].message.content.strip()
            
            if rewritten_content:
                # Parse the JSON response
                try:
                    import json
                    rewritten_data = json.loads(rewritten_content)
                    
                    # Validate required fields
                    if 'title' in rewritten_data and 'summary' in rewritten_data and 'content' in rewritten_data:
                        logger.info(f"Successfully rewritten article (original: {len(content)} chars, rewritten: {len(rewritten_data['content'])} chars)")
                        return rewritten_data
                    else:
                        logger.warning("OpenAI response missing required fields")
                        return None
                        
                except json.JSONDecodeError:
                    logger.warning("OpenAI response is not valid JSON")
                    return None
            else:
                logger.warning("OpenAI returned empty content")
                return None

        except Exception as e:
            logger.error(f"Error rewriting article: {e}")
            return None

    def is_enabled(self) -> bool:
        """Check if article rewriting is enabled"""
        return self.enabled
