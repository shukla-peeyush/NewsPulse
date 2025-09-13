"""
Article Model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from .base import Base, TimestampMixin


class Article(Base, TimestampMixin):
    """Model for news articles"""
    __tablename__ = "articles"
    
    # Primary key as UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to news source
    source_id = Column(Integer, ForeignKey('news_sources.id'))
    
    # Article content
    title = Column(String(500), nullable=False)
    link = Column(String(1000), nullable=False)  # URL to original article
    summary = Column(Text)
    content = Column(Text)  # Full article content
    published_date = Column(DateTime)
    
    # Content identification
    content_hash = Column(String(64), unique=True, nullable=False)
    
    # Classification and scoring
    relevance_score = Column(Integer)  # 1-100 relevance score
    primary_category = Column(String(50))
    confidence_level = Column(String(20))  # HIGH, MEDIUM, LOW
    
    # Processing status
    processed = Column(String(20), default='pending')  # pending, processed, failed
    
    # Relationships
    source = relationship("NewsSource", back_populates="articles")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', source_id={self.source_id})>"
    
    @property
    def source_name(self):
        """Get source name if source relationship is loaded"""
        return self.source.name if self.source else None