import redis
from redis.exceptions import RedisError
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

# Redis connection pool
_redis_pool = None

def get_redis():
    """
    Get Redis client instance from connection pool.
    Returns a Redis client that can be used for operations.
    """
    global _redis_pool
    
    try:
        if _redis_pool is None:
            _redis_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True  # Automatically decode responses to strings
            )
        
        return redis.Redis(connection_pool=_redis_pool)
    except RedisError as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise

def init_redis():
    """Initialize Redis connection"""
    try:
        redis_client = get_redis()
        redis_client.ping()  # Synchronous ping
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

def close_redis():
    """Close Redis connection"""
    try:
        redis_client = get_redis()
        redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
        raise 