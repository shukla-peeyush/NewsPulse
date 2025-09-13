"""
SQLAlchemy models that exactly match the actual database schema
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class NewsSource(Base):
    """Model for news sources - EXACT match to database schema"""
    __tablename__ = "news_sources"
    
    # Only columns that actually exist in the database
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    rss_url = Column(String(500), nullable=False)
    region = Column(String(14), nullable=False)
    enabled = Column(Boolean, nullable=False)
    
    # Relationship to articles
    articles = relationship("Article", back_populates="source")


class Article(Base):
    """Model for news articles - EXACT match to database schema"""
    __tablename__ = "articles"
    
    # Only columns that actually exist in the database
    id = Column(String(32), primary_key=True)  # String ID as stored in database
    source_id = Column(Integer, ForeignKey('news_sources.id'))
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False)  # Note: 'link' not 'url'
    summary = Column(Text)
    content = Column(Text)
    published_date = Column(DateTime)
    content_hash = Column(String(64), unique=True, nullable=False)
    relevance_score = Column(Integer)  # INTEGER in database
    primary_category = Column(String(8))  # VARCHAR(8)
    confidence_level = Column(String(6))  # VARCHAR(6)
    
    # Relationships
    source = relationship("NewsSource", back_populates="articles")