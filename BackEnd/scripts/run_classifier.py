"""
Manual Article Classification Script
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models import Article
from app.services import ArticleClassifier
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Run article classification manually"""
    
    logger.info("Starting manual article classification...")
    
    db = SessionLocal()
    classifier = ArticleClassifier()
    
    try:
        # Get unclassified articles
        unclassified_articles = db.query(Article).filter(
            Article.primary_category.is_(None)
        ).all()
        
        if not unclassified_articles:
            print("No unclassified articles found!")
            return
        
        print(f"Found {len(unclassified_articles)} unclassified articles")
        
        classified_count = 0
        failed_count = 0
        
        for article in unclassified_articles:
            try:
                # Classify article
                classification = classifier.classify_article(
                    article.title or "",
                    article.summary or "",
                    article.content or ""
                )
                
                # Update article
                success = classifier.update_article_classification(article, classification)
                
                if success:
                    classified_count += 1
                    logger.info(f"Classified: {article.title[:50]}... -> {classification['primary_category']}")
                else:
                    failed_count += 1
                    logger.error(f"Failed to classify: {article.title[:50]}...")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Error classifying article {article.id}: {e}")
        
        # Commit changes
        db.commit()
        
        print("\n" + "="*50)
        print("CLASSIFICATION RESULTS")
        print("="*50)
        print(f"Total articles processed: {len(unclassified_articles)}")
        print(f"Successfully classified: {classified_count}")
        print(f"Failed: {failed_count}")
        
        # Show category distribution
        category_stats = classifier.get_category_stats(db)
        if category_stats.get('category_counts'):
            print("\nCategory Distribution:")
            for category, count in category_stats['category_counts'].items():
                if count > 0:
                    print(f"  {category}: {count}")
        
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()