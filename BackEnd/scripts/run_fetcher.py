#!/usr/bin/env python3
"""
Cross-platform RSS Fetcher Script
Fetches news articles from configured RSS sources
"""

import os
import sys
import asyncio
import platform
from pathlib import Path

# Add src to Python path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "src"))

def main():
    """Main fetcher function"""
    print("🔄 NewsPulse RSS Fetcher")
    print(f"🖥️  Platform: {platform.system()}")
    print("-" * 40)
    
    try:
        # Import after path setup
        from src.fetcher.rss import process_all_feeds
        from src.storage.database import init_database
        
        print("📊 Initializing database...")
        init_database()
        
        print("🔍 Starting RSS feed processing...")
        
        # Run the async fetcher
        stats = asyncio.run(process_all_feeds())
        
        print("\n✅ RSS Fetching Complete!")
        print(f"📈 Statistics:")
        print(f"   • Sources processed: {stats.get('total_sources', 0)}")
        print(f"   • Articles found: {stats.get('total_articles_found', 0)}")
        print(f"   • New articles: {stats.get('total_articles_new', 0)}")
        print(f"   • Duplicates skipped: {stats.get('total_articles_duplicate', 0)}")
        
        if stats.get('total_errors', 0) > 0:
            print(f"   ⚠️  Errors: {stats.get('total_errors', 0)}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running from the BackEnd directory")
        print("💡 And that all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during RSS fetching: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()