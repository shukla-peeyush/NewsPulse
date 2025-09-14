#!/usr/bin/env python3
"""
Cross-platform Database Initialization Script
Sets up the database with tables and sample data
"""

import os
import sys
import platform
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir / "src"))

def main():
    """Main database initialization function"""
    print("🗄️  NewsPulse Database Initializer")
    print(f"🖥️  Platform: {platform.system()}")
    print("-" * 40)
    
    try:
        # Import after path setup
        from src.storage.database import engine, test_connection
        from src.storage.models_simple import Base, NewsSource
        from src.storage.database import get_db_session
        from datetime import datetime
        
        print("🔗 Testing database connection...")
        if not test_connection():
            print("❌ Database connection failed!")
            sys.exit(1)
        
        print("✅ Database connection successful!")
        
        print("📋 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created!")
        
        # Add sample news sources
        print("📰 Adding sample news sources...")
        db = get_db_session()
        
        sample_sources = [
            {
                "name": "TechCrunch",
                "website_url": "https://techcrunch.com",
                "rss_url": "https://techcrunch.com/feed/",
                "region": "Global",
                "language": "en",
                "priority": 1,
                "enabled": True
            },
            {
                "name": "Fintech News",
                "website_url": "https://fintechnews.asia",
                "rss_url": "https://fintechnews.asia/feed/",
                "region": "Asia",
                "language": "en",
                "priority": 1,
                "enabled": True
            },
            {
                "name": "PaymentsSource",
                "website_url": "https://www.paymentssource.com",
                "rss_url": "https://www.paymentssource.com/feed",
                "region": "Global",
                "language": "en",
                "priority": 2,
                "enabled": True
            },
            {
                "name": "The Block",
                "website_url": "https://www.theblock.co",
                "rss_url": "https://www.theblock.co/rss.xml",
                "region": "Global",
                "language": "en",
                "priority": 2,
                "enabled": True
            }
        ]
        
        added_count = 0
        for source_data in sample_sources:
            # Check if source already exists
            existing = db.query(NewsSource).filter_by(name=source_data["name"]).first()
            if not existing:
                source = NewsSource(**source_data)
                db.add(source)
                added_count += 1
        
        db.commit()
        db.close()
        
        print(f"✅ Added {added_count} new news sources!")
        
        print("\n🎉 Database initialization complete!")
        print("\n📋 Next steps:")
        print("   1. Run the server: python run_server.py")
        print("   2. Fetch articles: python scripts/run_fetcher.py")
        print("   3. Classify articles: python scripts/run_classifier.py")
        print("   4. Visit API docs: http://localhost:8000/docs")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the BackEnd directory")
        print("💡 And that all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()