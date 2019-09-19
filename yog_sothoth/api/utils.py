"""Helper functions and classes definition for API endpoints."""
from starlette.requests import Request

from yog_sothoth import settings


def get_cache(request: Request):
    """Cache session dependency for FastAPI."""
    return request.app.cache


def build_prefix(api_prefix: str) -> str:
    """Build API URL prefix."""
    return f'{settings.API_PREFIX}{api_prefix}'
