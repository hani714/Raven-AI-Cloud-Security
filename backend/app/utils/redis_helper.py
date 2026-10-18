import json
import logging
from app.utils import settings

logger = logging.getLogger(__name__)

async def get_cached(cache, key: str) -> dict | None:
    if not cache:
        return None
    try:
        cached = await cache.get(key)
        if cached:
            return json.loads(cached)
    except (Exception, json.JSONDecodeError) as e:
        logger.warning(f"Cache read failed for {key}: {e}")
    return None

async def set_cached(cache, key: str, data: dict) -> None:
    if not cache:
        return
    try:
        await cache.setex(key, settings.REDIS_TTL, json.dumps(data))
    except Exception as e:
        logger.warning(f"Cache write failed for {key}: {e}")