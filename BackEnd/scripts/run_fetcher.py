"""
Manual News Fetching Script
"""

import sys
import os
import asyncio

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.services import fetch_news_manually
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run news fetching manually"""
    
    logger.info("Starting manual news fetching...")
    
    db = SessionLocal()
    try:
        result = await fetch_news_manually(db)
        
        logger.info("Fetching completed!")
        logger.info(f"Results: {result}")
        
        print("\n" + "="*50)
        print("FETCHING RESULTS")
        print("="*50)
        print(f"Total articles fetched: {result['total_articles']}")
        print(f"Sources processed: {result['sources_processed']}/{result['total_sources']}")
        
        if result['errors']:
            print(f"Errors encountered: {len(result['errors'])}")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error during fetching: {e}")
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())