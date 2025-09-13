"""
Keyword-based classifier for article relevance scoring
"""

import logging
import re
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..storage.models import Article
from ..storage.database import get_db_session

logger = logging.getLogger(__name__)


class KeywordClassifier:
    """Fast keyword-based classifier for article relevance"""
    
    def __init__(self):
        self.payment_keywords = self._load_payment_keywords()
        self.fintech_keywords = self._load_fintech_keywords()
        self.business_keywords = self._load_business_keywords()
        self.negative_keywords = self._load_negative_keywords()
        
        # Category weights
        self.category_weights = {
            'PAYMENTS': 1.0,
            'FINTECH': 0.9,
            'FUNDING': 0.8,
            'BUSINESS': 0.7,
            'TECHNOLOGY': 0.6
        }
    
    def _load_payment_keywords(self) -> Dict[str, float]:
        """Load payment-related keywords with weights"""
        return {
            # Core payment terms
            'payment': 3.0,
            'payments': 3.0,
            'pay': 2.0,
            'transaction': 2.5,
            'transactions': 2.5,
            'merchant': 3.0,
            'merchants': 3.0,
            'checkout': 2.5,
            'gateway': 2.5,
            'processor': 2.5,
            'processing': 2.0,
            
            # Payment methods
            'credit card': 2.5,
            'debit card': 2.5,
            'digital wallet': 3.0,
            'mobile payment': 3.0,
            'contactless': 2.5,
            'nfc': 2.0,
            'qr code': 2.0,
            'apple pay': 2.5,
            'google pay': 2.5,
            'paypal': 2.0,
            'stripe': 2.5,
            'square': 2.0,
            
            # Payment infrastructure
            'pos': 2.5,
            'point of sale': 2.5,
            'terminal': 2.0,
            'acquirer': 2.5,
            'issuer': 2.0,
            'interchange': 2.5,
            'settlement': 2.0,
            'clearing': 2.0,
            
            # Compliance and security
            'pci dss': 3.0,
            'pci compliance': 3.0,
            'fraud': 2.5,
            'chargeback': 2.5,
            'authentication': 2.0,
            '3d secure': 2.5,
            'tokenization': 2.5,
            'encryption': 2.0
        }
    
    def _load_fintech_keywords(self) -> Dict[str, float]:
        """Load fintech-related keywords with weights"""
        return {
            'fintech': 3.0,
            'financial technology': 3.0,
            'neobank': 2.5,
            'challenger bank': 2.5,
            'digital bank': 2.5,
            'open banking': 2.5,
            'api banking': 2.5,
            'regtech': 2.0,
            'insurtech': 2.0,
            'wealthtech': 2.0,
            'robo advisor': 2.0,
            'cryptocurrency': 2.0,
            'blockchain': 2.0,
            'bitcoin': 1.5,
            'ethereum': 1.5,
            'defi': 2.0,
            'cbdc': 2.5,
            'stablecoin': 2.0,
            'lending': 2.0,
            'p2p lending': 2.5,
            'crowdfunding': 1.5,
            'remittance': 2.5,
            'cross border': 2.0,
            'forex': 1.5,
            'trading': 1.5
        }
    
    def _load_business_keywords(self) -> Dict[str, float]:
        """Load business-related keywords with weights"""
        return {
            'startup': 2.0,
            'funding': 2.5,
            'investment': 2.0,
            'venture capital': 2.5,
            'series a': 2.5,
            'series b': 2.5,
            'ipo': 2.0,
            'acquisition': 2.0,
            'merger': 2.0,
            'partnership': 1.5,
            'collaboration': 1.5,
            'expansion': 1.5,
            'launch': 1.5,
            'revenue': 1.5,
            'growth': 1.5,
            'market': 1.0,
            'industry': 1.0,
            'business': 1.0,
            'company': 1.0,
            'enterprise': 1.5,
            'b2b': 1.5,
            'b2c': 1.5,
            'saas': 1.5,
            'platform': 1.5,
            'solution': 1.0,
            'service': 1.0
        }
    
    def _load_negative_keywords(self) -> List[str]:
        """Load keywords that reduce relevance"""
        return [
            'sports', 'football', 'soccer', 'basketball', 'tennis',
            'entertainment', 'celebrity', 'movie', 'film', 'music',
            'weather', 'traffic', 'accident', 'crime', 'politics',
            'election', 'government', 'military', 'war', 'conflict',
            'health', 'medical', 'hospital', 'doctor', 'patient',
            'education', 'school', 'university', 'student', 'teacher',
            'travel', 'tourism', 'hotel', 'restaurant', 'food',
            'fashion', 'beauty', 'lifestyle', 'personal'
        ]
    
    def classify_article(self, article: Article) -> Dict[str, Any]:
        """
        Classify an article and assign relevance score and category
        
        Args:
            article: Article object to classify
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Combine title and content for analysis
            text_to_analyze = ""
            if article.title:
                text_to_analyze += article.title + " "
            if article.summary:
                text_to_analyze += article.summary + " "
            if hasattr(article, 'full_text') and article.full_text:
                # Use first 500 words of full text to avoid processing very long articles
                words = article.full_text.split()[:500]
                text_to_analyze += " ".join(words)
            
            if not text_to_analyze.strip():
                return self._default_classification("No content to analyze")
            
            # Convert to lowercase for analysis
            text_lower = text_to_analyze.lower()
            
            # Calculate scores for each category
            payment_score = self._calculate_keyword_score(text_lower, self.payment_keywords)
            fintech_score = self._calculate_keyword_score(text_lower, self.fintech_keywords)
            business_score = self._calculate_keyword_score(text_lower, self.business_keywords)
            
            # Calculate negative score
            negative_score = self._calculate_negative_score(text_lower)
            
            # Determine primary category and score
            category_scores = {
                'PAYMENTS': payment_score,
                'FINTECH': fintech_score,
                'FUNDING': business_score * 0.8,  # Business keywords with funding focus
                'BUSINESS': business_score * 0.6,
                'TECHNOLOGY': (fintech_score + payment_score) * 0.3
            }
            
            # Find primary category
            primary_category = max(category_scores.items(), key=lambda x: x[1])
            
            # Calculate overall relevance score (0-100)
            base_score = primary_category[1]
            
            # Apply negative keyword penalty
            relevance_score = max(0, base_score - negative_score)
            
            # Normalize to 0-100 scale
            relevance_score = min(100, relevance_score * 10)
            
            # Determine confidence level
            confidence_level = self._determine_confidence(relevance_score, base_score)
            
            # Create secondary categories (categories with score > 1.0)
            secondary_categories = {
                cat: score for cat, score in category_scores.items() 
                if score > 1.0 and cat != primary_category[0]
            }
            
            # Determine geographic tags from content
            geographic_tags = self._extract_geographic_tags(text_lower)
            
            # Determine industry segments
            industry_segments = self._extract_industry_segments(text_lower)
            
            return {
                'relevance_score': round(relevance_score, 2),
                'primary_category': primary_category[0] if primary_category[1] > 0.5 else None,
                'secondary_categories': secondary_categories,
                'confidence_level': confidence_level,
                'geographic_tags': geographic_tags,
                'industry_segments': industry_segments,
                'classification_method': 'keyword_based',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error classifying article {article.id}: {str(e)}")
            return self._default_classification(f"Classification error: {str(e)}")
    
    def _calculate_keyword_score(self, text: str, keywords: Dict[str, float]) -> float:
        """Calculate score based on keyword matches"""
        score = 0.0
        
        for keyword, weight in keywords.items():
            # Count occurrences (case insensitive)
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
            if count > 0:
                # Diminishing returns for multiple occurrences
                keyword_score = weight * (1 + 0.5 * (count - 1))
                score += keyword_score
        
        return score
    
    def _calculate_negative_score(self, text: str) -> float:
        """Calculate penalty score for negative keywords"""
        score = 0.0
        
        for keyword in self.negative_keywords:
            count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
            if count > 0:
                score += 0.5 * count  # Penalty for each occurrence
        
        return score
    
    def _determine_confidence(self, relevance_score: float, base_score: float) -> str:
        """Determine confidence level based on scores"""
        if base_score >= 5.0 and relevance_score >= 70:
            return 'high'
        elif base_score >= 2.0 and relevance_score >= 40:
            return 'medium'
        elif relevance_score >= 20:
            return 'low'
        else:
            return 'very_low'
    
    def _extract_geographic_tags(self, text: str) -> Dict[str, List[str]]:
        """Extract geographic information from text"""
        regions = {
            'Southeast Asia': ['singapore', 'malaysia', 'thailand', 'indonesia', 'philippines', 'vietnam'],
            'Middle East': ['uae', 'dubai', 'saudi arabia', 'qatar', 'kuwait', 'bahrain', 'oman'],
            'Asia Pacific': ['china', 'japan', 'south korea', 'india', 'australia', 'hong kong'],
            'Europe': ['uk', 'germany', 'france', 'netherlands', 'sweden', 'switzerland'],
            'North America': ['usa', 'united states', 'canada', 'mexico']
        }
        
        found_regions = {}
        for region, countries in regions.items():
            found_countries = []
            for country in countries:
                if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
                    found_countries.append(country)
            
            if found_countries:
                found_regions[region] = found_countries
        
        return found_regions
    
    def _extract_industry_segments(self, text: str) -> List[str]:
        """Extract industry segments from text"""
        segments = {
            'E-commerce': ['ecommerce', 'e-commerce', 'online shopping', 'marketplace'],
            'Banking': ['bank', 'banking', 'financial institution', 'credit union'],
            'Insurance': ['insurance', 'insurtech', 'policy', 'claims'],
            'Investment': ['investment', 'trading', 'wealth management', 'asset management'],
            'Lending': ['lending', 'loan', 'credit', 'mortgage'],
            'Remittance': ['remittance', 'money transfer', 'cross border'],
            'Cryptocurrency': ['crypto', 'bitcoin', 'blockchain', 'digital currency'],
            'Retail': ['retail', 'pos', 'point of sale', 'merchant'],
            'Healthcare': ['healthcare', 'health', 'medical', 'telemedicine'],
            'Education': ['education', 'edtech', 'learning', 'training']
        }
        
        found_segments = []
        for segment, keywords in segments.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
                    found_segments.append(segment)
                    break
        
        return list(set(found_segments))  # Remove duplicates
    
    def _default_classification(self, error_message: str = "") -> Dict[str, Any]:
        """Return default classification for failed cases"""
        return {
            'relevance_score': 0.0,
            'primary_category': None,
            'secondary_categories': {},
            'confidence_level': 'very_low',
            'geographic_tags': {},
            'industry_segments': [],
            'classification_method': 'keyword_based_failed',
            'success': False,
            'error': error_message
        }


def main():
    """Main function for running classifier standalone"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test classifier
    classifier = KeywordClassifier()
    print("Keyword classifier initialized successfully")


if __name__ == "__main__":
    main()