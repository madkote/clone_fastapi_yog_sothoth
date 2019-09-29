"""Helper functions and classes definition for API endpoints."""
from aioredis import Redis
from starlette.requests import Request

from yog_sothoth.conf import settings


def get_cache(request: Request) -> Redis:
    """Cache session dependency for FastAPI."""
    return request.app.cache


def build_prefix(api_prefix: str) -> str:
    """Build API URL prefix."""
    return f'{settings.API_PREFIX}{api_prefix}'
