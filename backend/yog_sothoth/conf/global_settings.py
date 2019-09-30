"""Settings for Yog-Sothoth."""
import os
from typing import Optional
from typing import Tuple

# Points to the application root directory
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Development mode: this mode sets email usage to a local `aiosmtpd` server for
# development, enables debug, sets log level to debug and fakes Matrix
# registration using and internal fake API.
_development_mode: str = os.getenv('YOG_DEVELOPMENT_MODE', 'false')
DEVELOPMENT_MODE: bool = True if _development_mode.lower() == 'true' else False

# Redis
REDIS_HOST: str = os.getenv('YOG_REDIS_HOST', '')
REDIS_PORT: int = int(os.getenv('YOG_REDIS_PORT', 6379))
REDIS_PASSWORD: Optional[str] = os.getenv('YOG_REDIS_PASSWORD')
REDIS_DB: int = int(os.getenv('YOG_REDIS_DB', 0))
REDIS_CONNECTION_TIMEOUT: int = int(os.getenv('YOG_REDIS_CONNECTION_TIMEOUT', 2))

# Cache definition
CACHE_TTL: int = int(os.getenv('YOG_CACHE_TTL', 48 * 3600))
CACHE = {
    'default': {
        'BACKEND': 'yog_sothoth.cache.redis',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'PASSWORD': REDIS_PASSWORD,
            'TIMEOUT': REDIS_CONNECTION_TIMEOUT,
        },
    },
}

# Prefix for your API, such as /api/yog or /yog (must begin with slash)
API_PREFIX: str = os.getenv('YOG_API_PREFIX', '').rstrip('/')
# Misc URLs (must begin with slash)
OPENAPI_URL_PATH: str = os.getenv('YOG_OPENAPI_URL_PATH', '/openapi.json').rstrip('/')
DOCS_URL_PATH: str = os.getenv('YOG_DOCS_URL_PATH', '/docs').rstrip('/')
REDOC_URL_PATH: str = os.getenv('YOG_REDOC_URL_PATH', '/redoc').rstrip('/')

# Frontend URL if any (with protocol)
FRONTEND_URL: str = os.getenv('YOG_FRONTEND_URL', '')
# Matrix homeserver URL (with protocol)
MATRIX_URL: str = os.getenv('YOG_MATRIX_URL', '').rstrip('/')
# Matrix `registration_shared_secret` for homeservers with registration disabled
# IMPORTANT NOTE: this secret enables the creation of admin accounts! Handle with
# extra care. This application hardcodes the creation of user accounts only and I
# heavily recommend you to leave it like that.
# For more info see:
# https://github.com/matrix-org/synapse/blob/master/docs/admin_api/register_api.rst
MATRIX_REGISTRATION_SHARED_SECRET: Optional[str] = os.getenv(
    'YOG_MATRIX_REGISTRATION_SHARED_SECRET',
)

# Default timeout for requests done from the app
REQUESTS_TIMEOUT: int = int(os.getenv('YOG_REQUEST_TIMEOUT', 5))

# Application allowed hosts: used to check the Host header and CORS. The first
# one is considered the main one.
_allowed_hosts = os.getenv('YOG_ALLOWED_HOSTS', '')
ALLOWED_HOSTS: Tuple[str] = tuple(
    host.strip() for host in _allowed_hosts.split(',') if host
)

# Logging
_loglevel_raw = os.getenv('YOG_LOGLEVEL', '').upper()
if _loglevel_raw in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
    LOGLEVEL: str = _loglevel_raw
else:
    LOGLEVEL: str = 'DEBUG' if DEVELOPMENT_MODE else 'INFO'
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
        'yog_sothoth': {
            'handlers': ['console'],
            'level': LOGLEVEL,
        },
    },
}

# Debug
_debug = os.getenv('YOG_DEBUG', 'false')
DEBUG: bool = True if DEVELOPMENT_MODE else (True if _debug.lower() == 'true' else False)

# Email settings
EMAIL_HOST: str = os.getenv('YOG_EMAIL_HOST', '')
EMAIL_PORT: int = int(os.getenv('YOG_EMAIL_PORT', 465))
EMAIL_USERNAME: Optional[str] = os.getenv('YOG_EMAIL_USERNAME')
EMAIL_PASSWORD: Optional[str] = os.getenv('YOG_EMAIL_PASSWORD')
EMAIL_TIMEOUT: int = int(os.getenv('YOG_EMAIL_TIMEOUT', 60))
# Emails can only be sent over an encrypted channel. By default, it uses
# STARTTLS unless TLS is directly supported. This setting is to simply indicate
# to use TLS directly.
_email_tls = os.getenv('YOG_EMAIL_USE_TLS', 'false')
EMAIL_USE_TLS: bool = True if _email_tls.lower() == 'true' else False
# Email address used in the `From` field of sent emails.
EMAIL_SENDER_ADDRESS: str = os.getenv('YOG_EMAIL_SENDER_ADDRESS', '')
# Email subject prefix (used as is, you might want to leave a space at the end)
EMAIL_SUBJECT_PREFIX: str = os.getenv('YOG_EMAIL_SUBJECT_PREFIX', '[Yog Sothtoth] ')

# Managers email addresses comma-separated
_managers_addresses = os.getenv('YOG_MANAGERS_ADDRESSES', '')
MANAGERS_ADDRESSES: Tuple[str] = tuple(
    email.strip() for email in _managers_addresses.split(',') if email
)

# Contact email address to use in emails body to users and other parts
# (it will be public)
CONTACT_ADDRESS: str = os.getenv('YOG_CONTACT_ADDRESS', '')

##############################################################################
# DO NOT ADD SETTINGS AFTER THIS LINE
##############################################################################

# As default, all settings listed in this file are mandatory, except the ones
# indicated as optional below. Settings are checked when the app starts.
OPTIONAL_SETTINGS = {
    'REDIS_PASSWORD',
    'API_PREFIX',
    'FRONTEND_URL',
    'EMAIL_USERNAME',
    'EMAIL_PASSWORD',
    'EMAIL_SUBJECT_PREFIX',
    'CONTACT_ADDRESS',
}
