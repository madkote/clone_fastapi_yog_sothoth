"""Settings for Yog Sothoth."""
import logging.config
import os
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Redis
REDIS_HOST: str = os.getenv('YOG_REDIS_HOST', '127.0.0.1')
REDIS_PORT: int = os.getenv('YOG_REDIS_PORT', 6379)
REDIS_PASSWORD: Optional[str] = os.getenv('YOG_REDIS_PASSWORD')
REDIS_DB: int = int(os.getenv('YOG_REDIS_DB', 0))
CACHE_TTL: int = int(os.getenv('YOG_CACHE_TTL', 48 * 3600))
CACHE = {
    'default': {
        'BACKEND': 'yog_sothoth.cache.redis',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'PASSWORD': REDIS_PASSWORD,
            'TIMEOUT': 2,
        },
    },
}

# Prefix for your API, such as /api/yog or /yog (must begin with slash)
API_PREFIX: str = os.getenv('YOG_API_PREFIX', '').rstrip('/')
# Misc URLs (must begin with slash)
OPENAPI_URL = os.getenv('YOG_OPENAPI_URL', '/openapi.json').rstrip('/')
DOCS_URL = os.getenv('YOG_DOCS_URL', '/docs').rstrip('/')
REDOC_URL = os.getenv('YOG_REDOC_URL', '/redoc').rstrip('/')

# Application host (used to check the Host header and others)
ALLOWED_HOST = os.getenv('YOG_HOST', '*')

# Logging
_loglevel_raw = os.getenv('YOG_LOG_LEVEL', 'INFO').upper()
if _loglevel_raw in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    LOGLEVEL: str = _loglevel_raw
else:
    LOGLEVEL: str = 'INFO'
LOGGING: dict = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} p:{process:d} t:{thread:d} '
                      '[{name}.{funcName}:{lineno:d}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
        'yog_sothoth': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
    },
}

# Debug
_debug = os.getenv('YOG_DEBUG', 'false')
DEBUG = True if _debug.lower() == 'true' else False

# Allow settings override
try:
    from local_settings import *  # noqa
except ImportError:
    pass

logging.config.dictConfig(LOGGING)
