"""
Database Session Utilities
"""

from sqlalchemy.orm import Session
from .connection import SessionLocal
from typing import Generator
import logging

logger = logging.getLogger(__name__)


def get_session() -> Generator[Session, None, None]:
    """
    Get database session with proper error handling
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


class DatabaseManager:
    """
    Database manager for handling transactions
    """
    
    def __init__(self):
        self.session = None
    
    def __enter__(self):
        self.session = SessionLocal()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()