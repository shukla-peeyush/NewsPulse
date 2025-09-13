"""
Database initialization script
"""

import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.storage.database import init_database, test_connection

def main():
    """Initialize the database with tables and default data"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Initializing database...")
        
        # Test connection first
        if not test_connection():
            logger.error("Database connection failed")
            return False
        
        # Initialize database
        init_database()
        logger.info("Database initialization completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)