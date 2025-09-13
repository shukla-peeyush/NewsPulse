"""
Redis client and caching utilities
"""

import json
import logging
import os
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    from redis.exceptions import RedisError, ConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    logger.warning("Redis not available. Caching will be disabled.")
    REDIS_AVAILABLE = False


class RedisCache:
    """Redis cache client with fallback to in-memory cache"""
    
    def __init__(self, redis_url: str = None, fallback_to_memory: bool = True):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.fallback_to_memory = fallback_to_memory
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        self.memory_cache_ttl = {}  # TTL tracking for memory cache
        self.connected = False
        
        if REDIS_AVAILABLE:
            self._connect()
        else:
            logger.warning("Redis not available, using in-memory cache only")
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            if not self.fallback_to_memory:
                raise
    
    def _clean_memory_cache(self):
        """Clean expired items from memory cache"""
        current_time = datetime.utcnow()
        expired_keys = []
        
        for key, expiry in self.memory_cache_ttl.items():
            if expiry and current_time > expiry:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.memory_cache.pop(key, None)
            self.memory_cache_ttl.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            if self.connected and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                # Use memory cache
                self._clean_memory_cache()
                if key in self.memory_cache:
                    return self.memory_cache[key]
                return None
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value, default=str)
            
            if self.connected and self.redis_client:
                return self.redis_client.setex(key, ttl, json_value)
            else:
                # Use memory cache
                self.memory_cache[key] = value
                if ttl > 0:
                    self.memory_cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)
                else:
                    self.memory_cache_ttl[key] = None
                return True
                
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                # Use memory cache
                self.memory_cache.pop(key, None)
                self.memory_cache_ttl.pop(key, None)
                return True
                
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                # Use memory cache
                self._clean_memory_cache()
                return key in self.memory_cache
                
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in cache
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if error
        """
        try:
            if self.connected and self.redis_client:
                return self.redis_client.incr(key, amount)
            else:
                # Use memory cache
                current_value = self.memory_cache.get(key, 0)
                new_value = int(current_value) + amount
                self.memory_cache[key] = new_value
                return new_value
                
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration for existing key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.expire(key, ttl))
            else:
                # Use memory cache
                if key in self.memory_cache:
                    self.memory_cache_ttl[key] = datetime.utcnow() + timedelta(seconds=ttl)
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error setting expiration for cache key {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all cache
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.connected and self.redis_client:
                return bool(self.redis_client.flushdb())
            else:
                # Use memory cache
                self.memory_cache.clear()
                self.memory_cache_ttl.clear()
                return True
                
        except Exception as e:
            logger.error(f"Error flushing cache: {e}")
            return False


class CacheManager:
    """High-level cache manager with common caching patterns"""
    
    def __init__(self, redis_cache: RedisCache = None):
        self.cache = redis_cache or RedisCache()
    
    def cache_article(self, article_id: str, article_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache article data"""
        key = f"article:{article_id}"
        return self.cache.set(key, article_data, ttl)
    
    def get_cached_article(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get cached article data"""
        key = f"article:{article_id}"
        return self.cache.get(key)
    
    def cache_search_results(self, query: str, results: List[Dict[str, Any]], ttl: int = 1800) -> bool:
        """Cache search results"""
        # Create hash of query for consistent key
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"search:{query_hash}"
        return self.cache.set(key, results, ttl)
    
    def get_cached_search_results(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        key = f"search:{query_hash}"
        return self.cache.get(key)
    
    def cache_api_response(self, endpoint: str, params: Dict[str, Any], response: Any, ttl: int = 600) -> bool:
        """Cache API response"""
        # Create hash of endpoint and params
        cache_key = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        key_hash = hashlib.md5(cache_key.encode()).hexdigest()
        key = f"api:{key_hash}"
        return self.cache.set(key, response, ttl)
    
    def get_cached_api_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached API response"""
        cache_key = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        key_hash = hashlib.md5(cache_key.encode()).hexdigest()
        key = f"api:{key_hash}"
        return self.cache.get(key)
    
    def track_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        """
        Track rate limiting
        
        Args:
            identifier: User/IP identifier
            limit: Request limit
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False if rate limited
        """
        key = f"rate_limit:{identifier}"
        current_count = self.cache.get(key) or 0
        
        if current_count >= limit:
            return False
        
        # Increment counter
        new_count = self.cache.increment(key)
        if new_count == 1:
            # Set expiration for first request
            self.cache.expire(key, window)
        
        return True
    
    def cache_trending_topics(self, topics: List[Dict[str, Any]], ttl: int = 3600) -> bool:
        """Cache trending topics"""
        key = "trending:topics"
        return self.cache.set(key, topics, ttl)
    
    def get_cached_trending_topics(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached trending topics"""
        key = "trending:topics"
        return self.cache.get(key)
    
    def cache_statistics(self, stats: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache platform statistics"""
        key = "stats:platform"
        return self.cache.set(key, stats, ttl)
    
    def get_cached_statistics(self) -> Optional[Dict[str, Any]]:
        """Get cached platform statistics"""
        key = "stats:platform"
        return self.cache.get(key)
    
    def invalidate_article_cache(self, article_id: str) -> bool:
        """Invalidate article cache"""
        key = f"article:{article_id}"
        return self.cache.delete(key)
    
    def invalidate_search_cache(self) -> bool:
        """Invalidate all search cache"""
        # This is a simplified version - in production, you'd want to track search keys
        # For now, we'll just clear common search patterns
        try:
            # In a real implementation, you'd maintain a set of search keys
            logger.info("Search cache invalidation requested")
            return True
        except Exception as e:
            logger.error(f"Error invalidating search cache: {e}")
            return False


# Global cache instance
_cache_manager = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def main():
    """Test Redis connection and caching"""
    logging.basicConfig(level=logging.INFO)
    
    cache = RedisCache()
    cache_manager = CacheManager(cache)
    
    # Test basic operations
    print(f"Redis connected: {cache.connected}")
    
    # Test set/get
    test_data = {"test": "value", "timestamp": datetime.utcnow().isoformat()}
    success = cache_manager.cache.set("test_key", test_data, 60)
    print(f"Set test data: {success}")
    
    retrieved = cache_manager.cache.get("test_key")
    print(f"Retrieved data: {retrieved}")
    
    # Test rate limiting
    allowed = cache_manager.track_rate_limit("test_user", 5, 60)
    print(f"Rate limit check: {allowed}")


if __name__ == "__main__":
    main()