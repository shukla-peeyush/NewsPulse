#!/usr/bin/env python3
"""
Cross-platform ML Classifier Script
Classifies articles using ML models (FinBERT + custom models)
"""

import os
import sys
import platform
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

def main():
    """Main classifier function"""
    print("🤖 NewsPulse ML Classifier")
    print(f"🖥️  Platform: {platform.system()}")
    print("-" * 40)
    
    try:
        # Import after path setup
        from src.classifier.ml_classifier import MLClassifier
        from src.storage.database import get_db_session
        from src.storage.models_simple import Article
        
        print("🧠 Initializing ML Classifier...")
        classifier = MLClassifier()
        
        if not classifier.model_loaded:
            print("⚠️  ML models not available. Using fallback classification.")
            print("💡 To use ML classification, install: pip install torch transformers scikit-learn")
        
        print("📊 Getting unclassified articles...")
        db = get_db_session()
        
        # Get articles that need classification
        unclassified = db.query(Article).filter(
            (Article.relevance_score == None) | 
            (Article.primary_category == None)
        ).limit(100).all()
        
        if not unclassified:
            print("✅ No articles need classification!")
            return
        
        print(f"🔍 Found {len(unclassified)} articles to classify...")
        
        classified_count = 0
        for article in unclassified:
            try:
                print(f"📝 Classifying: {article.title[:60]}...")
                
                # Classify the article
                result = classifier.classify_article(article)
                
                if result.get('success', False):
                    # Update article with classification results
                    article.relevance_score = int(result.get('relevance_score', 0))
                    article.primary_category = result.get('primary_category')
                    article.confidence_level = result.get('confidence_level', 'low')
                    
                    db.commit()
                    classified_count += 1
                    
                    print(f"   ✅ Category: {article.primary_category}, Score: {article.relevance_score}")
                else:
                    print(f"   ⚠️  Classification failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Error classifying article: {e}")
                db.rollback()
                continue
        
        db.close()
        
        print(f"\n✅ Classification Complete!")
        print(f"📈 Successfully classified {classified_count}/{len(unclassified)} articles")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the BackEnd directory")
        print("💡 And that all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()