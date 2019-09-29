"""Project utils."""
import logging
import os

from yog_sothoth.conf import settings

logger = logging.getLogger(__name__)


def get_project_version() -> str:
    """Get app version from PyProject TOML file efficiently."""
    try:
        return get_project_version.project_version  # Get "static" var
    except AttributeError:
        pass  # Read file

    project_version = '0.1.0'  # Default version when not found
    pyproject = os.path.join(os.path.dirname(settings.BASE_DIR), 'pyproject.toml')
    with open(pyproject, 'rt') as toml_file:
        for line in toml_file:
            if 'version' in line:
                _, version = line.split(' = ')
                project_version = version.strip()[1:-1]  # Remove double quotes
                break
    get_project_version.project_version = project_version  # Set "static" var

    return project_version


def check_settings() -> None:
    """Check for mandatory settings and raise exception if any not set."""
    setting_names = (name for name in dir(settings) if name.isupper())
    for name in setting_names:
        # If setting has no value and is not optional, fail.
        value = getattr(settings, name)
        missing = any((
            value is None,
            isinstance(value, str) and value == '',
        ))
        if missing and name not in settings.OPTIONAL_SETTINGS:
            raise ValueError(
                f'Missing setting or not set: {name} (verify environment '
                f'variable YOG_{name})',
            )
    if settings.DEVELOPMENT_MODE:
        logger.warning('!!! DEVELOPMENT MODE IS ACTIVE !!!')


def get_app_base_url() -> str:
    """Get the application base full URL including protocol."""
    # HTTPS protocol hardcoded :)
    host = settings.ALLOWED_HOSTS[0]
    return f'https://{host}{settings.API_PREFIX}'.rstrip('/')
