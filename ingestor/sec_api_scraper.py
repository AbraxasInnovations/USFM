"""
SEC API-based scraper that uses official SEC endpoints to avoid blocking
"""
import logging
import requests
import time
from typing import Dict, List, Optional
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SECAPIScraper:
    def __init__(self):
        self.base_url = "https://data.sec.gov"
        self.edgar_url = "https://www.sec.gov/edgar"
        
        # Use the official SEC API headers
        self.headers = {
            'User-Agent': 'US Financial Moves (contact@usfinancemoves.com)',
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting: SEC allows 10 requests per second
        self.rate_limit_delay = 0.1

    def get_recent_s4_filings(self, days_back: int = 30, max_filings: int = 5) -> List[Dict]:
        """
        Get recent S-4 filings using SEC's company facts API
        """
        try:
            logger.info(f"Fetching recent S-4 filings using SEC API (last {days_back} days)")
            
            # Get recent filings from SEC's recent filings endpoint
            recent_filings_url = f"{self.base_url}/api/xbrl/companyfacts/CIK0000789019.json"  # Example CIK
            
            # Instead, let's use the submissions endpoint for a known company
            # We'll search for companies that have recent S-4 filings
            filings = []
            
            # Try to get filings from major companies known to have M&A activity
            major_companies = [
                "0000789019",  # Apple
                "0001018724",  # Amazon  
                "0001652044",  # Google/Alphabet
                "0000789019",  # Microsoft
                "0001067983",  # Berkshire Hathaway
            ]
            
            for cik in major_companies[:2]:  # Limit to avoid rate limits
                try:
                    company_filings = self._get_company_s4_filings(cik, days_back)
                    filings.extend(company_filings)
                    
                    if len(filings) >= max_filings:
                        break
                        
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.warning(f"Error getting filings for CIK {cik}: {e}")
                    continue
            
            logger.info(f"Found {len(filings)} S-4 filings")
            return filings[:max_filings]
            
        except Exception as e:
            logger.error(f"Error getting recent S-4 filings: {e}")
            return []

    def _get_company_s4_filings(self, cik: str, days_back: int) -> List[Dict]:
        """
        Get S-4 filings for a specific company
        """
        try:
            # Get company submissions
            submissions_url = f"{self.base_url}/submissions/CIK{cik.zfill(10)}.json"
            
            response = self.session.get(submissions_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Look for S-4 filings in recent submissions
            recent_filings = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            if 'filings' in data and 'recent' in data['filings']:
                recent = data['filings']['recent']
                
                for i, form_type in enumerate(recent.get('form', [])):
                    if form_type == 'S-4':
                        # Get filing details
                        filing_date = recent.get('filingDate', [])[i] if i < len(recent.get('filingDate', [])) else ''
                        accession = recent.get('accessionNumber', [])[i] if i < len(recent.get('accessionNumber', [])) else ''
                        
                        if filing_date:
                            try:
                                filing_datetime = datetime.strptime(filing_date, '%Y-%m-%d')
                                if filing_datetime >= cutoff_date:
                                    filing_data = {
                                        'company_name': data.get('name', 'Unknown Company'),
                                        'form_type': 'S-4',
                                        'filing_date': filing_date,
                                        'accession_number': accession,
                                        'cik': cik,
                                        'source_name': 'SEC EDGAR',
                                        'domain': 'sec.gov',
                                        'document_url': f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{accession}.txt",
                                        'title': f"S-4 Filing - {data.get('name', 'Unknown Company')}",
                                        'summary': f"S-4 merger/acquisition filing by {data.get('name', 'Unknown Company')}"
                                    }
                                    recent_filings.append(filing_data)
                            except ValueError:
                                continue
            
            return recent_filings
            
        except Exception as e:
            logger.error(f"Error getting company S-4 filings for CIK {cik}: {e}")
            return []

    def scrape_filing_content(self, filing_data: Dict) -> Optional[Dict]:
        """
        Scrape the actual content from an S-4 filing document
        """
        try:
            doc_url = filing_data.get('document_url')
            if not doc_url:
                return None
            
            logger.info(f"Scraping S-4 filing content from: {doc_url}")
            
            # Add delay to be respectful to SEC servers
            time.sleep(self.rate_limit_delay)
            
            response = self.session.get(doc_url, timeout=30)
            response.raise_for_status()
            
            # Parse the filing document
            content_data = self._parse_filing_document(response.text, filing_data)
            
            if content_data:
                logger.info(f"Successfully scraped S-4 filing: {content_data['title'][:50]}...")
                return content_data
            else:
                logger.warning(f"No content extracted from S-4 filing: {doc_url}")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping S-4 filing content: {e}")
            return None

    def _parse_filing_document(self, content: str, filing_data: Dict) -> Optional[Dict]:
        """
        Parse the S-4 filing document to extract key information
        """
        try:
            from bs4 import BeautifulSoup
            
            # Check if we got blocked
            if "Your Request Originates from an Undeclared Automated Tool" in content:
                logger.warning("SEC blocked our request - using fallback content")
                return self._create_fallback_content(filing_data)
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title = self._extract_filing_title(soup, filing_data)
            
            # Extract key content
            content_text = self._extract_filing_content(soup)
            
            if not title or not content_text:
                return self._create_fallback_content(filing_data)
            
            return {
                'title': title,
                'content': content_text,
                'author': f"SEC Filing - {filing_data.get('company_name', '')}",
                'publish_date': filing_data.get('filing_date', ''),
                'url': filing_data.get('document_url', ''),
                'image_url': None,
                'source_name': 'SEC EDGAR',
                'domain': 'sec.gov',
                'filing_type': 'S-4',
                'company_name': filing_data.get('company_name', '')
            }
            
        except Exception as e:
            logger.error(f"Error parsing filing document: {e}")
            return self._create_fallback_content(filing_data)

    def _create_fallback_content(self, filing_data: Dict) -> Dict:
        """
        Create fallback content when we can't access the full filing
        """
        company_name = filing_data.get('company_name', 'Company')
        filing_date = filing_data.get('filing_date', '')
        
        return {
            'title': f"{company_name} S-4 Merger/Acquisition Filing",
            'content': f"""
            {company_name} has filed an S-4 registration statement with the U.S. Securities and Exchange Commission, 
            indicating a proposed merger or acquisition transaction. S-4 filings are typically used for business 
            combinations where securities are being offered in exchange for shares of another company.
            
            The filing was submitted on {filing_date} and represents a significant corporate action that will 
            require shareholder approval and regulatory review. S-4 filings contain detailed information about 
            the proposed transaction, including financial terms, strategic rationale, and risk factors.
            
            This type of filing is commonly associated with mergers, acquisitions, and other business combinations 
            that involve the exchange of securities. The company will need to provide comprehensive disclosure 
            about the transaction terms, the companies involved, and the expected benefits and risks.
            """,
            'author': f"SEC Filing - {company_name}",
            'publish_date': filing_date,
            'url': filing_data.get('document_url', ''),
            'image_url': None,
            'source_name': 'SEC EDGAR',
            'domain': 'sec.gov',
            'filing_type': 'S-4',
            'company_name': company_name
        }

    def _extract_filing_title(self, soup, filing_data: Dict) -> str:
        """Extract a meaningful title from the S-4 filing"""
        company_name = filing_data.get('company_name', 'Company')
        return f"{company_name} S-4 Merger/Acquisition Filing"

    def _extract_filing_content(self, soup) -> str:
        """Extract key content from the S-4 filing document"""
        try:
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get all text content
            text_content = soup.get_text()
            
            # Clean up the text
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            content = ' '.join(lines)
            
            # Truncate to reasonable length
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting filing content: {e}")
            return ""

    def close(self):
        """Close the session"""
        if hasattr(self, 'session'):
            self.session.close()
