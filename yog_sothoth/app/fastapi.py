"""FastAPI application."""
from fastapi import FastAPI

from yog_sothoth import settings
from yog_sothoth.api.utils import build_prefix
from yog_sothoth.utils.project import get_project_version

app = FastAPI(
    title='Yog Sothoth',
    description='Self-registration app for Matrix homeserver',
    version=get_project_version(),
    debug=settings.DEBUG,
    openapi_url=build_prefix(settings.OPENAPI_URL),
    docs_url=build_prefix(settings.DOCS_URL),
    redoc_url=build_prefix(settings.REDOC_URL),
)
