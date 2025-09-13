"""
Articles API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from uuid import UUID

from ...database import get_db
from ...models import Article, NewsSource
from ...schemas import ArticleResponse, ArticleListResponse
from ...services import ContentExtractor, ArticleClassifier

router = APIRouter()

# Initialize services
content_extractor = ContentExtractor()
classifier = ArticleClassifier()


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of articles to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    source_id: Optional[int] = Query(None, description="Filter by source ID"),
    min_relevance_score: Optional[int] = Query(None, ge=1, le=100, description="Minimum relevance score"),
    processed_only: Optional[bool] = Query(None, description="Only return processed articles"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of articles with optional filtering
    """
    try:
        # Build query
        query = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id)
        
        # Apply filters
        if category:
            query = query.filter(Article.primary_category == category.lower())
        
        if source_id:
            query = query.filter(Article.source_id == source_id)
        
        if min_relevance_score:
            query = query.filter(Article.relevance_score >= min_relevance_score)
        
        if processed_only is not None:
            if processed_only:
                query = query.filter(Article.processed == 'processed')
            else:
                query = query.filter(Article.processed != 'processed')
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        articles = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
        
        # Add source names to articles
        for article in articles:
            if article.source:
                article.source_name = article.source.name
        
        return ArticleListResponse(
            articles=articles,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + limit < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get specific article by ID
    """
    try:
        article = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id).filter(
            Article.id == article_id
        ).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Add source name
        if article.source:
            article.source_name = article.source.name
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")


@router.post("/{article_id}/extract-content")
async def extract_article_content(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Extract full content for a specific article
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Extract content
        extracted_data = await content_extractor.extract_content_async(article.link)
        
        # Update article with extracted content
        success = content_extractor.update_article_content(article, extracted_data)
        
        if success:
            db.commit()
            return {"message": "Content extracted successfully", "success": True}
        else:
            db.rollback()
            return {"message": "Content extraction failed", "success": False}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")


@router.post("/{article_id}/classify")
async def classify_article(
    article_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Classify a specific article
    """
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Classify article
        classification = classifier.classify_article(
            article.title or "",
            article.summary or "",
            article.content or ""
        )
        
        # Update article with classification
        success = classifier.update_article_classification(article, classification)
        
        if success:
            db.commit()
            return {
                "message": "Article classified successfully",
                "classification": classification,
                "success": True
            }
        else:
            db.rollback()
            return {"message": "Classification failed", "success": False}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error classifying article: {str(e)}")


@router.get("/category/{category}")
async def get_articles_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get articles by category
    """
    try:
        query = db.query(Article).join(NewsSource, Article.source_id == NewsSource.id).filter(
            Article.primary_category == category.lower()
        )
        
        total = query.count()
        articles = query.order_by(desc(Article.created_at)).offset(skip).limit(limit).all()
        
        # Add source names
        for article in articles:
            if article.source:
                article.source_name = article.source.name
        
        return ArticleListResponse(
            articles=articles,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + limit < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles by category: {str(e)}")