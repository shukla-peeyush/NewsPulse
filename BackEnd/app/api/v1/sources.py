"""
News Sources API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List

from ...database import get_db
from ...models import NewsSource, Article
from ...schemas import NewsSourceResponse, NewsSourceCreate, NewsSourceUpdate, NewsSourceWithStats

router = APIRouter()


@router.get("/", response_model=List[NewsSourceResponse])
async def get_sources(
    enabled_only: bool = Query(False, description="Only return enabled sources"),
    db: Session = Depends(get_db)
):
    """
    Get all news sources
    """
    try:
        query = db.query(NewsSource)
        
        if enabled_only:
            query = query.filter(NewsSource.enabled == True)
        
        sources = query.order_by(NewsSource.priority.desc(), NewsSource.name).all()
        return sources
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")


@router.get("/stats", response_model=List[NewsSourceWithStats])
async def get_sources_with_stats(
    db: Session = Depends(get_db)
):
    """
    Get news sources with article statistics
    """
    try:
        # Query sources with article counts
        sources_with_stats = db.query(
            NewsSource,
            func.count(Article.id).label('article_count'),
            func.max(Article.created_at).label('last_article_date')
        ).outerjoin(Article).group_by(NewsSource.id).all()
        
        result = []
        for source, article_count, last_article_date in sources_with_stats:
            source_dict = {
                **source.__dict__,
                'article_count': article_count or 0,
                'last_article_date': last_article_date
            }
            result.append(NewsSourceWithStats(**source_dict))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching source stats: {str(e)}")


@router.get("/{source_id}", response_model=NewsSourceResponse)
async def get_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific news source by ID
    """
    try:
        source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        
        if not source:
            raise HTTPException(status_code=404, detail="News source not found")
        
        return source
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching source: {str(e)}")


@router.get("/{source_id}/articles")
async def get_source_articles(
    source_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get articles from a specific news source
    """
    try:
        # Verify source exists
        source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="News source not found")
        
        # Get articles from this source
        query = db.query(Article).filter(Article.source_id == source_id)
        total = query.count()
        
        articles = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
        
        # Add source name to articles
        for article in articles:
            article.source_name = source.name
        
        return {
            "source": source,
            "articles": articles,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching source articles: {str(e)}")


@router.post("/", response_model=NewsSourceResponse)
async def create_source(
    source: NewsSourceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new news source
    """
    try:
        # Check if source with same name already exists
        existing = db.query(NewsSource).filter(NewsSource.name == source.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Source with this name already exists")
        
        # Create new source
        db_source = NewsSource(**source.dict())
        db.add(db_source)
        db.commit()
        db.refresh(db_source)
        
        return db_source
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating source: {str(e)}")


@router.put("/{source_id}", response_model=NewsSourceResponse)
async def update_source(
    source_id: int,
    source_update: NewsSourceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a news source
    """
    try:
        # Get existing source
        db_source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        if not db_source:
            raise HTTPException(status_code=404, detail="News source not found")
        
        # Update fields
        update_data = source_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_source, field, value)
        
        db.commit()
        db.refresh(db_source)
        
        return db_source
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating source: {str(e)}")


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a news source
    """
    try:
        # Get existing source
        db_source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        if not db_source:
            raise HTTPException(status_code=404, detail="News source not found")
        
        # Check if source has articles
        article_count = db.query(Article).filter(Article.source_id == source_id).count()
        if article_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete source with {article_count} articles. Disable it instead."
            )
        
        # Delete source
        db.delete(db_source)
        db.commit()
        
        return {"message": "News source deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting source: {str(e)}")


@router.post("/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    db: Session = Depends(get_db)
):
    """
    Toggle source enabled/disabled status
    """
    try:
        # Get existing source
        db_source = db.query(NewsSource).filter(NewsSource.id == source_id).first()
        if not db_source:
            raise HTTPException(status_code=404, detail="News source not found")
        
        # Toggle enabled status
        db_source.enabled = not db_source.enabled
        db.commit()
        db.refresh(db_source)
        
        status = "enabled" if db_source.enabled else "disabled"
        return {
            "message": f"Source {status} successfully",
            "source": db_source
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error toggling source: {str(e)}")