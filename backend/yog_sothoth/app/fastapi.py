"""FastAPI application."""
from fastapi import FastAPI

from yog_sothoth.api.utils import build_prefix
from yog_sothoth.conf import settings
from yog_sothoth.utils.project import check_settings
from yog_sothoth.utils.project import get_project_version

check_settings()

description = (f'Self-registration app for Matrix homeserver'
               f'{" (DEV MODE)" if settings.DEVELOPMENT_MODE else ""}')
app = FastAPI(
    title='Yog-Sothoth',
    description=description,
    version=get_project_version(),
    debug=settings.DEBUG,
    openapi_url=build_prefix(settings.OPENAPI_URL_PATH),
    docs_url=build_prefix(settings.DOCS_URL_PATH),
    redoc_url=build_prefix(settings.REDOC_URL_PATH),
)
