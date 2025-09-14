#!/usr/bin/env python3
"""
Advanced ML Classifier Script for NewsPulse
Classifies news articles using FinBERT model and updates database records
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('classifier.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger.info("✅ Transformers library loaded successfully")
except ImportError as e:
    TRANSFORMERS_AVAILABLE = False
    logger.error(f"❌ Transformers library not available: {e}")
    logger.error("💡 Install with: pip install transformers torch")

try:
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import SQLAlchemyError
    from src.storage.database import get_db_session, engine
    from src.storage.models_simple import Article
    SQLALCHEMY_AVAILABLE = True
    logger.info("✅ SQLAlchemy and database models loaded successfully")
except ImportError as e:
    SQLALCHEMY_AVAILABLE = False
    logger.error(f"❌ Database modules not available: {e}")


class FinBERTClassifier:
    """FinBERT-based news article classifier for financial domain"""
    
    # Predefined categories for NewsPulse
    CATEGORIES = {
        'PAYMENTS': ['payment', 'transaction', 'processing', 'gateway', 'merchant'],
        'FUNDING': ['funding', 'investment', 'venture', 'capital', 'round', 'raised'],
        'REGULATION': ['regulation', 'compliance', 'regulatory', 'law', 'policy', 'government'],
        'PRODUCT LAUNCH': ['launch', 'product', 'feature', 'release', 'announce', 'unveil'],
        'MERGERS & ACQUISITIONS': ['merger', 'acquisition', 'acquire', 'buyout', 'takeover'],
        'CRYPTO': ['crypto', 'cryptocurrency', 'bitcoin', 'blockchain', 'digital currency'],
        'FINANCIAL CRIME': ['fraud', 'crime', 'money laundering', 'aml', 'kyc', 'security breach']
    }
    
    def __init__(self, model_name: str = "ProsusAI/finbert", batch_size: int = 8):
        """Initialize the FinBERT classifier"""
        self.model_name = model_name
        self.batch_size = batch_size
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"🤖 Initializing FinBERT Classifier")
        logger.info(f"📱 Device: {self.device}")
        
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load the FinBERT model and tokenizer"""
        try:
            logger.info(f"📥 Loading model: {self.model_name}")
            
            self.pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            logger.info("✅ Model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def _preprocess_text(self, title: str, content: str) -> str:
        """Preprocess article text for classification"""
        text = f"{title or ''} {content or ''}".strip()
        
        # Limit text length to avoid token limits
        max_chars = 2000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
        
        return text
    
    def _map_to_category(self, text: str, finbert_labels: List[Dict]) -> Tuple[str, float]:
        """Map FinBERT output to predefined categories"""
        best_prediction = max(finbert_labels, key=lambda x: x['score'])
        finbert_confidence = best_prediction['score']
        
        text_lower = text.lower()
        
        # Calculate category scores based on keyword matching
        category_scores = {}
        for category, keywords in self.CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score / len(keywords)
        
        # Determine final category
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] >= 0.3:
                final_category = best_category[0]
                final_confidence = min(0.95, finbert_confidence + (best_category[1] * 0.2))
            else:
                final_category = 'GENERAL FINTECH'
                final_confidence = finbert_confidence * 0.8
        else:
            final_category = 'GENERAL FINTECH'
            final_confidence = finbert_confidence * 0.7
        
        relevance_score = min(100, max(0, final_confidence * 100))
        return final_category, relevance_score
    
    def classify_article(self, article: Article) -> Dict:
        """Classify a single article"""
        try:
            text = self._preprocess_text(article.title, article.content)
            
            if not text.strip():
                return {
                    'success': False,
                    'error': 'No content to classify',
                    'category': 'GENERAL FINTECH',
                    'relevance_score': 0
                }
            
            predictions = self.pipeline(text)
            category, relevance_score = self._map_to_category(text, predictions)
            
            return {
                'success': True,
                'category': category,
                'relevance_score': round(relevance_score, 2),
                'finbert_predictions': predictions,
                'text_length': len(text)
            }
            
        except Exception as e:
            logger.error(f"❌ Error classifying article {article.id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'category': 'GENERAL FINTECH',
                'relevance_score': 0
            }


class ArticleClassificationService:
    """Service for managing article classification workflow"""
    
    def __init__(self, batch_size: int = 8):
        """Initialize the classification service"""
        self.batch_size = batch_size
        self.classifier = None
        self.stats = {
            'total_processed': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'database_errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        if TRANSFORMERS_AVAILABLE:
            self.classifier = FinBERTClassifier(batch_size=batch_size)
        else:
            logger.error("❌ Cannot initialize classifier: transformers library not available")
    
    def get_unclassified_articles(self, db: Session, limit: Optional[int] = None) -> List[Article]:
        """Fetch articles that need classification"""
        try:
            query = db.query(Article).filter(
                (Article.primary_category.is_(None)) | 
                (Article.primary_category == '') |
                (Article.relevance_score.is_(None))
            )
            
            if limit:
                query = query.limit(limit)
            
            articles = query.all()
            logger.info(f"📊 Found {len(articles)} articles needing classification")
            return articles
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error fetching articles: {e}")
            return []
    
    def update_article_classification(self, db: Session, article: Article, result: Dict) -> bool:
        """Update article with classification results"""
        try:
            article.primary_category = result['category']
            article.relevance_score = int(result['relevance_score'])
            
            # Set confidence level based on relevance score
            if result['relevance_score'] >= 80:
                article.confidence_level = 'high'
            elif result['relevance_score'] >= 60:
                article.confidence_level = 'medium'
            elif result['relevance_score'] >= 40:
                article.confidence_level = 'low'
            else:
                article.confidence_level = 'very_low'
            
            db.commit()
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error updating article {article.id}: {e}")
            db.rollback()
            self.stats['database_errors'] += 1
            return False
    
    def process_articles(self, limit: Optional[int] = None) -> Dict:
        """Main processing function to classify articles"""
        if not SQLALCHEMY_AVAILABLE:
            logger.error("❌ Cannot process articles: database modules not available")
            return self.stats
        
        if not self.classifier:
            logger.error("❌ Cannot process articles: classifier not initialized")
            return self.stats
        
        self.stats['start_time'] = datetime.now()
        logger.info("🚀 Starting article classification process")
        
        db = get_db_session()
        
        try:
            articles = self.get_unclassified_articles(db, limit)
            
            if not articles:
                logger.info("✅ No articles need classification!")
                return self.stats
            
            # Process articles one by one for better error handling
            for i, article in enumerate(articles, 1):
                logger.info(f"📝 Processing article {i}/{len(articles)}: {article.title[:60]}...")
                
                result = self.classifier.classify_article(article)
                self.stats['total_processed'] += 1
                
                if result['success']:
                    if self.update_article_classification(db, article, result):
                        self.stats['successful_classifications'] += 1
                        logger.info(f"   ✅ Category: {result['category']}, Score: {result['relevance_score']}")
                    else:
                        self.stats['failed_classifications'] += 1
                        logger.error(f"   ❌ Database update failed")
                else:
                    self.stats['failed_classifications'] += 1
                    logger.error(f"   ❌ Classification failed: {result.get('error', 'Unknown error')}")
                
                time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Unexpected error during processing: {e}")
        
        finally:
            db.close()
            self.stats['end_time'] = datetime.now()
            self._log_final_stats()
        
        return self.stats
    
    def _log_final_stats(self):
        """Log final processing statistics"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info("📊 Classification Complete!")
        logger.info(f"⏱️  Duration: {duration}")
        logger.info(f"📈 Total processed: {self.stats['total_processed']}")
        logger.info(f"✅ Successful: {self.stats['successful_classifications']}")
        logger.info(f"❌ Failed: {self.stats['failed_classifications']}")
        logger.info(f"🗄️  Database errors: {self.stats['database_errors']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful_classifications'] / self.stats['total_processed']) * 100
            logger.info(f"📊 Success rate: {success_rate:.1f}%")


def main():
    """Main function to run the article classification script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Classify news articles using FinBERT')
    parser.add_argument('--limit', type=int, help='Maximum number of articles to process')
    parser.add_argument('--batch-size', type=int, default=8, help='Batch size for processing')
    
    args = parser.parse_args()
    
    logger.info("🤖 NewsPulse Article Classifier")
    logger.info("=" * 50)
    
    # Check dependencies
    if not TRANSFORMERS_AVAILABLE:
        logger.error("❌ Transformers library not available")
        logger.error("💡 Install with: pip install transformers torch")
        sys.exit(1)
    
    if not SQLALCHEMY_AVAILABLE:
        logger.error("❌ Database modules not available")
        logger.error("💡 Make sure you're running from the BackEnd directory")
        sys.exit(1)
    
    # Initialize and run classification service
    service = ArticleClassificationService(batch_size=args.batch_size)
    stats = service.process_articles(limit=args.limit)
    
    # Exit with appropriate code
    if stats['total_processed'] == 0:
        sys.exit(0)
    elif stats['successful_classifications'] == stats['total_processed']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()