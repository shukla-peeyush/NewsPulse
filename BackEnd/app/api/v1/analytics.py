"""
Analytics API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ...database import get_db
from ...models import Article, NewsSource
from ...services import ArticleClassifier

router = APIRouter()

# Initialize classifier for category stats
classifier = ArticleClassifier()


@router.get("/stats")
async def get_platform_stats(
    db: Session = Depends(get_db)
):
    """
    Get overall platform statistics
    """
    try:
        # Basic counts
        total_articles = db.query(Article).count()
        total_sources = db.query(NewsSource).count()
        enabled_sources = db.query(NewsSource).filter(NewsSource.enabled == True).count()
        
        # Processing stats
        processed_articles = db.query(Article).filter(Article.processed == 'processed').count()
        pending_articles = db.query(Article).filter(Article.processed == 'pending').count()
        failed_articles = db.query(Article).filter(Article.processed == 'failed').count()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_articles = db.query(Article).filter(Article.created_at >= yesterday).count()
        
        # Category distribution
        category_stats = classifier.get_category_stats(db)
        
        # Average relevance score
        avg_relevance = db.query(func.avg(Article.relevance_score)).filter(
            Article.relevance_score.isnot(None)
        ).scalar()
        
        return {
            "total_articles": total_articles,
            "total_sources": total_sources,
            "enabled_sources": enabled_sources,
            "processing_stats": {
                "processed": processed_articles,
                "pending": pending_articles,
                "failed": failed_articles,
                "processing_rate": round((processed_articles / max(total_articles, 1)) * 100, 2)
            },
            "recent_activity": {
                "articles_last_24h": recent_articles
            },
            "category_stats": category_stats,
            "average_relevance_score": round(avg_relevance or 0, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching platform stats: {str(e)}")


@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_db)
):
    """
    Get article categories with counts
    """
    try:
        # Get category counts from database
        category_counts = db.query(
            Article.primary_category,
            func.count(Article.id).label('count')
        ).filter(
            Article.primary_category.isnot(None)
        ).group_by(Article.primary_category).all()
        
        # Format response
        categories = []
        for category, count in category_counts:
            categories.append({
                "name": category,
                "count": count
            })
        
        # Sort by count descending
        categories.sort(key=lambda x: x['count'], reverse=True)
        
        # Get total classified articles
        total_classified = sum(cat['count'] for cat in categories)
        
        # Get unclassified count
        unclassified = db.query(Article).filter(Article.primary_category.is_(None)).count()
        
        return {
            "categories": categories,
            "total_classified": total_classified,
            "unclassified": unclassified,
            "total_articles": total_classified + unclassified
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")


@router.get("/sources/performance")
async def get_source_performance(
    db: Session = Depends(get_db)
):
    """
    Get news source performance metrics
    """
    try:
        # Get source performance data
        source_stats = db.query(
            NewsSource.id,
            NewsSource.name,
            NewsSource.enabled,
            func.count(Article.id).label('total_articles'),
            func.avg(Article.relevance_score).label('avg_relevance'),
            func.max(Article.created_at).label('last_article'),
            func.count(func.nullif(Article.processed == 'processed', False)).label('processed_count')
        ).outerjoin(Article).group_by(NewsSource.id).all()
        
        performance_data = []
        for stat in source_stats:
            performance_data.append({
                "source_id": stat.id,
                "source_name": stat.name,
                "enabled": stat.enabled,
                "total_articles": stat.total_articles or 0,
                "avg_relevance_score": round(stat.avg_relevance or 0, 2),
                "last_article_date": stat.last_article,
                "processed_articles": stat.processed_count or 0,
                "processing_rate": round(
                    ((stat.processed_count or 0) / max(stat.total_articles or 1, 1)) * 100, 2
                )
            })
        
        # Sort by total articles descending
        performance_data.sort(key=lambda x: x['total_articles'], reverse=True)
        
        return {
            "source_performance": performance_data,
            "total_sources": len(performance_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching source performance: {str(e)}")


@router.get("/trends/daily")
async def get_daily_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get daily article trends for the last N days
    """
    try:
        if days > 30:
            days = 30  # Limit to 30 days
        
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get daily article counts
        daily_counts = db.query(
            func.date(Article.created_at).label('date'),
            func.count(Article.id).label('count')
        ).filter(
            func.date(Article.created_at) >= start_date
        ).group_by(func.date(Article.created_at)).all()
        
        # Create complete date range with zero counts for missing days
        trends = []
        current_date = start_date
        count_dict = {str(date): count for date, count in daily_counts}
        
        while current_date <= end_date:
            date_str = str(current_date)
            trends.append({
                "date": date_str,
                "article_count": count_dict.get(date_str, 0)
            })
            current_date += timedelta(days=1)
        
        return {
            "trends": trends,
            "period_days": days,
            "total_articles": sum(trend['article_count'] for trend in trends)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily trends: {str(e)}")


@router.get("/relevance/distribution")
async def get_relevance_distribution(
    db: Session = Depends(get_db)
):
    """
    Get distribution of article relevance scores
    """
    try:
        # Define score ranges
        score_ranges = [
            (1, 20, "Very Low"),
            (21, 40, "Low"),
            (41, 60, "Medium"),
            (61, 80, "High"),
            (81, 100, "Very High")
        ]
        
        distribution = []
        total_scored = 0
        
        for min_score, max_score, label in score_ranges:
            count = db.query(Article).filter(
                Article.relevance_score >= min_score,
                Article.relevance_score <= max_score
            ).count()
            
            distribution.append({
                "range": f"{min_score}-{max_score}",
                "label": label,
                "count": count
            })
            total_scored += count
        
        # Get unscored articles
        unscored = db.query(Article).filter(Article.relevance_score.is_(None)).count()
        
        return {
            "distribution": distribution,
            "total_scored": total_scored,
            "unscored": unscored,
            "total_articles": total_scored + unscored
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching relevance distribution: {str(e)}")