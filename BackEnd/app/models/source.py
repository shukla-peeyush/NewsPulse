"""
News Source Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class NewsSource(Base, TimestampMixin):
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
    
    # Relationship to articles
    articles = relationship("Article", back_populates="source")
    
    def __repr__(self):
        return f"<NewsSource(id={self.id}, name='{self.name}', enabled={self.enabled})>"