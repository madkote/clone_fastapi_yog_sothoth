"""Expose API v1 router and prefix."""
from .urls import api_router
from .urls import version_prefix

__all__ = (
    'api_router',
    'version_prefix',
)
