"""Application initializations."""
# Import app components so that they are executed
from . import events  # noqa: F401
from . import middlewares  # noqa: F401
from . import router  # noqa: F401
from .fastapi import app

__all__ = (
    'app',
)
