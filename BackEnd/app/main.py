"""
NewsPulse FastAPI Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import test_connection, create_tables
from .api import api_router
from .services import NewsFetcher


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting NewsPulse application...")
    
    # Test database connection
    if not test_connection():
        logger.error("Database connection failed!")
        raise Exception("Database connection failed")
    
    # Create tables if they don't exist
    create_tables()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NewsPulse application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Automated news scraping and intelligence platform for merchant and payments industry",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API welcome and basic information"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "description": "News Intelligence Platform",
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """System health check and database statistics"""
    try:
        from .database import get_db
        from .models import Article, NewsSource
        
        # Test database connection
        db_healthy = test_connection()
        
        if not db_healthy:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            )
        
        # Get database statistics
        db = next(get_db())
        try:
            total_articles = db.query(Article).count()
            total_sources = db.query(NewsSource).count()
            enabled_sources = db.query(NewsSource).filter(NewsSource.enabled == True).count()
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            total_articles = total_sources = enabled_sources = 0
        finally:
            db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "statistics": {
                "total_articles": total_articles,
                "total_sources": total_sources,
                "enabled_sources": enabled_sources
            },
            "version": settings.app_version,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        )


# Manual scraping endpoint
@app.post("/scrape")
async def trigger_scraping():
    """Manually trigger RSS feed scraping"""
    try:
        from .database import get_db
        from .services import fetch_news_manually
        
        db = next(get_db())
        try:
            result = await fetch_news_manually(db)
            
            return {
                "message": "Scraping completed",
                "result": result,
                "success": True
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Manual scraping error: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


# Legacy endpoints for backward compatibility
@app.get("/articles")
async def get_articles_legacy(
    skip: int = 0,
    limit: int = 100,
    min_relevance_score: int = None,
    category: str = None,
    source_id: int = None,
    processed_only: bool = None
):
    """Legacy articles endpoint - redirects to v1 API"""
    from .api.v1.articles import get_articles
    from .database import get_db
    
    db = next(get_db())
    try:
        return await get_articles(
            skip=skip,
            limit=limit,
            category=category,
            source_id=source_id,
            min_relevance_score=min_relevance_score,
            processed_only=processed_only,
            db=db
        )
    finally:
        db.close()


@app.get("/sources")
async def get_sources_legacy():
    """Legacy sources endpoint - redirects to v1 API"""
    from .api.v1.sources import get_sources
    from .database import get_db
    
    db = next(get_db())
    try:
        return await get_sources(db=db)
    finally:
        db.close()


@app.get("/categories")
async def get_categories_legacy():
    """Legacy categories endpoint - redirects to v1 API"""
    from .api.v1.analytics import get_categories
    from .database import get_db
    
    db = next(get_db())
    try:
        return await get_categories(db=db)
    finally:
        db.close()


@app.get("/stats")
async def get_stats_legacy():
    """Legacy stats endpoint - redirects to v1 API"""
    from .api.v1.analytics import get_platform_stats
    from .database import get_db
    
    db = next(get_db())
    try:
        return await get_platform_stats(db=db)
    finally:
        db.close()


# Include API router
app.include_router(api_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )