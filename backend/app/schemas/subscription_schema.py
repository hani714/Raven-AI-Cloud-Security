from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Optional

from app.models.enums import ScanDepth, AnalysisLevel

class PlanResponse(BaseModel):
    id: UUID
    name: str
    price: str
    max_environments: int
    max_scans_per_month: int
    scan_depth: ScanDepth
    analysis_level: AnalysisLevel
    history_days: int

    model_config = {
        "from_attributes": True
    }

class PlanDetailedResponse(PlanResponse):
    created_at: datetime

class PlanCreate(BaseModel):
    name: str
    price: str
    max_environments: int
    max_scans_per_month: int
    scan_depth: ScanDepth
    analysis_level: AnalysisLevel
    history_days: int

    model_config = {
        "from_attributes": True
    }

class NewSubscriptionRequest(BaseModel):
    user_id: str
    plan_id: str


class SubscriptionChangeStatus(str, Enum):
    NO_OP = "NO_OP"
    PENDING_PAYMENT = "PENDING_PAYMENT"
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    REVOKE_SCHEDULED = "REVOKE_SCHEDULED"


class SubscriptionChangeResponse(BaseModel):
    request_id: str
    status: SubscriptionChangeStatus
    user_id: str
    target_plan_id: UUID
    target_plan_name: str
    current_plan_id: Optional[UUID] = None
    current_plan_name: Optional[str] = None
    subscription_id: Optional[UUID] = None
    requires_payment: bool
    checkout_url: Optional[str] = None
    effective_at: Optional[datetime] = None
    message: str


class RevokeSubscriptionRequest(BaseModel):
    user_id: str


class RevokeSubscriptionResponse(BaseModel):
    user_id: str
    subscription_id: UUID
    status: SubscriptionChangeStatus
    effective_at: datetime
    message: str