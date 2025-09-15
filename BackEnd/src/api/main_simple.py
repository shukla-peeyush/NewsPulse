"""
Simplified FastAPI application matching actual database schema
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..storage.database import get_db, test_connection
from ..storage.models_simple import Article, NewsSource, ScrapingSession

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
    allow_origins=["*"],
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
    content: Optional[str] = None
    published_date: Optional[datetime] = None
    source_name: Optional[str] = None
    relevance_score: Optional[int] = None
    primary_category: Optional[str] = None
    confidence_level: Optional[str] = None
    
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


class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime
    total_articles: int
    total_sources: int


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
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/articles", response_model=List[ArticleResponse], tags=["Articles"])
async def get_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of articles to return"),
    min_relevance_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum relevance score"),
    category: Optional[str] = Query(None, description="Filter by primary category"),
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    db: Session = Depends(get_db)
):
    """Get articles with optional filtering and pagination"""
    try:
        # Build query
        query = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id, isouter=True)
        
        # Apply filters
        if min_relevance_score is not None:
            query = query.filter(Article.relevance_score >= min_relevance_score)
        
        if category:
            query = query.filter(Article.primary_category == category)
        
        if source_id:
            query = query.filter(Article.source_id == source_id)
        
        # Order by published date (newest first) and apply pagination
        articles = query.order_by(desc(Article.published_date)).offset(skip).limit(limit).all()
        
        if not articles:
            return []  # Return empty list instead of 404
        
        # Convert to response format
        response_articles = []
        for article in articles:
            article_dict = {
                "id": str(article.id),
                "title": article.title,
                "url": article.link,  # Map link to url for API response
                "summary": article.summary,
                "content": article.content,
                "published_date": article.published_date,
                "source_name": article.source.name if article.source else None,
                "relevance_score": article.relevance_score,
                "primary_category": article.primary_category,
                "confidence_level": article.confidence_level
            }
            response_articles.append(ArticleResponse(**article_dict))
        
        return response_articles
        
    except Exception as e:
        logger.error(f"Error fetching articles: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
            "url": article.link,  # Map link to url for API response
            "summary": article.summary,
            "content": article.content,
            "published_date": article.published_date,
            "source_name": article.source.name if article.source else None,
            "relevance_score": article.relevance_score,
            "primary_category": article.primary_category,
            "confidence_level": article.confidence_level
        }
        
        return ArticleResponse(**article_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/articles/{article_id}/summary", tags=["Articles"])
async def get_article_summary(article_id: str, db: Session = Depends(get_db)):
    """Get enhanced summary for a specific article"""
    try:
        # Handle UUID string conversion
        import uuid
        try:
            # Try to parse as UUID
            uuid_obj = uuid.UUID(article_id)
            article = db.query(Article).filter(Article.id == uuid_obj).first()
        except ValueError:
            # If not a valid UUID, try as string
            article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Return enhanced summary (for now, just return the existing summary)
        # In the future, this could generate AI-enhanced summaries
        return {
            "summary": article.summary or "No summary available",
            "content": article.content or "",
            "title": article.title,
            "source_name": article.source.name if article.source else None,
            "primary_category": article.primary_category,
            "relevance_score": article.relevance_score,
            "confidence_level": article.confidence_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching summary for article {article_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/sources", response_model=List[NewsSourceResponse], tags=["Sources"])
async def get_sources(db: Session = Depends(get_db)):
    """Get all news sources"""
    try:
        sources = db.query(NewsSource).all()
        return [NewsSourceResponse.from_orm(source) for source in sources]
        
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
                "url": article.link,  # Map link to url for API response
                "summary": article.summary,
                "content": article.content,
                "published_date": article.published_date,
                "source_name": source.name,
                "relevance_score": article.relevance_score,
                "primary_category": article.primary_category,
                "confidence_level": article.confidence_level
            }
            response_articles.append(ArticleResponse(**article_dict))
        
        return response_articles
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching articles for source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/stats", tags=["Analytics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Get platform statistics"""
    try:
        total_articles = db.query(Article).count()
        total_sources = db.query(NewsSource).count()
        enabled_sources = db.query(NewsSource).filter(NewsSource.enabled == True).count()
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(Article).filter(Article.published_date >= yesterday).count()
        
        return {
            "total_articles": total_articles,
            "total_sources": total_sources,
            "enabled_sources": enabled_sources,
            "recent_articles_24h": recent_articles
        }
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)