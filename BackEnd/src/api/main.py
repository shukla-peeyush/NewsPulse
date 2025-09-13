"""
FastAPI application with comprehensive endpoints
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..storage.database import get_db, test_connection
from ..storage.models_exact import Article, NewsSource
from ..fetcher.rss import process_all_feeds

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="NewsPulse - News Intelligence Platform",
    description="Automated news scraping and intelligence platform for merchant and payments industry",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class ArticleResponse(BaseModel):
    id: str
    title: str
    url: str
    summary: Optional[str] = None
    published_date: Optional[datetime] = None
    scraped_date: datetime
    author: Optional[str] = None
    source_name: Optional[str] = None
    relevance_score: Optional[float] = None
    primary_category: Optional[str] = None
    secondary_categories: Optional[dict] = None
    geographic_tags: Optional[dict] = None
    word_count: Optional[int] = None
    processed: bool = False
    
    class Config:
        from_attributes = True


class NewsSourceResponse(BaseModel):
    id: int
    name: str
    website_url: str
    rss_url: Optional[str] = None
    region: Optional[str] = None
    language: str = "en"
    enabled: bool = True
    last_scraped: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScrapingSessionResponse(BaseModel):
    id: str
    source_name: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    articles_found: int = 0
    articles_processed: int = 0
    articles_relevant: int = 0
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
    total_articles: int
    total_sources: int


class ProcessingStatsResponse(BaseModel):
    total_sources: int
    successful_sources: int
    failed_sources: int
    total_articles_found: int
    total_articles_new: int
    total_articles_duplicate: int
    total_errors: int


# API Endpoints

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NewsPulse - News Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        db_status = "connected" if test_connection() else "disconnected"
        
        # Get basic statistics
        total_articles = db.query(Article).count()
        total_sources = db.query(NewsSource).count()
        
        return HealthResponse(
            status="healthy" if db_status == "connected" else "unhealthy",
            database=db_status,
            timestamp=datetime.utcnow(),
            total_articles=total_articles,
            total_sources=total_sources
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/articles", response_model=List[ArticleResponse], tags=["Articles"])
async def get_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of articles to return"),
    min_relevance_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum relevance score"),
    category: Optional[str] = Query(None, description="Filter by primary category"),
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    processed_only: bool = Query(False, description="Return only processed articles"),
    db: Session = Depends(get_db)
):
    """Get articles with optional filtering and pagination"""
    try:
        # Build query
        query = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id, isouter=True)
        
        # Apply filters
        # Only return articles that have summary data
        query = query.filter(Article.summary.isnot(None)).filter(Article.summary != '')
        
        if min_relevance_score is not None:
            query = query.filter(Article.relevance_score >= min_relevance_score)
        
        if category:
            query = query.filter(Article.primary_category == category)
        
        if source_id:
            query = query.filter(Article.source_id == source_id)
        
        if processed_only:
            query = query.filter(Article.processed == True)
        
        # Order by published date (newest first) and apply pagination
        articles = query.order_by(desc(Article.published_date)).offset(skip).limit(limit).all()
        
        if not articles:
            raise HTTPException(status_code=404, detail="No articles found")
        
        # Convert to response format
        response_articles = []
        for article in articles:
            article_dict = {
                "id": str(article.id),
                "title": article.title,
                "url": getattr(article, 'link', getattr(article, 'url', '')),  # Handle both column names
                "summary": article.summary,
                "published_date": article.published_date,
                "scraped_date": getattr(article, 'scraped_date', article.published_date),  # Fallback to published_date
                "author": getattr(article, 'author', None),
                "source_name": article.source.name if article.source else None,
                "relevance_score": article.relevance_score,
                "primary_category": article.primary_category,
                "secondary_categories": getattr(article, 'secondary_categories', {}),
                "geographic_tags": getattr(article, 'geographic_tags', {}),
                "word_count": getattr(article, 'word_count', None),
                "processed": getattr(article, 'processed', False)
            }
            response_articles.append(ArticleResponse(**article_dict))
        
        return response_articles
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/articles/{article_id}", response_model=ArticleResponse, tags=["Articles"])
async def get_article(article_id: str, db: Session = Depends(get_db)):
    """Get a specific article by ID"""
    try:
        article = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id, isouter=True).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        article_dict = {
            "id": str(article.id),
            "title": article.title,
            "url": getattr(article, 'link', getattr(article, 'url', '')),  # Handle both column names
            "summary": article.summary,
            "published_date": article.published_date,
            "scraped_date": getattr(article, 'scraped_date', article.published_date),  # Fallback to published_date
            "author": getattr(article, 'author', None),
            "source_name": article.source.name if article.source else None,
            "relevance_score": article.relevance_score,
            "primary_category": article.primary_category,
            "secondary_categories": getattr(article, 'secondary_categories', {}),
            "geographic_tags": getattr(article, 'geographic_tags', {}),
            "word_count": getattr(article, 'word_count', None),
            "processed": getattr(article, 'processed', False)
        }
        
        return ArticleResponse(**article_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sources", response_model=List[NewsSourceResponse], tags=["Sources"])
async def get_sources(db: Session = Depends(get_db)):
    """Get all news sources"""
    try:
        sources = db.query(NewsSource).all()
        return [NewsSourceResponse.from_orm(source) for source in sources]
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sources/{source_id}/articles", response_model=List[ArticleResponse], tags=["Sources"])
async def get_source_articles(
    source_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get articles from a specific source"""
    try:
        # Check if source exists
        source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Get articles from this source
        articles = db.query(Article).filter(Article.source_id == source_id).order_by(desc(Article.published_date)).offset(skip).limit(limit).all()
        
        response_articles = []
        for article in articles:
            article_dict = {
                "id": str(article.id),
                "title": article.title,
                "url": getattr(article, 'link', getattr(article, 'url', '')),  # Handle both column names
                "summary": article.summary,
                "published_date": article.published_date,
                "scraped_date": getattr(article, 'scraped_date', article.published_date),  # Fallback to published_date
                "author": getattr(article, 'author', None),
                "source_name": source.name,
                "relevance_score": article.relevance_score,
                "primary_category": article.primary_category,
                "secondary_categories": getattr(article, 'secondary_categories', {}),
                "geographic_tags": getattr(article, 'geographic_tags', {}),
                "word_count": getattr(article, 'word_count', None),
                "processed": getattr(article, 'processed', False)
            }
            response_articles.append(ArticleResponse(**article_dict))
        
        return response_articles
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching articles for source {source_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/scraping-sessions", response_model=List[ScrapingSessionResponse], tags=["Scraping"])
async def get_scraping_sessions(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get recent scraping sessions"""
    try:
        sessions = db.query(ScrapingSession).join(NewsSource, ScrapingSession.source_id == NewsSource.id, isouter=True).order_by(desc(ScrapingSession.started_at)).limit(limit).all()
        
        response_sessions = []
        for session in sessions:
            session_dict = {
                "id": str(session.id),
                "source_name": session.source.name if session.source else None,
                "started_at": session.started_at,
                "completed_at": session.completed_at,
                "status": session.status,
                "articles_found": session.articles_found,
                "articles_processed": session.articles_processed,
                "articles_relevant": session.articles_relevant,
                "error_message": session.error_message
            }
            response_sessions.append(ScrapingSessionResponse(**session_dict))
        
        return response_sessions
        
    except Exception as e:
        logger.error(f"Error fetching scraping sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/scrape", response_model=ProcessingStatsResponse, tags=["Scraping"])
async def trigger_scraping(db: Session = Depends(get_db)):
    """Manually trigger RSS feed scraping"""
    try:
        logger.info("Manual scraping triggered via API")
        results = await process_all_feeds(db)
        
        return ProcessingStatsResponse(**results)
        
    except Exception as e:
        logger.error(f"Error during manual scraping: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed")


@app.get("/categories", tags=["Analytics"])
async def get_categories(db: Session = Depends(get_db)):
    """Get all available article categories with counts"""
    try:
        # Get distinct categories with counts
        categories = db.query(Article.primary_category, db.func.count(Article.id).label('count')).filter(Article.primary_category.isnot(None)).group_by(Article.primary_category).all()
        
        return {
            "categories": [{"name": cat[0], "count": cat[1]} for cat in categories],
            "total_categories": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/stats", tags=["Analytics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get platform statistics"""
    try:
        total_articles = db.query(Article).count()
        processed_articles = db.query(Article).filter(Article.processed == True).count()
        total_sources = db.query(NewsSource).count()
        enabled_sources = db.query(NewsSource).filter(NewsSource.enabled == True).count()
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(Article).filter(Article.published_date >= yesterday).count()
        
        return {
            "total_articles": total_articles,
            "processed_articles": processed_articles,
            "unprocessed_articles": total_articles - processed_articles,
            "total_sources": total_sources,
            "enabled_sources": enabled_sources,
            "recent_articles_24h": recent_articles,
            "processing_rate": round((processed_articles / total_articles * 100), 2) if total_articles > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Pydantic model for summary response
class ArticleSummaryResponse(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    published_date: Optional[datetime] = None
    source_name: Optional[str] = None
    
    class Config:
        from_attributes = True


@app.get("/articles/{article_id}/summary", response_model=ArticleSummaryResponse, tags=["Articles"])
async def get_article_summary(article_id: str, db: Session = Depends(get_db)):
    """Get summary for a specific article by ID"""
    try:
        # Query for the specific article
        article = db.query(Article).join(
            NewsSource, 
            Article.source_id == NewsSource.id, 
            isouter=True
        ).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Return article with full summary
        return ArticleSummaryResponse(
            id=str(article.id),
            title=article.title,
            summary=article.summary,  # RAW HTML summary from database
            content=article.content,  # Use correct column name
            url=article.link,  # Use correct column name 'link' not 'url'
            published_date=article.published_date,
            source_name=article.source.name if article.source else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article summary {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)