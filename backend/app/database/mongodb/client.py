from __future__ import annotations

import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from .config import get_settings

_CLIENT: Optional[AsyncIOMotorClient] = None
_LOCK = asyncio.Lock()

def _build_client() -> AsyncIOMotorClient:
    settings = get_settings()
    uri = settings.uri

    client = AsyncIOMotorClient(
        uri,
        appname=settings.app_name,
        connectTimeoutMS=settings.connect_timeout_ms,
        socketTimeoutMS=settings.socket_timeout_ms,
        tls=settings.tls,
        directConnection=settings.direct_connection,
    )

    return client

async def get_mongo_client(force_refresh: bool = False) -> AsyncIOMotorClient:
    global _CLIENT

    if _CLIENT is not None and not force_refresh:
        return _CLIENT
    
    async with _LOCK:
        if _CLIENT is not None and not force_refresh:
            return _CLIENT
            
        _CLIENT = _build_client()
        await _CLIENT.admin.command('ping')
    
    return _CLIENT

async def get_database(database_name: Optional[str] = None) -> AsyncIOMotorDatabase:
    client = await get_mongo_client()
    settings = get_settings()
    db_name = database_name or settings.database
    return client[db_name]

async def close_mongo_client():
    global _CLIENT
    if _CLIENT is not None:
        _CLIENT.close()
        _CLIENT = None
