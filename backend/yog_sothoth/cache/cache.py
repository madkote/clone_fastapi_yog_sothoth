"""Cache base classes and functions."""
from aioredis import Redis

from .redis import get_redis_pool

DEFAULT_CACHE_ALIAS = 'default'


async def get_default_cache_pool() -> Redis:
    """Get a cache connection pool object."""
    return await get_redis_pool(DEFAULT_CACHE_ALIAS)
