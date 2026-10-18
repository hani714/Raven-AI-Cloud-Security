from fastapi import APIRouter

from app.schemas import (
    PlanResponse,
    PlanCreate,
    PlanDetailedResponse,
    NewSubscriptionRequest,
    RevokeSubscriptionRequest,
    RevokeSubscriptionResponse,
    SubscriptionChangeResponse,
)
from app.utils.dependency import SubscriptionService, CurrentUser

router = APIRouter(prefix = "/subscription", tags=["Subscription"])

@router.get("/", response_model=list[PlanResponse])
async def get_plans(user: CurrentUser, service: SubscriptionService):
    return await service.get_plans()

@router.post("/", response_model=PlanDetailedResponse)
async def create_plan(plan: PlanCreate, service: SubscriptionService):
    return await service.create_plan(plan)

@router.post("/new", response_model=SubscriptionChangeResponse)
async def new_subscription(user: CurrentUser, request: NewSubscriptionRequest, service: SubscriptionService):
    return await service.new_subscription(user.id, request.plan_id)

@router.post("/revoke", response_model=RevokeSubscriptionResponse)
async def revoke_subscription(user: CurrentUser, request: RevokeSubscriptionRequest, service: SubscriptionService):
    return await service.revoke_subscription(user.id)