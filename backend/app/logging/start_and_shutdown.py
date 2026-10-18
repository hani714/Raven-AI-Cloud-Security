import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
import traceback

from app.sentry import init_sentry
from app.redis import init_redis, close_redis
from app.database.postgre import init_db
from app.logging.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    queue_listener = None

    try:

        # init_sentry()

        queue_listener = setup_logging()
        app.state.queue_listener = queue_listener

        await init_db()
        
        await init_redis()
        
        yield

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    finally:
        
        if queue_listener:
            queue_listener.stop()

        try:
            await close_redis()
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")