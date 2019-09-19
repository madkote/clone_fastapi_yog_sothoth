"""Application URL's."""
from fastapi import APIRouter

from .endpoints import registrations

version_prefix = '/v1'

api_router = APIRouter()
api_router.include_router(
    registrations.router,
    prefix='/registrations',
    tags=['registrations'],
)
