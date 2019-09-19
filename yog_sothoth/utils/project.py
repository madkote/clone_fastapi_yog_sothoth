"""Project utils."""
import os

from yog_sothoth import settings


def get_project_version() -> str:
    """Get app version from PyProject TOML file."""
    pyproject = os.path.join(os.path.dirname(settings.BASE_DIR), 'pyproject.toml')
    with open(pyproject, 'rt') as toml_file:
        for line in toml_file:
            if 'version' in line:
                _, version = line.split(' = ')
                return version.strip()[1:-1]  # Remove double quotes
    return '0.1.0'  # Default version when not found
