"""Application middlewares."""
from starlette.middleware.trustedhost import TrustedHostMiddleware

from yog_sothoth import settings
from .fastapi import app

app.add_middleware(TrustedHostMiddleware, allowed_hosts=[settings.ALLOWED_HOST])
