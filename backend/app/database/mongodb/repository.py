from __future__ import annotations

import logging
import uuid
from dataclasses import asdict, is_dataclass
from pydantic import BaseModel
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Dict, Any, Optional, List
from . import get_database
from app.utils import normalize_for_mongo


logger = logging.getLogger(__name__)


async def save_snapshot(
    service_name: str, 
    result, 
    *,
    resource_mappings: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:

    db = await get_database()

    try:
        doc = normalize_for_mongo(result.__dict__.copy())
    except Exception:
        raise

    doc["captured_at"] = datetime.now(timezone.utc).isoformat()

    summary: Dict[str, Any] = {"service": service_name, "resources_saved": {}}

    if resource_mappings:
        for field_name, collection_suffix in resource_mappings.items():
            raw_resources = doc.get(field_name) or []
            resources = []
            for r in raw_resources:
                try:
                    converted = normalize_for_mongo(r)
                    if isinstance(converted, dict):
                        resources.append(converted)
                    elif hasattr(r, "__dict__"):
                        resources.append(normalize_for_mongo(r.__dict__))
                except Exception:
                    try:
                        resources.append(normalize_for_mongo(r.__dict__))
                    except Exception:
                        continue

            if not resources:
                summary["resources_saved"][collection_suffix] = 0
                continue

            collection_name = f"{service_name}_{collection_suffix}"
            resource_col = db[collection_name]

            try:
                res = await resource_col.insert_many(resources, ordered=False)
                summary["resources_saved"][collection_suffix] = len(res.inserted_ids)
            except Exception as exc:
                logger.warning(
                    "Bulk insert failed for %s, falling back to row-by-row insert: %s",
                    collection_name,
                    str(exc),
                )
                count = 0
                for r in resources:
                    try:
                        await resource_col.insert_one(r)
                        count += 1
                    except Exception as row_exc:
                        logger.debug(
                            "Failed to insert resource into %s: %s",
                            collection_name,
                            str(row_exc),
                        )
                        continue                
                summary["resources_saved"][collection_suffix] = count

    return summary

async def get_by_scan_id(collection_name: str, scan_id) -> Optional[dict]:
    db = await get_database()
    collection: AsyncIOMotorCollection = db[collection_name]

    if scan_id is None:
        return []

    normalized_scan_id = str(scan_id)
    docs = await collection.find({"scan_id": normalized_scan_id}).to_list(length=None)

    if not docs:
        try:
            parsed_uuid = uuid.UUID(normalized_scan_id)
            docs = await collection.find({"scan_id": str(parsed_uuid)}).to_list(length=None)
        except (ValueError, TypeError, AttributeError):
            docs = []

    for doc in docs:
        if "scan_id" in doc and doc["scan_id"] is not None:
            doc["scan_id"] = str(doc["scan_id"])
    
    return docs

async def get_vuln_summary(collection_name: str, scan_ids: List[str]) -> list[Dict[str, Any]]:
    db = await get_database()
    collection: AsyncIOMotorCollection = db[collection_name]

    if not scan_ids:
        return []

    pipeline = [
        {"$match": {"scan_id": {"$in": scan_ids}}},
        {
            "$project": {
                "severity": {"$toLower": {"$ifNull": ["$severity", "unknown"]}},
                "created_at": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {"$toDate": "$created_at"}
                    }
                }
            }
        },
        {
            "$group": {
                "_id": {"created_at": "$created_at", "severity": "$severity"},
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.created_at",
                "pairs": {"$push": {"k": "$_id.severity", "v": "$count"}}
            }
        },
        {"$project": {"_id": 0, "created_at": "$_id", "pairs": {"$arrayToObject": "$pairs"}}},
        {"$replaceRoot": {"newRoot": {"$mergeObjects": [{"created_at": "$created_at"}, "$pairs"]}}},
        {"$sort": {"created_at": 1}},
    ]

    return await collection.aggregate(pipeline).to_list(length=None)

async def store_result(collection_name: str, data: BaseModel) -> str:
    db = await get_database()
    collection: AsyncIOMotorCollection = db[collection_name]

    attack_path_dict = normalize_for_mongo(data.model_dump(exclude_none=True))
    attack_path_dict['created_at'] = datetime.now(timezone.utc).isoformat()
    
    result = await collection.insert_one(attack_path_dict)
    return str(result.inserted_id)