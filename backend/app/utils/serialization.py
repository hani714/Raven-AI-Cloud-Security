import uuid
from dataclasses import is_dataclass, asdict
from typing import Any
from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel

def normalize_for_mongo(value: Any) -> Any:
    if isinstance(value, uuid.UUID):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, BaseModel):
        return normalize_for_mongo(value.model_dump(exclude_none=True))

    if is_dataclass(value):
        return normalize_for_mongo(asdict(value))

    if isinstance(value, dict):
        return {str(k): normalize_for_mongo(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [normalize_for_mongo(item) for item in value]

    return value

def inject_scan_id(items, scan_id):
    for item in items:
        item["scan_id"] = scan_id
    return items

async def convert_objectids(obj):
    if isinstance(obj, list):
        return [await convert_objectids(i) for i in obj]
    if isinstance(obj, dict):
        return {k: await convert_objectids(v) for k, v in obj.items()}
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj