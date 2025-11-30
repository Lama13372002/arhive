"""Redis configuration and client management."""

import redis.asyncio as redis
from typing import Optional

from .config import settings


class RedisClient:
    """Redis client wrapper."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._client is None:
            self._client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
        return self._client
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> redis.Redis:
    """Get Redis client for dependency injection."""
    return await redis_client.get_client()

