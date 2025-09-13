"""
Cache Service
"""

import json
import logging
from typing import Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Simple cache service with optional Redis backend"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client if URL is provided"""
        if settings.redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except ImportError:
                logger.warning("Redis not installed, using memory cache")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using memory cache")
                self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        try:
            ttl = ttl or settings.cache_ttl
            
            if self.redis_client:
                serialized_value = json.dumps(value, default=str)
                self.redis_client.setex(key, ttl, serialized_value)
            else:
                # Simple memory cache (no TTL implementation)
                self.memory_cache[key] = value
                
                # Prevent memory cache from growing too large
                if len(self.memory_cache) > 1000:
                    # Remove oldest entries
                    keys_to_remove = list(self.memory_cache.keys())[:100]
                    for k in keys_to_remove:
                        del self.memory_cache[k]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if successful
        """
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache entries
        
        Returns:
            True if successful
        """
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Cache statistics
        """
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'type': 'redis',
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'total_keys': self.redis_client.dbsize()
                }
            else:
                return {
                    'type': 'memory',
                    'connected': True,
                    'total_keys': len(self.memory_cache)
                }
                
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {
                'type': 'unknown',
                'connected': False,
                'error': str(e)
            }


# Global cache instance
cache = CacheService()


def cache_key(*args) -> str:
    """
    Generate cache key from arguments
    
    Args:
        *args: Arguments to include in key
        
    Returns:
        Cache key string
    """
    return ":".join(str(arg) for arg in args)


def cached_response(key: str, ttl: Optional[int] = None):
    """
    Decorator for caching function responses
    
    Args:
        key: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key_str)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, ttl)
            
            return result
        return wrapper
    return decorator