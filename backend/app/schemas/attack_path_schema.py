from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any

class AttackPath(BaseModel):
    scan_id: str
    severity: Optional[str] = None
    triage: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None
    commands: Optional[Dict[str, Any]] = None
    risk_summary: Optional[Dict[str, Any]] = None

    class Config:
        extra = "allow"   # <-- critical
    
    @model_validator(mode='before')
    @classmethod
    def remove_mongodb_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and '_id' in data:
            data = data.copy()
            data.pop('_id')
        return data


class AttackPathSummary(BaseModel):
    scan_id: str
    severity: Optional[str] = None
    triage: Optional[Dict[str, Any]] = None
    risk_summary: Optional[Dict[str, Any]] = None

    @model_validator(mode='before')
    @classmethod
    def remove_mongodb_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and '_id' in data:
            data = data.copy()
            data.pop('_id')
        return data


class VulnerabilitySummary(BaseModel):
    scan_id: str
    severity: Optional[str] = None
    created_at: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def remove_mongodb_id(cls, data: Any) -> Any:
        if isinstance(data, dict) and '_id' in data:
            data = data.copy()
            data.pop('_id')
        return data
