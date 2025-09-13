"""
Database Initialization Script
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import create_tables, test_connection
from app.models import NewsSource
from app.database import SessionLocal
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with tables and default data"""
    
    logger.info("Testing database connection...")
    if not test_connection():
        logger.error("Database connection failed!")
        return False
    
    logger.info("Creating database tables...")
    if not create_tables():
        logger.error("Failed to create tables!")
        return False
    
    logger.info("Adding default news sources...")
    add_default_sources()
    
    logger.info("Database initialization completed successfully!")
    return True


def add_default_sources():
    """Add default news sources from configuration"""
    
    db = SessionLocal()
    try:
        # Default sources with RSS feeds
        default_sources = [
            {
                "name": "E27",
                "website_url": "https://e27.co",
                "rss_url": "https://e27.co/feed/",
                "region": "Asia",
                "priority": 1
            },
            {
                "name": "Tech in Asia",
                "website_url": "https://www.techinasia.com",
                "rss_url": "https://www.techinasia.com/rss",
                "region": "Asia",
                "priority": 1
            },
            {
                "name": "Fintech News Asia",
                "website_url": "https://fintechnews.asia",
                "rss_url": "https://fintechnews.asia/feed/",
                "region": "Asia",
                "priority": 2
            },
            {
                "name": "The National News",
                "website_url": "https://www.thenationalnews.com",
                "rss_url": "https://www.thenationalnews.com/rss.xml",
                "region": "Middle East",
                "priority": 2
            },
            {
                "name": "Arabian Business",
                "website_url": "https://www.arabianbusiness.com",
                "rss_url": "https://www.arabianbusiness.com/rss.xml",
                "region": "Middle East",
                "priority": 2
            }
        ]
        
        for source_data in default_sources:
            # Check if source already exists
            existing = db.query(NewsSource).filter(
                NewsSource.name == source_data["name"]
            ).first()
            
            if not existing:
                source = NewsSource(**source_data)
                db.add(source)
                logger.info(f"Added source: {source_data['name']}")
            else:
                logger.info(f"Source already exists: {source_data['name']}")
        
        db.commit()
        logger.info("Default sources added successfully")
        
    except Exception as e:
        logger.error(f"Error adding default sources: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()