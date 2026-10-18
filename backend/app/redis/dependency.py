import redis.asyncio as redis
from app.utils import settings

# Global Redis pool
redis_pool: redis.Redis = None

async def get_redis() -> redis.Redis:
    return redis_pool

async def init_redis():
    global redis_pool
    redis_pool = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )

async def close_redis():
    await redis_pool.aclose()