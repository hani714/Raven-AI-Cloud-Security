from fastapi import APIRouter, Request, status

from app.utils.dependency import PaymentService, CurrentUser
from app.schemas import (
    PaymentCheckoutRequest,
    PlanPaddlePriceMappingUpsertRequest,
    PlanPaddlePriceMappingResponse,
)

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/webhook/paddle", status_code=status.HTTP_200_OK)
async def paddle_webhook(request: Request, service: PaymentService):
    return await service.webhook_handler(request)

@router.post("/", status_code=status.HTTP_200_OK)
async def create_transaction(request: PaymentCheckoutRequest, service: PaymentService, user: CurrentUser):
    return await service.create_transaction(
        plan_id=request.plan_id,
        customer_email=request.customer_email,
        quantity=request.quantity,
        user_id=user.id,
        from_plan_id=request.from_plan_id,
        request_id=request.request_id,
        idempotency_key=request.idempotency_key,
    )


@router.post("/mappings", response_model=PlanPaddlePriceMappingResponse, status_code=status.HTTP_200_OK)
async def upsert_plan_price_mapping(
    request: PlanPaddlePriceMappingUpsertRequest,
    service: PaymentService,
):
    return await service.upsert_plan_price_mapping(
        plan_id=request.plan_id,
        paddle_price_id=request.paddle_price_id,
        paddle_environment=request.paddle_environment,
        is_active=request.is_active,
    )
