"""
Content Extraction Service
"""

import logging
from typing import Optional
from newspaper import Article as NewspaperArticle
import httpx

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Service for extracting full content from article URLs"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def extract_content(self, url: str) -> dict:
        """
        Extract full content from article URL
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with extracted content
        """
        try:
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            
            # Generate summary if content is available
            summary = self._generate_summary(article.text) if article.text else None
            
            return {
                'content': article.text,
                'summary': summary,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'keywords': article.keywords if hasattr(article, 'keywords') else [],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return {
                'content': None,
                'summary': None,
                'authors': [],
                'publish_date': None,
                'top_image': None,
                'keywords': [],
                'success': False,
                'error': str(e)
            }
    
    def _generate_summary(self, text: str, max_words: int = 80) -> str:
        """
        Generate a summary from article text
        
        Args:
            text: Full article text
            max_words: Maximum words in summary
            
        Returns:
            Generated summary
        """
        if not text:
            return "Summary not available."
        
        # Split into words and take approximately max_words
        words = text.split()
        if len(words) <= max_words:
            return text
        
        # Take first max_words and ensure it ends properly
        summary_words = words[:max_words]
        summary = " ".join(summary_words)
        
        # Try to end at a sentence boundary
        if '.' in summary:
            sentences = summary.split('.')
            if len(sentences) > 1:
                # Keep all complete sentences
                summary = '. '.join(sentences[:-1]) + '.'
        
        return summary
    
    async def extract_content_async(self, url: str) -> dict:
        """
        Async version of content extraction
        
        Args:
            url: Article URL
            
        Returns:
            Dictionary with extracted content
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # Use newspaper3k for parsing
                article = NewspaperArticle(url)
                article.set_html(response.text)
                article.parse()
                
                summary = self._generate_summary(article.text) if article.text else None
                
                return {
                    'content': article.text,
                    'summary': summary,
                    'authors': article.authors,
                    'publish_date': article.publish_date,
                    'top_image': article.top_image,
                    'keywords': article.keywords if hasattr(article, 'keywords') else [],
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return {
                'content': None,
                'summary': None,
                'authors': [],
                'publish_date': None,
                'top_image': None,
                'keywords': [],
                'success': False,
                'error': str(e)
            }
    
    def update_article_content(self, article, extracted_data: dict) -> bool:
        """
        Update article with extracted content
        
        Args:
            article: Article model instance
            extracted_data: Extracted content data
            
        Returns:
            True if update successful
        """
        try:
            if extracted_data['success']:
                if extracted_data['content']:
                    article.content = extracted_data['content']
                
                if extracted_data['summary']:
                    article.summary = extracted_data['summary']
                
                if extracted_data['publish_date']:
                    article.published_date = extracted_data['publish_date']
                
                article.processed = 'processed'
                return True
            else:
                article.processed = 'failed'
                return False
                
        except Exception as e:
            logger.error(f"Error updating article content: {e}")
            article.processed = 'failed'
            return False