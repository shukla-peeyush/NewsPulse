"""
News Fetching Service
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

from ..models import NewsSource, Article
from ..config import settings

logger = logging.getLogger(__name__)


class NewsFetcher:
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
        
        try:
            logger.info(f"Fetching RSS feed: {source.rss_url}")
            
            response = await self.session.get(source.rss_url)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.text)
            
            if feed.bozo:
                logger.warning(f"RSS feed parsing issues for {source.name}: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                article_data = self._parse_entry(entry, source)
                if article_data:
                    articles.append(article_data)
            
            logger.info(f"Fetched {len(articles)} articles from {source.name}")
            return articles
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {source.rss_url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS feed {source.rss_url}: {e}")
            return []
    
    def _parse_entry(self, entry: Any, source: NewsSource) -> Optional[Dict[str, Any]]:
        """
        Parse individual RSS entry into article data
        
        Args:
            entry: RSS entry from feedparser
            source: NewsSource object
            
        Returns:
            Article data dictionary or None if parsing fails
        """
        try:
            # Extract basic fields
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()
            
            if not title or not link:
                logger.warning(f"Missing title or link in entry from {source.name}")
                return None
            
            # Extract description/summary
            summary = entry.get('summary', '') or entry.get('description', '')
            
            # Parse published date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_date = datetime(*entry.published_parsed[:6])
                except (ValueError, TypeError):
                    pass
            
            # Generate content hash for deduplication
            content_for_hash = f"{title}{link}{source.id}"
            content_hash = hashlib.sha256(content_for_hash.encode()).hexdigest()
            
            return {
                'source_id': source.id,
                'title': title[:500],  # Truncate to fit database
                'link': link[:1000],
                'summary': summary,
                'published_date': published_date,
                'content_hash': content_hash,
                'processed': 'pending'
            }
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    async def fetch_all_sources(self, db: Session) -> Dict[str, Any]:
        """
        Fetch articles from all enabled news sources
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with fetching results
        """
        # Get all enabled sources
        sources = db.query(NewsSource).filter(NewsSource.enabled == True).all()
        
        if not sources:
            logger.warning("No enabled news sources found")
            return {'total_articles': 0, 'sources_processed': 0, 'errors': []}
        
        logger.info(f"Fetching from {len(sources)} news sources")
        
        # Fetch from all sources concurrently
        tasks = [self.fetch_feed(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_articles = 0
        sources_processed = 0
        errors = []
        
        # Process results and save articles
        for i, result in enumerate(results):
            source = sources[i]
            
            if isinstance(result, Exception):
                error_msg = f"Error fetching from {source.name}: {result}"
                logger.error(error_msg)
                errors.append(error_msg)
                continue
            
            if isinstance(result, list):
                # Save articles to database
                saved_count = self._save_articles(db, result)
                total_articles += saved_count
                sources_processed += 1
                
                # Update source last_scraped timestamp
                source.last_scraped = datetime.utcnow()
                
                logger.info(f"Saved {saved_count} articles from {source.name}")
        
        # Commit all changes
        try:
            db.commit()
        except Exception as e:
            logger.error(f"Error committing to database: {e}")
            db.rollback()
            errors.append(f"Database commit error: {e}")
        
        return {
            'total_articles': total_articles,
            'sources_processed': sources_processed,
            'total_sources': len(sources),
            'errors': errors
        }
    
    def _save_articles(self, db: Session, articles: List[Dict[str, Any]]) -> int:
        """
        Save articles to database with duplicate handling
        
        Args:
            db: Database session
            articles: List of article dictionaries
            
        Returns:
            Number of articles saved
        """
        saved_count = 0
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = db.query(Article).filter(
                    Article.content_hash == article_data['content_hash']
                ).first()
                
                if existing:
                    logger.debug(f"Article already exists: {article_data['title'][:50]}...")
                    continue
                
                # Create new article
                article = Article(**article_data)
                db.add(article)
                saved_count += 1
                
            except IntegrityError:
                logger.debug(f"Duplicate article detected: {article_data['title'][:50]}...")
                db.rollback()
                continue
            except Exception as e:
                logger.error(f"Error saving article: {e}")
                db.rollback()
                continue
        
        return saved_count


# Convenience function for manual fetching
async def fetch_news_manually(db: Session) -> Dict[str, Any]:
    """
    Manually trigger news fetching from all sources
    
    Args:
        db: Database session
        
    Returns:
        Fetching results
    """
    async with NewsFetcher() as fetcher:
        return await fetcher.fetch_all_sources(db)