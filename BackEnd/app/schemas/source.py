"""
News Source Pydantic Schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class NewsSourceBase(BaseModel):
    """Base news source schema"""
    name: str = Field(..., max_length=100)
    website_url: str = Field(..., max_length=500)
    rss_url: Optional[str] = Field(None, max_length=500)
    region: Optional[str] = Field(None, max_length=50)
    language: str = Field(default="en", max_length=10)
    priority: int = Field(default=1, ge=1, le=10)
    enabled: bool = Field(default=True)


class NewsSourceCreate(NewsSourceBase):
    """Schema for creating news sources"""
    pass


class NewsSourceUpdate(BaseModel):
    """Schema for updating news sources"""
    name: Optional[str] = Field(None, max_length=100)
    website_url: Optional[str] = Field(None, max_length=500)
    rss_url: Optional[str] = Field(None, max_length=500)
    region: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    priority: Optional[int] = Field(None, ge=1, le=10)
    enabled: Optional[bool] = None


class NewsSourceResponse(NewsSourceBase):
    """Schema for news source responses"""
    id: int
    last_scraped: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NewsSourceWithStats(NewsSourceResponse):
    """News source with article statistics"""
    article_count: int = 0
    last_article_date: Optional[datetime] = None