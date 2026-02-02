"""Redis Connection Management"""

import redis
from typing import Optional
from app.core.config import settings

# Create Redis connection
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20
)


def get_redis() -> redis.Redis:
    """
    Get Redis client
    """
    return redis_client


async def cache_get(key: str) -> Optional[str]:
    """
    Get value from cache
    """
    return redis_client.get(key)


async def cache_set(key: str, value: str, expire: int = 3600):
    """
    Set value in cache with expiration
    """
    redis_client.setex(key, expire, value)


async def cache_delete(key: str):
    """
    Delete value from cache
    """
    redis_client.delete(key)


async def cache_exists(key: str) -> bool:
    """
    Check if key exists in cache
    """
    return redis_client.exists(key) > 0
