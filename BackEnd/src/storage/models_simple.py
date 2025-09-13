"""
Simplified SQLAlchemy models matching actual database schema
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class NewsSource(Base):
    """Model for news sources (RSS feeds, websites) - simplified"""
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


class Article(Base):
    """Model for news articles - simplified to match actual database"""
    __tablename__ = "articles"
    
    # Only include columns that actually exist in the database
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey('news_sources.id'))
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False)  # This is the actual column name
    summary = Column(Text)
    content = Column(Text)  # This is the actual column name (not full_text)
    published_date = Column(DateTime)
    content_hash = Column(String(64), unique=True, nullable=False)
    relevance_score = Column(Integer)  # This is INTEGER in the actual DB
    primary_category = Column(String(8))  # VARCHAR(8) in actual DB
    confidence_level = Column(String(6))  # VARCHAR(6) in actual DB
    
    # Relationships
    source = relationship("NewsSource", back_populates="articles")


class ScrapingSession(Base):
    """Model for tracking scraping sessions - simplified"""
    __tablename__ = "scraping_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(Integer, ForeignKey('news_sources.id'))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(20), default='running')
    articles_found = Column(Integer, default=0)
    articles_processed = Column(Integer, default=0)
    articles_relevant = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Relationship
    source = relationship("NewsSource")