from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from typing import Literal


class PaymentCheckoutRequest(BaseModel):
    plan_id: str
    customer_email: Optional[EmailStr] = None
    quantity: int = Field(default=1, ge=1)
    user_id: Optional[str] = None
    from_plan_id: Optional[str] = None
    request_id: Optional[str] = None
    idempotency_key: Optional[str] = None


class PlanPaddlePriceMappingUpsertRequest(BaseModel):
    plan_id: str
    paddle_price_id: str
    paddle_environment: Optional[Literal["sandbox", "production"]] = None
    is_active: bool = True


class PlanPaddlePriceMappingResponse(BaseModel):
    id: UUID
    plan_id: UUID
    paddle_price_id: str
    paddle_environment: str
    is_active: bool
