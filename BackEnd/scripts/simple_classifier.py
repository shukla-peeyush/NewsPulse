#!/usr/bin/env python3
"""
Simple, robust classifier for testing
"""

import os
import sys
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "src"))

def classify_simple(title, summary):
    """Simple keyword-based classification"""
    text = f"{title} {summary}".lower()
    
    # Simple keyword matching
    if any(word in text for word in ['payment', 'transaction', 'gateway', 'merchant', 'pay']):
        return 'PAYMENTS', 85
    elif any(word in text for word in ['funding', 'investment', 'raised', 'venture', 'capital']):
        return 'FUNDING', 80
    elif any(word in text for word in ['regulation', 'law', 'policy', 'government', 'compliance']):
        return 'REGULATION', 75
    elif any(word in text for word in ['crypto', 'bitcoin', 'blockchain', 'cryptocurrency']):
        return 'CRYPTO', 90
    elif any(word in text for word in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
        return 'GENERAL FINTECH', 70
    else:
        return 'GENERAL FINTECH', 60

def main():
    print("🤖 Simple Article Classifier")
    print("=" * 40)
    
    try:
        from src.storage.database import get_db_session
        from src.storage.models_simple import Article
        
        db = get_db_session()
        
        # Get unclassified articles
        articles = db.query(Article).filter(
            (Article.primary_category.is_(None)) | 
            (Article.relevance_score.is_(None))
        ).limit(10).all()
        
        print(f"📊 Found {len(articles)} articles to classify")
        
        classified_count = 0
        for article in articles:
            try:
                # Simple classification
                category, score = classify_simple(article.title or '', article.summary or '')
                
                # Update article
                article.primary_category = category
                article.relevance_score = score
                article.confidence_level = 'medium' if score >= 70 else 'low'
                
                db.commit()
                classified_count += 1
                
                print(f"✅ {article.title[:50]}...")
                print(f"   Category: {category}, Score: {score}")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                db.rollback()
        
        db.close()
        print(f"\n🎉 Classified {classified_count} articles!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()