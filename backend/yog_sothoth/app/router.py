"""Application routers."""
import os
from importlib import import_module
from pathlib import Path

from yog_sothoth.api.root import router as api_router_root
from yog_sothoth.api.utils import build_prefix
from yog_sothoth.conf import settings
from .fastapi import app

# Add root API
app.include_router(api_router_root, prefix=build_prefix(''))

# Find and add endpoints
package_name = os.path.basename(settings.BASE_DIR)
api_path = Path(os.path.join(settings.BASE_DIR, 'api'))
for version_path in api_path.glob('v*/'):
    if version_path.is_dir():
        module = import_module(f'{package_name}.api.{version_path.name}', package_name)
        api_router = getattr(module, 'api_router')
        version_prefix = getattr(module, 'version_prefix')
        app.include_router(api_router, prefix=build_prefix(version_prefix))
