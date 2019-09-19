"""Application routers."""
from yog_sothoth.api.root import router as api_router_root
from yog_sothoth.api.utils import build_prefix
from yog_sothoth.api.v1 import api_prefix_v1
from yog_sothoth.api.v1 import api_router_v1
from .fastapi import app

app.include_router(api_router_v1, prefix=build_prefix(api_prefix_v1))
app.include_router(api_router_root, prefix=build_prefix(''))
