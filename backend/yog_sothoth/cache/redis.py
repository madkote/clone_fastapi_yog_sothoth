"""Redis cache stuff."""
from typing import Dict
from typing import Tuple

import aioredis

from yog_sothoth.conf import settings


def get_address_and_options(alias: str) -> Tuple[str, Dict[str, any]]:
    """Get Redis address and options from settings."""
    config = settings.CACHE[alias]
    options = config.get('OPTIONS', {})
    return config['LOCATION'], {key.lower(): value for key, value in options.items()}


async def get_redis_pool(alias: str) -> aioredis.Redis:
    """Get a Redis connection pool object."""
    address, opts = get_address_and_options(alias)
    return await aioredis.create_redis_pool(address, **opts)


async def close_connection(cache: aioredis.Redis) -> None:
    """Close the connection for a Redis cache object."""
    cache.close()
    await cache.wait_closed()
