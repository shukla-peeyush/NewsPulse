"""
Script to run keyword-based classifier
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.classifier.processor import process_unclassified_articles

async def main():
    """Main function for classifier"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting keyword-based classifier...")
    
    try:
        # Process unclassified articles
        stats = await process_unclassified_articles(batch_size=100)
        logger.info(f"Classification completed: {stats}")
        
    except Exception as e:
        logger.error(f"Classifier failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())