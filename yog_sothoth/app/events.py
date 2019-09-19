"""Application events."""
from yog_sothoth.cache import close_connection
from yog_sothoth.cache import get_default_cache_pool
from .fastapi import app


@app.on_event('startup')
async def startup() -> None:
    """Initialize the cache."""
    app.cache = await get_default_cache_pool()


@app.on_event('shutdown')
async def shutdown() -> None:
    """Close connection to the cache."""
    # noinspection PyUnresolvedReferences
    await close_connection(app.cache)
