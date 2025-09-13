"""
Application Configuration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "NewsPulse"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False
    
    # Database
    database_url: str = "sqlite:///./data/newspulse.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["*"]
    
    # RSS Feeds
    rss_feeds: list = [
        "https://e27.co/feed/",
        "https://www.techinasia.com/rss",
        "https://fintechnews.asia/feed/",
        "https://www.thenationalnews.com/rss.xml",
        "https://www.arabianbusiness.com/rss.xml"
    ]
    
    # Cache
    redis_url: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()