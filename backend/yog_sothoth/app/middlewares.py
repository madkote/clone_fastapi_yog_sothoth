"""Application middlewares."""
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from yog_sothoth.conf import settings
from .fastapi import app

# List of defaults for localhost
ALLOWED_ORIGINS = [
    'http://127.0.0.1:3000',  # Frontend
]
# HTTPS protocol hardcoded :)
ALLOWED_ORIGINS.extend(f'https://{host}' for host in settings.ALLOWED_HOSTS)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['Authorization', 'Content-Type'],
    allow_credentials=False,
    max_age=24 * 3600,
)

if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
