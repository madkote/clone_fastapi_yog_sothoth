"""Expose cache utils."""
from .cache import get_default_cache_pool
from .redis import close_connection

__all__ = ('get_default_cache_pool', 'close_connection')
