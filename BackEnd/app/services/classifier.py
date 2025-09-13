"""
Article Classification Service
"""

import logging
from typing import Dict, List, Optional, Tuple
import re
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ArticleClassifier:
    """Service for classifying articles by category and relevance"""
    
    def __init__(self):
        self.categories = {
            'fintech': {
                'keywords': [
                    'fintech', 'financial technology', 'digital payments', 'blockchain',
                    'cryptocurrency', 'bitcoin', 'ethereum', 'defi', 'neobank',
                    'digital banking', 'mobile payments', 'payment gateway', 'wallet',
                    'lending', 'insurtech', 'regtech', 'wealthtech', 'robo-advisor'
                ],
                'weight': 1.0
            },
            'payments': {
                'keywords': [
                    'payments', 'payment', 'transaction', 'merchant', 'pos', 'card',
                    'credit card', 'debit card', 'contactless', 'nfc', 'qr code',
                    'digital wallet', 'apple pay', 'google pay', 'paypal', 'stripe',
                    'square', 'visa', 'mastercard', 'amex', 'processing'
                ],
                'weight': 1.0
            },
            'banking': {
                'keywords': [
                    'banking', 'bank', 'financial services', 'retail banking',
                    'commercial banking', 'investment banking', 'central bank',
                    'federal reserve', 'interest rates', 'loans', 'mortgages',
                    'deposits', 'savings', 'checking account', 'atm'
                ],
                'weight': 0.8
            },
            'ecommerce': {
                'keywords': [
                    'ecommerce', 'e-commerce', 'online shopping', 'retail',
                    'marketplace', 'amazon', 'shopify', 'alibaba', 'ebay',
                    'online payments', 'checkout', 'cart abandonment',
                    'conversion rate', 'customer experience'
                ],
                'weight': 0.7
            },
            'technology': {
                'keywords': [
                    'artificial intelligence', 'machine learning', 'ai', 'ml',
                    'automation', 'api', 'cloud computing', 'saas', 'software',
                    'mobile app', 'cybersecurity', 'data analytics', 'big data'
                ],
                'weight': 0.6
            },
            'business': {
                'keywords': [
                    'startup', 'funding', 'investment', 'venture capital', 'ipo',
                    'merger', 'acquisition', 'partnership', 'revenue', 'growth',
                    'market share', 'competition', 'strategy', 'innovation'
                ],
                'weight': 0.5
            }
        }
    
    def classify_article(self, title: str, summary: str = "", content: str = "") -> Dict:
        """
        Classify article and calculate relevance score
        
        Args:
            title: Article title
            summary: Article summary
            content: Article content
            
        Returns:
            Classification results with category and scores
        """
        # Combine all text for analysis
        text_to_analyze = f"{title} {summary} {content}".lower()
        
        # Calculate scores for each category
        category_scores = {}
        for category, config in self.categories.items():
            score = self._calculate_category_score(text_to_analyze, config)
            if score > 0:
                category_scores[category] = score
        
        # Determine primary category and confidence
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[primary_category]
            
            # Calculate overall relevance score (1-100)
            relevance_score = min(100, int(max_score * 10))
            
            # Determine confidence level
            confidence_level = self._determine_confidence(max_score, category_scores)
            
        else:
            primary_category = None
            relevance_score = 0
            confidence_level = "LOW"
        
        return {
            'primary_category': primary_category,
            'relevance_score': relevance_score,
            'confidence_level': confidence_level,
            'category_scores': category_scores
        }
    
    def _calculate_category_score(self, text: str, category_config: Dict) -> float:
        """
        Calculate score for a specific category
        
        Args:
            text: Text to analyze
            category_config: Category configuration with keywords and weight
            
        Returns:
            Category score
        """
        keywords = category_config['keywords']
        weight = category_config['weight']
        
        score = 0.0
        word_count = len(text.split())
        
        for keyword in keywords:
            # Count keyword occurrences (case insensitive)
            keyword_lower = keyword.lower()
            
            # Exact phrase matching
            phrase_count = text.count(keyword_lower)
            
            # Word boundary matching for single words
            if ' ' not in keyword_lower:
                word_pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                word_matches = len(re.findall(word_pattern, text))
                phrase_count = max(phrase_count, word_matches)
            
            if phrase_count > 0:
                # Calculate keyword score based on frequency and text length
                keyword_score = (phrase_count / max(word_count, 1)) * 100
                score += keyword_score
        
        return score * weight
    
    def _determine_confidence(self, max_score: float, category_scores: Dict) -> str:
        """
        Determine confidence level based on scores
        
        Args:
            max_score: Highest category score
            category_scores: All category scores
            
        Returns:
            Confidence level string
        """
        if max_score >= 5.0:
            return "HIGH"
        elif max_score >= 2.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def classify_batch(self, articles: List) -> List[Dict]:
        """
        Classify multiple articles
        
        Args:
            articles: List of article objects or dictionaries
            
        Returns:
            List of classification results
        """
        results = []
        
        for article in articles:
            # Handle both model objects and dictionaries
            if hasattr(article, 'title'):
                title = article.title or ""
                summary = article.summary or ""
                content = article.content or ""
            else:
                title = article.get('title', "")
                summary = article.get('summary', "")
                content = article.get('content', "")
            
            classification = self.classify_article(title, summary, content)
            results.append(classification)
        
        return results
    
    def update_article_classification(self, article, classification: Dict) -> bool:
        """
        Update article with classification results
        
        Args:
            article: Article model instance
            classification: Classification results
            
        Returns:
            True if update successful
        """
        try:
            article.primary_category = classification['primary_category']
            article.relevance_score = classification['relevance_score']
            article.confidence_level = classification['confidence_level']
            
            # Mark as processed if it wasn't already
            if article.processed == 'pending':
                article.processed = 'processed'
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating article classification: {e}")
            return False
    
    def get_category_stats(self, db: Session) -> Dict:
        """
        Get statistics about article categories
        
        Args:
            db: Database session
            
        Returns:
            Category statistics
        """
        from ..models import Article
        
        try:
            # Get category counts
            category_counts = {}
            for category in self.categories.keys():
                count = db.query(Article).filter(
                    Article.primary_category == category
                ).count()
                category_counts[category] = count
            
            # Get total articles
            total_articles = db.query(Article).count()
            
            # Get unclassified articles
            unclassified = db.query(Article).filter(
                Article.primary_category.is_(None)
            ).count()
            
            return {
                'category_counts': category_counts,
                'total_articles': total_articles,
                'unclassified': unclassified,
                'classified': total_articles - unclassified
            }
            
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return {}