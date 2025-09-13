"""
Database Migration Script
Add missing columns to existing database
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Add missing columns to existing database"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'newspulse.db')
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return False
    
    logger.info(f"Migrating database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(articles)")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"Current columns: {columns}")
        
        # Add missing columns
        migrations = []
        
        if 'processed' not in columns:
            migrations.append("ALTER TABLE articles ADD COLUMN processed VARCHAR(20)")
        
        if 'created_at' not in columns:
            migrations.append("ALTER TABLE articles ADD COLUMN created_at DATETIME")
        
        if 'updated_at' not in columns:
            migrations.append("ALTER TABLE articles ADD COLUMN updated_at DATETIME")
        
        # Execute migrations
        for migration in migrations:
            logger.info(f"Executing: {migration}")
            cursor.execute(migration)
        
        # Update existing records with current timestamp if needed
        if migrations:
            current_time = datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE articles 
                SET created_at = ?, updated_at = ? 
                WHERE created_at IS NULL OR updated_at IS NULL
            """, (current_time, current_time))
        
        # Check news_sources table
        cursor.execute("PRAGMA table_info(news_sources)")
        source_columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"News sources columns: {source_columns}")
        
        # Add missing columns to news_sources
        source_migrations = []
        
        if 'created_at' not in source_columns:
            source_migrations.append("ALTER TABLE news_sources ADD COLUMN created_at DATETIME")
        
        if 'updated_at' not in source_columns:
            source_migrations.append("ALTER TABLE news_sources ADD COLUMN updated_at DATETIME")
        
        # Execute source migrations
        for migration in source_migrations:
            logger.info(f"Executing: {migration}")
            cursor.execute(migration)
        
        # Update existing source records
        if source_migrations:
            cursor.execute("""
                UPDATE news_sources 
                SET created_at = ?, updated_at = ? 
                WHERE created_at IS NULL OR updated_at IS NULL
            """, (current_time, current_time))
        
        conn.commit()
        logger.info("Database migration completed successfully!")
        
        # Show final schema
        cursor.execute("PRAGMA table_info(articles)")
        final_columns = cursor.fetchall()
        logger.info("Final articles table schema:")
        for col in final_columns:
            logger.info(f"  {col[1]} {col[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    migrate_database()