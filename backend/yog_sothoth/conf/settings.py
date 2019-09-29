"""Import all settings and leave them ready to be used by the app."""
import logging.config

# noinspection PyUnresolvedReferences
from .global_settings import *  # noqa

# Allow settings override
try:
    from .local_settings import *  # noqa
except ImportError:
    pass

logging.config.dictConfig(LOGGING)  # noqa:F405
