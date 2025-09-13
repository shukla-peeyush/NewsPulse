"""
Content extraction module for full article text using newspaper3k and playwright
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from newspaper import Article as NewspaperArticle
from playwright.async_api import async_playwright, Browser, Page
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..storage.models import Article
from ..storage.database import get_db_session

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Content extractor with multiple extraction methods"""
    
    def __init__(self, use_playwright: bool = False, timeout: int = 30):
        self.use_playwright = use_playwright
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        if self.use_playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    def extract_with_newspaper3k(self, url: str, fallback_description: str = "") -> Dict[str, Any]:
        """
        Extract content using newspaper3k library
        
        Args:
            url: Article URL
            fallback_description: Fallback description if extraction fails
            
        Returns:
            Dictionary with extracted content
        """
        try:
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            
            # Extract text content
            full_text = article.text.strip() if article.text else ""
            
            # Generate summary (first 80 words or use existing summary)
            summary = self._generate_summary(full_text, fallback_description)
            
            # Count words
            word_count = len(full_text.split()) if full_text else 0
            
            # Extract additional metadata
            authors = article.authors if article.authors else []
            publish_date = article.publish_date
            
            return {
                'full_text': full_text,
                'summary': summary,
                'word_count': word_count,
                'authors': authors,
                'publish_date': publish_date,
                'extraction_method': 'newspaper3k',
                'success': bool(full_text)
            }
            
        except Exception as e:
            logger.error(f"Newspaper3k extraction failed for {url}: {str(e)}")
            
            # Fallback to description
            summary = self._generate_summary("", fallback_description)
            return {
                'full_text': "",
                'summary': summary,
                'word_count': 0,
                'authors': [],
                'publish_date': None,
                'extraction_method': 'newspaper3k_failed',
                'success': False,
                'error': str(e)
            }
    
    async def extract_with_playwright(self, url: str, fallback_description: str = "") -> Dict[str, Any]:
        """
        Extract content using Playwright for JavaScript-heavy sites
        
        Args:
            url: Article URL
            fallback_description: Fallback description if extraction fails
            
        Returns:
            Dictionary with extracted content
        """
        if not self.browser:
            raise RuntimeError("Playwright browser not initialized")
        
        try:
            page = await self.browser.new_page()
            
            # Set user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Navigate to page
            await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Extract text content using various selectors
            content_selectors = [
                'article',
                '[role="main"]',
                '.content',
                '.article-content',
                '.post-content',
                '.entry-content',
                'main',
                '#content'
            ]
            
            full_text = ""
            for selector in content_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            text = await element.inner_text()
                            if text and len(text) > len(full_text):
                                full_text = text
                        break
                except:
                    continue
            
            # If no content found, get all text
            if not full_text:
                full_text = await page.inner_text('body')
            
            # Clean up text
            full_text = self._clean_text(full_text)
            
            # Generate summary
            summary = self._generate_summary(full_text, fallback_description)
            
            # Count words
            word_count = len(full_text.split()) if full_text else 0
            
            await page.close()
            
            return {
                'full_text': full_text,
                'summary': summary,
                'word_count': word_count,
                'authors': [],
                'publish_date': None,
                'extraction_method': 'playwright',
                'success': bool(full_text)
            }
            
        except Exception as e:
            logger.error(f"Playwright extraction failed for {url}: {str(e)}")
            
            summary = self._generate_summary("", fallback_description)
            return {
                'full_text': "",
                'summary': summary,
                'word_count': 0,
                'authors': [],
                'publish_date': None,
                'extraction_method': 'playwright_failed',
                'success': False,
                'error': str(e)
            }
    
    async def extract_content(self, url: str, fallback_description: str = "") -> Dict[str, Any]:
        """
        Extract content using the configured method
        
        Args:
            url: Article URL
            fallback_description: Fallback description if extraction fails
            
        Returns:
            Dictionary with extracted content
        """
        if self.use_playwright:
            return await self.extract_with_playwright(url, fallback_description)
        else:
            return self.extract_with_newspaper3k(url, fallback_description)
    
    def _generate_summary(self, full_text: str, fallback_description: str = "") -> str:
        """
        Generate 80-word summary from full text or fallback description
        
        Args:
            full_text: Full article text
            fallback_description: Fallback description
            
        Returns:
            Generated summary
        """
        # Use full text if available, otherwise use fallback
        text = full_text if full_text else fallback_description
        
        if not text:
            return "Summary not available."
        
        # Split into words and take approximately 80 words
        words = text.split()
        if len(words) <= 80:
            return text
        
        # Take first 80 words and ensure it ends properly
        summary_words = words[:80]
        summary = " ".join(summary_words)
        
        # Try to end at a sentence boundary
        if '.' in summary:
            sentences = summary.split('.')
            if len(sentences) > 1:
                # Keep all complete sentences
                summary = '. '.join(sentences[:-1]) + '.'
        
        return summary
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Remove very short lines (likely navigation/ads)
        meaningful_lines = [line for line in lines if len(line) > 20]
        
        # Join lines
        cleaned_text = '\n'.join(meaningful_lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()


async def extract_article_content(article: Article, extractor: ContentExtractor) -> bool:
    """
    Extract content for a single article
    
    Args:
        article: Article object to extract content for
        extractor: ContentExtractor instance
        
    Returns:
        True if extraction was successful, False otherwise
    """
    try:
        logger.info(f"Extracting content for article: {article.title}")
        
        # Get fallback description from existing summary or empty string
        fallback_description = getattr(article, 'summary', '') or ""
        
        # Extract content
        result = await extractor.extract_content(article.url, fallback_description)
        
        # Update article with extracted content
        if result['success'] and result['full_text']:
            article.full_text = result['full_text']
            article.summary = result['summary']
            article.word_count = result['word_count']
            article.content_extracted = True
            
            # Update author if extracted and not already set
            if result['authors'] and not article.author:
                article.author = ', '.join(result['authors'][:3])  # Limit to 3 authors
            
            # Update publish date if extracted and not already set
            if result['publish_date'] and not article.published_date:
                article.published_date = result['publish_date']
            
            logger.info(f"Successfully extracted {result['word_count']} words for: {article.title}")
            return True
        else:
            # Even if extraction failed, update summary if we have fallback
            if result['summary']:
                article.summary = result['summary']
            
            article.content_extracted = False
            article.processing_errors = result.get('error', 'Content extraction failed')
            
            logger.warning(f"Content extraction failed for: {article.title}")
            return False
            
    except Exception as e:
        article.content_extracted = False
        article.processing_errors = str(e)
        logger.error(f"Error extracting content for {article.title}: {str(e)}")
        return False


async def process_articles_batch(articles: List[Article], use_playwright: bool = False) -> Dict[str, int]:
    """
    Process a batch of articles for content extraction
    
    Args:
        articles: List of Article objects to process
        use_playwright: Whether to use Playwright for extraction
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'total': len(articles),
        'successful': 0,
        'failed': 0,
        'skipped': 0
    }
    
    if not articles:
        return stats
    
    logger.info(f"Processing batch of {len(articles)} articles for content extraction")
    
    async with ContentExtractor(use_playwright=use_playwright) as extractor:
        # Process articles with limited concurrency
        semaphore = asyncio.Semaphore(3)  # Limit concurrent extractions
        
        async def process_with_semaphore(article):
            async with semaphore:
                return await extract_article_content(article, extractor)
        
        # Execute all tasks
        tasks = [process_with_semaphore(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in results:
            if isinstance(result, Exception):
                stats['failed'] += 1
            elif result:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
    
    logger.info(f"Batch processing completed: {stats}")
    return stats


async def process_unextracted_articles(db: Session = None, batch_size: int = 10, use_playwright: bool = False) -> Dict[str, int]:
    """
    Process all articles that don't have extracted content
    
    Args:
        db: Database session (optional)
        batch_size: Number of articles to process in each batch
        use_playwright: Whether to use Playwright for extraction
        
    Returns:
        Dictionary with overall processing statistics
    """
    if db is None:
        db = get_db_session()
        should_close = True
    else:
        should_close = False
    
    try:
        # Get articles that need content extraction
        unextracted_articles = db.query(Article).filter(
            and_(
                Article.content_extracted == False,
                Article.url.isnot(None)
            )
        ).limit(batch_size).all()
        
        if not unextracted_articles:
            logger.info("No articles need content extraction")
            return {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Found {len(unextracted_articles)} articles needing content extraction")
        
        # Process articles
        stats = await process_articles_batch(unextracted_articles, use_playwright)
        
        # Commit changes to database
        db.commit()
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing unextracted articles: {str(e)}")
        raise
    finally:
        if should_close:
            db.close()


def main():
    """Main function for running content extractor standalone"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run content extraction
    asyncio.run(process_unextracted_articles())


if __name__ == "__main__":
    main()