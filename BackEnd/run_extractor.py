"""
Script to run content extractor
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.extractor.content import process_unextracted_articles

async def main():
    """Main function for content extractor"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting content extractor...")
    
    try:
        # Process unextracted articles
        stats = await process_unextracted_articles(batch_size=20, use_playwright=False)
        logger.info(f"Content extraction completed: {stats}")
        
    except Exception as e:
        logger.error(f"Content extractor failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())