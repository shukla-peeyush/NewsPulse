"""
Main entry point for RSS fetching
"""

import asyncio
import logging
from ..storage.database import get_db, init_database
from .rss import process_all_feeds

def main():
    """Main function for RSS fetcher"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting RSS fetcher...")
    
    try:
        # Initialize database
        init_database()
        
        # Run RSS processing
        db_session = next(get_db())
        try:
            results = asyncio.run(process_all_feeds(db_session))
            logger.info(f"RSS fetching completed: {results}")
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"RSS fetcher failed: {e}")
        raise

if __name__ == "__main__":
    main()