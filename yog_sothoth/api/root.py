"""Application main endpoints."""
from fastapi import APIRouter
from fastapi import Header
from starlette import status
from starlette.responses import Response

from yog_sothoth import settings
from .utils import build_prefix

router = APIRouter()


@router.get('/', status_code=status.HTTP_307_TEMPORARY_REDIRECT)
def read(response: Response, user_agent: str = Header(None)):
    """Redirect to the documentation."""
    browsers = ('Firefox', 'Chrome', 'Chromium', 'Opera', 'MSIE', 'Safari')
    if any(browser in user_agent for browser in browsers):
        # Redirect human readable
        response.headers['Location'] = build_prefix(settings.DOCS_URL)
    else:
        # Redirect machine
        response.headers['Location'] = build_prefix(settings.OPENAPI_URL)
