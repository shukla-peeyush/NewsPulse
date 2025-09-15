#!/usr/bin/env python3
"""
Add working RSS sources that don't have SSL issues
"""

import os
import sys
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "src"))

def main():
    print("📰 Adding Working RSS Sources")
    print("=" * 40)
    
    try:
        from src.storage.database import get_db_session
        from src.storage.models_simple import NewsSource
        from datetime import datetime
        
        db = get_db_session()
        
        # Working RSS sources without SSL issues
        working_sources = [
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
                "name": "VentureBeat",
                "website_url": "https://venturebeat.com",
                "rss_url": "https://venturebeat.com/feed/",
                "region": "Global", 
                "language": "en",
                "priority": 1,
                "enabled": True
            },
            {
                "name": "Coindesk",
                "website_url": "https://www.coindesk.com",
                "rss_url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "region": "Global",
                "language": "en", 
                "priority": 1,
                "enabled": True
            },
            {
                "name": "Reuters Tech",
                "website_url": "https://www.reuters.com",
                "rss_url": "https://www.reuters.com/technology/feed/",
                "region": "Global",
                "language": "en",
                "priority": 2,
                "enabled": True
            }
        ]
        
        # Disable old problematic sources
        old_sources = db.query(NewsSource).all()
        for source in old_sources:
            source.enabled = False
            print(f"🔇 Disabled: {source.name}")
        
        # Add new working sources
        added_count = 0
        for source_data in working_sources:
            existing = db.query(NewsSource).filter_by(name=source_data["name"]).first()
            if not existing:
                source = NewsSource(**source_data)
                db.add(source)
                added_count += 1
                print(f"✅ Added: {source_data['name']}")
            else:
                existing.enabled = True
                existing.rss_url = source_data["rss_url"]
                print(f"🔄 Updated: {source_data['name']}")
        
        db.commit()
        db.close()
        
        print(f"\n✅ Added/updated {len(working_sources)} working sources!")
        print("🎯 Now run: python3 scripts/run_fetcher.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()