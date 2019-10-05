"""Rate limiting object."""
from hashlib import blake2b
from math import ceil
from typing import Optional

from aioredis import Redis


class RateLimit:
    """Implement rate limit mechanism."""

    __slots__ = ('_cache', 'limit')

    def __init__(self, cache: Redis, limit: Optional[int] = None):
        """Verify cache values lower than given limit to implement rate limiting."""
        self._cache: Redis = cache
        self.limit: int = limit if limit else 0

    @classmethod
    def _derive_key(cls, identifier: str) -> str:
        """Get a hashed key from an identifier."""
        hashed_identifier = blake2b(identifier.encode(), digest_size=16).hexdigest()
        return f'{cls.__name__}:{hashed_identifier}'

    @staticmethod
    def compute_expiration_time(count: int) -> int:
        """Calculate expiration time using a back-off exponential formula.

        The applied formula is: ⌈(2^C-1)/2+1⌉
        """
        return ceil(1 / 2 * (2 ** count - 1) + 1)

    async def verify_below(self, identifier: str) -> bool:
        """Verify if a key is below given limit."""
        key = self._derive_key(identifier)
        count = await self._cache.incr(key)
        ttl = self.compute_expiration_time(count)
        await self._cache.expire(key, ttl)
        return count < self.limit

    async def get_expiration_time(self, identifier: str) -> int:
        """Get the expiration time of a given identifier.

        :return: The expiration time for the identifier or 0.
        """
        key = self._derive_key(identifier)
        ttl = await self._cache.ttl(key)
        return ttl if ttl > 0 else 0
