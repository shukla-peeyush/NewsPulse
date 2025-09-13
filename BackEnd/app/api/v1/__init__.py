"""
API v1 Package
"""

from fastapi import APIRouter
from .articles import router as articles_router
from .sources import router as sources_router
from .analytics import router as analytics_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
api_router.include_router(sources_router, prefix="/sources", tags=["sources"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

__all__ = ["api_router"]