"""
Article Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArticleBase(BaseModel):
    """Base article schema"""
    title: str = Field(..., max_length=500)
    link: str = Field(..., max_length=1000)
    summary: Optional[str] = None
    content: Optional[str] = None
    published_date: Optional[datetime] = None
    relevance_score: Optional[int] = Field(None, ge=1, le=100)
    primary_category: Optional[str] = Field(None, max_length=50)
    confidence_level: Optional[str] = Field(None, max_length=20)


class ArticleCreate(ArticleBase):
    """Schema for creating articles"""
    source_id: int
    content_hash: str = Field(..., max_length=64)


class ArticleUpdate(BaseModel):
    """Schema for updating articles"""
    title: Optional[str] = Field(None, max_length=500)
    summary: Optional[str] = None
    content: Optional[str] = None
    relevance_score: Optional[int] = Field(None, ge=1, le=100)
    primary_category: Optional[str] = Field(None, max_length=50)
    confidence_level: Optional[str] = Field(None, max_length=20)
    processed: Optional[str] = Field(None, max_length=20)


class ArticleResponse(ArticleBase):
    """Schema for article responses"""
    id: UUID
    source_id: int
    content_hash: str
    processed: str
    source_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for paginated article lists"""
    articles: list[ArticleResponse]
    total: int
    skip: int
    limit: int
    has_more: bool