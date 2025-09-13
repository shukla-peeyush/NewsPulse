"""
ML-based classifier using transformers for more accurate article classification
"""

import logging
import os
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session

from ..storage.models import Article
from ..storage.database import get_db_session

logger = logging.getLogger(__name__)

# Try to import transformers and related libraries
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Transformers or sklearn not available: {e}")
    TRANSFORMERS_AVAILABLE = False


class MLClassifier:
    """ML-based classifier using transformers and traditional ML models"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert", use_local_model: bool = True):
        self.model_name = model_name
        self.use_local_model = use_local_model
        self.finbert_pipeline = None
        self.local_model = None
        self.vectorizer = None
        self.model_loaded = False
        
        if TRANSFORMERS_AVAILABLE:
            self._initialize_models()
        else:
            logger.error("Transformers not available. ML classification will not work.")
    
    def _initialize_models(self):
        """Initialize ML models"""
        try:
            # Initialize FinBERT for financial sentiment/classification
            logger.info(f"Loading FinBERT model: {self.model_name}")
            self.finbert_pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Try to load local trained model if available
            if self.use_local_model:
                self._load_local_model()
            
            self.model_loaded = True
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
            self.model_loaded = False
    
    def _load_local_model(self):
        """Load locally trained model if available"""
        try:
            model_path = "models/local_classifier.pkl"
            vectorizer_path = "models/vectorizer.pkl"
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                with open(model_path, 'rb') as f:
                    self.local_model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Local trained model loaded successfully")
            else:
                logger.info("No local trained model found, will use FinBERT only")
                
        except Exception as e:
            logger.warning(f"Error loading local model: {e}")
            self.local_model = None
            self.vectorizer = None
    
    def classify_with_finbert(self, text: str) -> Dict[str, Any]:
        """
        Classify text using FinBERT
        
        Args:
            text: Text to classify
            
        Returns:
            Classification results
        """
        if not self.finbert_pipeline:
            return {'success': False, 'error': 'FinBERT not available'}
        
        try:
            # Truncate text to avoid token limits
            max_length = 512
            words = text.split()
            if len(words) > max_length:
                text = ' '.join(words[:max_length])
            
            # Get FinBERT prediction
            result = self.finbert_pipeline(text)
            
            # Map FinBERT labels to our categories
            label_mapping = {
                'positive': 'FINTECH',
                'negative': 'BUSINESS',
                'neutral': 'TECHNOLOGY'
            }
            
            if result and len(result) > 0:
                prediction = result[0]
                mapped_category = label_mapping.get(prediction['label'].lower(), 'BUSINESS')
                confidence = prediction['score']
                
                # Convert confidence to relevance score
                relevance_score = min(100, confidence * 100)
                
                return {
                    'success': True,
                    'primary_category': mapped_category,
                    'relevance_score': relevance_score,
                    'confidence': confidence,
                    'raw_prediction': prediction,
                    'method': 'finbert'
                }
            else:
                return {'success': False, 'error': 'No prediction from FinBERT'}
                
        except Exception as e:
            logger.error(f"Error in FinBERT classification: {e}")
            return {'success': False, 'error': str(e)}
    
    def classify_with_local_model(self, text: str) -> Dict[str, Any]:
        """
        Classify text using local trained model
        
        Args:
            text: Text to classify
            
        Returns:
            Classification results
        """
        if not self.local_model or not self.vectorizer:
            return {'success': False, 'error': 'Local model not available'}
        
        try:
            # Vectorize text
            text_vector = self.vectorizer.transform([text])
            
            # Get prediction
            prediction = self.local_model.predict(text_vector)[0]
            probabilities = self.local_model.predict_proba(text_vector)[0]
            
            # Get confidence (max probability)
            confidence = max(probabilities)
            
            # Convert confidence to relevance score
            relevance_score = min(100, confidence * 100)
            
            return {
                'success': True,
                'primary_category': prediction,
                'relevance_score': relevance_score,
                'confidence': confidence,
                'probabilities': dict(zip(self.local_model.classes_, probabilities)),
                'method': 'local_model'
            }
            
        except Exception as e:
            logger.error(f"Error in local model classification: {e}")
            return {'success': False, 'error': str(e)}
    
    def classify_article(self, article: Article) -> Dict[str, Any]:
        """
        Classify an article using ML models
        
        Args:
            article: Article object to classify
            
        Returns:
            Dictionary with classification results
        """
        if not self.model_loaded:
            return self._fallback_classification("ML models not loaded")
        
        try:
            # Prepare text for classification
            text_to_analyze = ""
            if article.title:
                text_to_analyze += article.title + " "
            if article.summary:
                text_to_analyze += article.summary + " "
            if hasattr(article, 'full_text') and article.full_text:
                # Use first 300 words to avoid token limits
                words = article.full_text.split()[:300]
                text_to_analyze += " ".join(words)
            
            if not text_to_analyze.strip():
                return self._fallback_classification("No content to analyze")
            
            # Try FinBERT first
            finbert_result = self.classify_with_finbert(text_to_analyze)
            
            # Try local model if available
            local_result = self.classify_with_local_model(text_to_analyze)
            
            # Combine results or use best available
            if finbert_result['success'] and local_result['success']:
                # Use the result with higher confidence
                if finbert_result['confidence'] > local_result['confidence']:
                    primary_result = finbert_result
                    secondary_result = local_result
                else:
                    primary_result = local_result
                    secondary_result = finbert_result
                
                # Average the relevance scores
                combined_score = (primary_result['relevance_score'] + secondary_result['relevance_score']) / 2
                
                return {
                    'relevance_score': round(combined_score, 2),
                    'primary_category': primary_result['primary_category'],
                    'confidence_level': self._determine_confidence_level(combined_score),
                    'ml_confidence': primary_result['confidence'],
                    'secondary_categories': {secondary_result['primary_category']: secondary_result['relevance_score']},
                    'geographic_tags': {},  # Could be enhanced with NER
                    'industry_segments': self._extract_industry_segments(text_to_analyze),
                    'classification_method': 'ml_combined',
                    'model_details': {
                        'primary': primary_result['method'],
                        'secondary': secondary_result['method']
                    },
                    'success': True
                }
                
            elif finbert_result['success']:
                return {
                    'relevance_score': round(finbert_result['relevance_score'], 2),
                    'primary_category': finbert_result['primary_category'],
                    'confidence_level': self._determine_confidence_level(finbert_result['relevance_score']),
                    'ml_confidence': finbert_result['confidence'],
                    'secondary_categories': {},
                    'geographic_tags': {},
                    'industry_segments': self._extract_industry_segments(text_to_analyze),
                    'classification_method': 'ml_finbert',
                    'model_details': {'primary': 'finbert'},
                    'success': True
                }
                
            elif local_result['success']:
                return {
                    'relevance_score': round(local_result['relevance_score'], 2),
                    'primary_category': local_result['primary_category'],
                    'confidence_level': self._determine_confidence_level(local_result['relevance_score']),
                    'ml_confidence': local_result['confidence'],
                    'secondary_categories': {},
                    'geographic_tags': {},
                    'industry_segments': self._extract_industry_segments(text_to_analyze),
                    'classification_method': 'ml_local',
                    'model_details': {'primary': 'local_model'},
                    'success': True
                }
            else:
                return self._fallback_classification("All ML models failed")
                
        except Exception as e:
            logger.error(f"Error in ML classification for article {article.id}: {e}")
            return self._fallback_classification(f"ML classification error: {str(e)}")
    
    def _determine_confidence_level(self, relevance_score: float) -> str:
        """Determine confidence level based on relevance score"""
        if relevance_score >= 80:
            return 'high'
        elif relevance_score >= 60:
            return 'medium'
        elif relevance_score >= 40:
            return 'low'
        else:
            return 'very_low'
    
    def _extract_industry_segments(self, text: str) -> List[str]:
        """Extract industry segments using simple keyword matching"""
        segments = {
            'E-commerce': ['ecommerce', 'e-commerce', 'online shopping', 'marketplace'],
            'Banking': ['bank', 'banking', 'financial institution'],
            'Insurance': ['insurance', 'insurtech'],
            'Investment': ['investment', 'trading', 'wealth management'],
            'Lending': ['lending', 'loan', 'credit'],
            'Remittance': ['remittance', 'money transfer'],
            'Cryptocurrency': ['crypto', 'bitcoin', 'blockchain'],
            'Retail': ['retail', 'pos', 'point of sale']
        }
        
        found_segments = []
        text_lower = text.lower()
        
        for segment, keywords in segments.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_segments.append(segment)
                    break
        
        return list(set(found_segments))
    
    def _fallback_classification(self, error_message: str = "") -> Dict[str, Any]:
        """Return fallback classification for failed cases"""
        return {
            'relevance_score': 0.0,
            'primary_category': None,
            'confidence_level': 'very_low',
            'ml_confidence': 0.0,
            'secondary_categories': {},
            'geographic_tags': {},
            'industry_segments': [],
            'classification_method': 'ml_failed',
            'model_details': {},
            'success': False,
            'error': error_message
        }
    
    def train_local_model(self, training_data: List[Dict[str, Any]]) -> bool:
        """
        Train a local model using provided training data
        
        Args:
            training_data: List of dictionaries with 'text' and 'category' keys
            
        Returns:
            True if training was successful
        """
        if not TRANSFORMERS_AVAILABLE:
            logger.error("Cannot train model: required libraries not available")
            return False
        
        try:
            # Prepare training data
            texts = [item['text'] for item in training_data]
            labels = [item['category'] for item in training_data]
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Vectorize texts
            X = self.vectorizer.fit_transform(texts)
            
            # Train logistic regression model
            self.local_model = LogisticRegression(
                random_state=42,
                max_iter=1000
            )
            self.local_model.fit(X, labels)
            
            # Save models
            os.makedirs('models', exist_ok=True)
            
            with open('models/local_classifier.pkl', 'wb') as f:
                pickle.dump(self.local_model, f)
            
            with open('models/vectorizer.pkl', 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            logger.info(f"Local model trained successfully with {len(training_data)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training local model: {e}")
            return False


def main():
    """Main function for testing ML classifier"""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not TRANSFORMERS_AVAILABLE:
        print("Transformers not available. Please install with: pip install transformers torch scikit-learn")
        return
    
    # Test ML classifier
    classifier = MLClassifier()
    print(f"ML classifier initialized. Model loaded: {classifier.model_loaded}")


if __name__ == "__main__":
    main()