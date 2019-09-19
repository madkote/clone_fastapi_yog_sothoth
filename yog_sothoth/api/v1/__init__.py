"""Expose API v1 router and prefix."""
from .urls import api_router as api_router_v1
from .urls import version_prefix as api_prefix_v1

__all__ = ('api_router_v1', 'api_prefix_v1')
