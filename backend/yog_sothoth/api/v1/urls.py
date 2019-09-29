"""Application URL's."""
from fastapi import APIRouter

from yog_sothoth.conf import settings
from .endpoints import matrix
from .endpoints import registrations

version_prefix = '/v1'

api_router = APIRouter()
api_router.include_router(
    registrations.router,
    prefix='/registrations',
    tags=['registrations'],
)

if settings.DEVELOPMENT_MODE:
    api_router.include_router(
        matrix.router,
        prefix='/matrix',
        tags=['matrix'],
    )
