"""
Test Configuration
"""

import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.database import get_db
from app.models import Base


# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_article_data():
    """Sample article data for testing"""
    return {
        "title": "Test Fintech Article",
        "link": "https://example.com/test-article",
        "summary": "This is a test article about fintech and digital payments",
        "content": "Full content about fintech innovations and payment technologies",
        "source_id": 1,
        "content_hash": "test_hash_123"
    }


@pytest.fixture
def sample_source_data():
    """Sample news source data for testing"""
    return {
        "name": "Test News Source",
        "website_url": "https://example.com",
        "rss_url": "https://example.com/rss",
        "region": "Test Region",
        "priority": 1
    }