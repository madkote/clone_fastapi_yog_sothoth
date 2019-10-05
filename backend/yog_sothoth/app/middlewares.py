"""Application middlewares."""
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import Response

from yog_sothoth.conf import settings
from yog_sothoth.objects import RateLimit
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
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allow_headers=['Authorization', 'Content-Type'],
    allow_credentials=False,
    max_age=24 * 3600,
)


@app.middleware('http')
async def rate_limit(request: Request, call_next):
    """Rate limit clients to avoid spammers/lammers."""
    identifying_headers = ('user-agent', 'x-forwarded-for', 'x-real-ip')
    identifier_parts = (request.headers.get(header, '')
                        for header in identifying_headers)
    identifier = ':'.join(identifier_parts)
    limiting = RateLimit(request.app.cache, settings.RATE_LIMIT)
    if await limiting.verify_below(identifier):
        response = await call_next(request)
        return response

    retry_after = await limiting.get_expiration_time(identifier)
    return Response(
        'Maximum allowed requests reached',
        status.HTTP_429_TOO_MANY_REQUESTS,
        {'Retry-After': str(retry_after)},
    )
