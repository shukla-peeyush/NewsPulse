"""
SQLAlchemy models for the NewsPulse application
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class NewsSource(Base):
    """Model for news sources (RSS feeds, websites)"""
    __tablename__ = "news_sources"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    website_url = Column(String(500), nullable=False)
    rss_url = Column(String(500))
    region = Column(String(50))
    language = Column(String(10), default='en')
    priority = Column(Integer, default=1)
    enabled = Column(Boolean, default=True)
    last_scraped = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to articles
    articles = relationship("Article", back_populates="source")
    scraping_sessions = relationship("ScrapingSession", back_populates="source")


class Article(Base):
    """Model for news articles"""
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey('news_sources.id', ondelete='SET NULL'))
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False)  # SHA-256 hash for deduplication
    published_date = Column(DateTime)
    scraped_date = Column(DateTime, default=datetime.utcnow)
    author = Column(String(200))
    word_count = Column(Integer)
    language = Column(String(10))
    
    # Full content storage
    summary = Column(Text)  # Generated summary
    full_text = Column(Text)  # Full article text
    full_text_s3_key = Column(String(1024))  # S3 key for full text storage
    
    # Classification results
    relevance_score = Column(Float)
    confidence_level = Column(String(20))
    primary_category = Column(String(50))
    secondary_categories = Column(JSON)
    geographic_tags = Column(JSON)
    industry_segments = Column(JSON)
    
    # Processing status
    processed = Column(Boolean, default=False)
    content_extracted = Column(Boolean, default=False)
    classified = Column(Boolean, default=False)
    processing_errors = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source = relationship("NewsSource", back_populates="articles")


class ScrapingSession(Base):
    """Model for tracking scraping sessions"""
    __tablename__ = "scraping_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey('news_sources.id', ondelete='CASCADE'))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(20), default='running')  # running, completed, failed
    articles_found = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    articles_relevant = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Relationship
    source = relationship("NewsSource", back_populates="scraping_sessions")


class AlertRule(Base):
    """Model for user-defined alert rules"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    keywords = Column(JSON)
    min_relevance_score = Column(Float)
    geographic_filters = Column(JSON)
    notification_channels = Column(JSON)  # {'email': ['...'], 'slack': '...'}
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def setup_database():
    """Initialize database with default news sources"""
    from .database import engine, get_db
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Add default news sources
    db = next(get_db())
    try:
        # Check if sources already exist
        existing_sources = db.query(NewsSource).count()
        if existing_sources == 0:
            default_sources = [
                NewsSource(
                    name="e27",
                    website_url="https://e27.co",
                    rss_url="https://e27.co/feed/",
                    region="Southeast Asia",
                    priority=1
                ),
                NewsSource(
                    name="Tech in Asia",
                    website_url="https://www.techinasia.com",
                    rss_url="https://www.techinasia.com/rss",
                    region="Asia",
                    priority=1
                ),
                NewsSource(
                    name="Fintech News Asia",
                    website_url="https://fintechnews.asia",
                    rss_url="https://fintechnews.asia/feed/",
                    region="Asia",
                    priority=2
                ),
                NewsSource(
                    name="The National UAE",
                    website_url="https://www.thenationalnews.com",
                    rss_url="https://www.thenationalnews.com/rss.xml",
                    region="Middle East",
                    priority=2
                ),
                NewsSource(
                    name="Arabian Business",
                    website_url="https://www.arabianbusiness.com",
                    rss_url="https://www.arabianbusiness.com/rss.xml",
                    region="Middle East",
                    priority=2
                )
            ]
            
            for source in default_sources:
                db.add(source)
            
            db.commit()
            print(f"Added {len(default_sources)} default news sources")
        else:
            print(f"Database already has {existing_sources} news sources")
            
    except Exception as e:
        db.rollback()
        print(f"Error setting up database: {e}")
        raise
    finally:
        db.close()