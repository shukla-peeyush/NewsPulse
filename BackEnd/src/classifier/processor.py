"""
Article classification processor
"""

import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..storage.models import Article
from ..storage.database import get_db_session
from .keyword_classifier import KeywordClassifier

logger = logging.getLogger(__name__)


async def classify_article(article: Article, classifier: KeywordClassifier) -> bool:
    """
    Classify a single article
    
    Args:
        article: Article object to classify
        classifier: KeywordClassifier instance
        
    Returns:
        True if classification was successful, False otherwise
    """
    try:
        logger.info(f"Classifying article: {article.title}")
        
        # Classify article
        result = classifier.classify_article(article)
        
        # Update article with classification results
        if result['success']:
            article.relevance_score = result['relevance_score']
            article.primary_category = result['primary_category']
            article.secondary_categories = result['secondary_categories']
            article.confidence_level = result['confidence_level']
            article.geographic_tags = result['geographic_tags']
            article.industry_segments = result['industry_segments']
            article.classified = True
            
            logger.info(f"Article classified - Score: {result['relevance_score']}, Category: {result['primary_category']}")
            return True
        else:
            article.classified = False
            article.processing_errors = result.get('error', 'Classification failed')
            logger.warning(f"Classification failed for: {article.title}")
            return False
            
    except Exception as e:
        article.classified = False
        article.processing_errors = str(e)
        logger.error(f"Error classifying article {article.title}: {str(e)}")
        return False


async def process_articles_batch(articles: List[Article]) -> Dict[str, int]:
    """
    Process a batch of articles for classification
    
    Args:
        articles: List of Article objects to classify
        
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
    
    logger.info(f"Processing batch of {len(articles)} articles for classification")
    
    classifier = KeywordClassifier()
    
    # Process articles sequentially (classification is fast)
    for article in articles:
        try:
            success = await classify_article(article, classifier)
            if success:
                stats['successful'] += 1
            else:
                stats['failed'] += 1
        except Exception as e:
            logger.error(f"Error processing article {article.id}: {str(e)}")
            stats['failed'] += 1
    
    logger.info(f"Batch processing completed: {stats}")
    return stats


async def process_unclassified_articles(db: Session = None, batch_size: int = 50) -> Dict[str, int]:
    """
    Process all articles that haven't been classified
    
    Args:
        db: Database session (optional)
        batch_size: Number of articles to process in each batch
        
    Returns:
        Dictionary with overall processing statistics
    """
    if db is None:
        db = get_db_session()
        should_close = True
    else:
        should_close = False
    
    try:
        # Get articles that need classification
        unclassified_articles = db.query(Article).filter(
            and_(
                Article.classified == False,
                Article.title.isnot(None)
            )
        ).limit(batch_size).all()
        
        if not unclassified_articles:
            logger.info("No articles need classification")
            return {'total': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Found {len(unclassified_articles)} articles needing classification")
        
        # Process articles
        stats = await process_articles_batch(unclassified_articles)
        
        # Commit changes to database
        db.commit()
        
        return stats
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing unclassified articles: {str(e)}")
        raise
    finally:
        if should_close:
            db.close()


def main():
    """Main function for running classifier standalone"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run classification
    asyncio.run(process_unclassified_articles())


if __name__ == "__main__":
    main()