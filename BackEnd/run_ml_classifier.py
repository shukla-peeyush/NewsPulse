"""
Script to run ML-based classifier
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.classifier.ml_classifier import MLClassifier, TRANSFORMERS_AVAILABLE
from src.storage.database import get_db_session
from src.storage.models import Article
from sqlalchemy import and_

async def classify_articles_with_ml(batch_size: int = 20):
    """Classify articles using ML classifier"""
    
    if not TRANSFORMERS_AVAILABLE:
        print("Transformers not available. Please install with:")
        print("pip install transformers torch scikit-learn")
        return
    
    db = get_db_session()
    
    try:
        # Initialize ML classifier
        classifier = MLClassifier()
        
        if not classifier.model_loaded:
            print("ML models could not be loaded")
            return
        
        # Get unclassified articles or articles with low confidence
        articles = db.query(Article).filter(
            and_(
                Article.title.isnot(None),
                # Either not classified or low confidence from keyword classifier
                Article.confidence_level.in_(['very_low', 'low'])
            )
        ).limit(batch_size).all()
        
        if not articles:
            print("No articles need ML classification")
            return
        
        print(f"Processing {len(articles)} articles with ML classifier...")
        
        successful = 0
        failed = 0
        
        for article in articles:
            try:
                result = classifier.classify_article(article)
                
                if result['success']:
                    # Update article with ML classification results
                    article.relevance_score = result['relevance_score']
                    article.primary_category = result['primary_category']
                    article.confidence_level = result['confidence_level']
                    article.secondary_categories = result['secondary_categories']
                    article.geographic_tags = result['geographic_tags']
                    article.industry_segments = result['industry_segments']
                    article.classified = True
                    
                    print(f"✓ {article.title[:50]}... - Score: {result['relevance_score']}, Category: {result['primary_category']}")
                    successful += 1
                else:
                    print(f"✗ Failed to classify: {article.title[:50]}...")
                    failed += 1
                    
            except Exception as e:
                print(f"✗ Error processing {article.title[:50]}...: {e}")
                failed += 1
        
        # Commit changes
        db.commit()
        
        print(f"\nML Classification completed:")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(articles)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error during ML classification: {e}")
        raise
    finally:
        db.close()

async def main():
    """Main function for ML classifier"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ML-based classifier...")
    
    try:
        await classify_articles_with_ml(batch_size=50)
        
    except Exception as e:
        logger.error(f"ML classifier failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())