"""
RSS feed fetching and processing logic
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import httpx
import feedparser
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..storage.models_simple import NewsSource, Article, ScrapingSession
from ..storage.database import get_db_session

logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS feed fetcher with async processing and error handling"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                'User-Agent': 'NewsPulse/1.0 (News Intelligence Platform)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.aclose()
    
    async def fetch_feed(self, source: NewsSource) -> List[Dict[str, Any]]:
        """
        Fetch and parse RSS feed from a news source
        
        Args:
            source: NewsSource object containing RSS URL and metadata
            
        Returns:
            List of article dictionaries
        """
        if not source.rss_url:
            logger.warning(f"No RSS URL for source {source.name}")
            return []
        
        articles = []
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                logger.info(f"Fetching RSS feed from {source.name}: {source.rss_url}")
                
                response = await self.session.get(source.rss_url)
                response.raise_for_status()
                
                # Parse RSS feed
                feed = feedparser.parse(response.text)
                
                if feed.bozo:
                    logger.warning(f"RSS feed parsing warning for {source.name}: {feed.bozo_exception}")
                
                # Process entries
                for entry in feed.entries:
                    article_data = self._parse_entry(entry, source)
                    if article_data:
                        articles.append(article_data)
                
                logger.info(f"Successfully fetched {len(articles)} articles from {source.name}")
                break
                
            except httpx.TimeoutException:
                retry_count += 1
                logger.warning(f"Timeout fetching {source.name}, retry {retry_count}/{self.max_retries}")
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {source.name}: {e.response.status_code}")
                break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error fetching {source.name}: {str(e)}, retry {retry_count}/{self.max_retries}")
                if retry_count < self.max_retries:
                    await asyncio.sleep(2 ** retry_count)
        
        return articles
    
    def _parse_entry(self, entry: Any, source: NewsSource) -> Optional[Dict[str, Any]]:
        """
        Parse a single RSS entry into article data
        
        Args:
            entry: RSS entry from feedparser
            source: NewsSource object
            
        Returns:
            Article data dictionary or None if parsing fails
        """
        try:
            # Extract basic information
            title = entry.get('title', '').strip()
            url = entry.get('link', '').strip()
            
            if not title or not url:
                logger.warning(f"Missing title or URL in entry from {source.name}")
                return None
            
            # Generate content hash for deduplication
            content_for_hash = f"{title}{url}".encode('utf-8')
            content_hash = hashlib.sha256(content_for_hash).hexdigest()
            
            # Parse published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_date = datetime(*entry.published_parsed[:6])
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse published date for article: {title}")
            
            # Extract description/summary
            description = entry.get('description', '') or entry.get('summary', '')
            
            # Extract author
            author = entry.get('author', '') or entry.get('dc_creator', '')
            
            return {
                'title': title,
                'link': url,  # Changed from 'url' to 'link' to match Article model
                'content_hash': content_hash,
                'published_date': published_date,
                'summary': description,  # Changed from 'description' to 'summary'
                'source_id': source.id
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry from {source.name}: {str(e)}")
            return None


async def process_single_source(source: NewsSource, db: Session) -> Dict[str, int]:
    """
    Process a single news source
    
    Args:
        source: NewsSource to process
        db: Database session
        
    Returns:
        Dictionary with processing statistics
    """
    stats = {
        'articles_found': 0,
        'articles_new': 0,
        'articles_duplicate': 0,
        'errors': 0
    }
    
    # Create scraping session
    session_record = ScrapingSession(
        source_id=source.id,
        started_at=datetime.utcnow(),
        status='running'
    )
    db.add(session_record)
    db.commit()
    
    try:
        async with RSSFetcher() as fetcher:
            articles_data = await fetcher.fetch_feed(source)
            stats['articles_found'] = len(articles_data)
            
            # Process each article
            for article_data in articles_data:
                try:
                    # Check if article already exists
                    existing = db.query(Article).filter_by(
                        content_hash=article_data['content_hash']
                    ).first()
                    
                    if existing:
                        stats['articles_duplicate'] += 1
                        logger.debug(f"Duplicate article skipped: {article_data['title']}")
                        continue
                    
                    # Create new article
                    article = Article(**article_data)
                    db.add(article)
                    db.commit()
                    
                    stats['articles_new'] += 1
                    logger.info(f"New article saved: {article_data['title']}")
                    
                except IntegrityError:
                    db.rollback()
                    stats['articles_duplicate'] += 1
                    logger.debug(f"Duplicate article (integrity error): {article_data['title']}")
                    
                except Exception as e:
                    db.rollback()
                    stats['errors'] += 1
                    logger.error(f"Error saving article {article_data.get('title', 'Unknown')}: {str(e)}")
        
        # Update session as completed
        session_record.completed_at = datetime.utcnow()
        session_record.status = 'completed'
        session_record.articles_found = stats['articles_found']
        session_record.articles_processed = stats['articles_new']
        
        # Update source last_scraped
        source.last_scraped = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Completed processing {source.name}: {stats}")
        
    except Exception as e:
        # Update session as failed
        session_record.completed_at = datetime.utcnow()
        session_record.status = 'failed'
        session_record.error_message = str(e)
        db.commit()
        
        logger.error(f"Failed to process source {source.name}: {str(e)}")
        stats['errors'] += 1
    
    return stats


async def process_all_feeds(db: Session = None) -> Dict[str, Any]:
    """
    Process all enabled news sources
    
    Args:
        db: Database session (optional, will create one if not provided)
        
    Returns:
        Dictionary with overall processing statistics
    """
    if db is None:
        db = get_db_session()
        should_close = True
    else:
        should_close = False
    
    try:
        # Get all enabled sources
        sources = db.query(NewsSource).filter_by(enabled=True).all()
        
        if not sources:
            logger.warning("No enabled news sources found")
            return {'total_sources': 0, 'total_articles': 0, 'errors': 0}
        
        logger.info(f"Processing {len(sources)} news sources")
        
        # Process sources concurrently with limited concurrency
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent requests
        
        async def process_with_semaphore(source):
            async with semaphore:
                return await process_single_source(source, db)
        
        # Execute all tasks
        tasks = [process_with_semaphore(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate statistics
        total_stats = {
            'total_sources': len(sources),
            'successful_sources': 0,
            'failed_sources': 0,
            'total_articles_found': 0,
            'total_articles_new': 0,
            'total_articles_duplicate': 0,
            'total_errors': 0
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                total_stats['failed_sources'] += 1
                total_stats['total_errors'] += 1
                logger.error(f"Source {sources[i].name} failed: {result}")
            else:
                total_stats['successful_sources'] += 1
                total_stats['total_articles_found'] += result['articles_found']
                total_stats['total_articles_new'] += result['articles_new']
                total_stats['total_articles_duplicate'] += result['articles_duplicate']
                total_stats['total_errors'] += result['errors']
        
        logger.info(f"RSS processing completed: {total_stats}")
        return total_stats
        
    finally:
        if should_close:
            db.close()


def main():
    """Main function for running RSS fetcher standalone"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    from ..storage.database import init_database
    init_database()
    
    # Run RSS processing
    asyncio.run(process_all_feeds())


if __name__ == "__main__":
    main()