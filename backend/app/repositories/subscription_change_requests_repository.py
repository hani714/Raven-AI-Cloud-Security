from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SubscriptionChangeRequest


class SubscriptionChangeRequestsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_idempotency_key(self, idempotency_key: str) -> SubscriptionChangeRequest | None:
        result = await self.db.execute(
            select(SubscriptionChangeRequest).where(
                SubscriptionChangeRequest.idempotency_key == idempotency_key
            )
        )
        return result.scalar_one_or_none()

    async def get_latest_for_user(self, user_id: str) -> SubscriptionChangeRequest | None:
        result = await self.db.execute(
            select(SubscriptionChangeRequest)
            .where(SubscriptionChangeRequest.user_id == user_id)
            .order_by(desc(SubscriptionChangeRequest.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_payment_transaction_id(
        self, payment_transaction_id: str
    ) -> SubscriptionChangeRequest | None:
        result = await self.db.execute(
            select(SubscriptionChangeRequest).where(
                SubscriptionChangeRequest.payment_transaction_id == payment_transaction_id
            )
        )
        return result.scalar_one_or_none()

    async def create_request(
        self,
        user_id: str,
        from_plan_id: str | None,
        to_plan_id: str,
        status: str,
        requires_payment: bool,
        payment_transaction_id: str | None = None,
        idempotency_key: str | None = None,
        checkout_url: str | None = None,
        message: str | None = None,
    ) -> SubscriptionChangeRequest:
        request = SubscriptionChangeRequest(
            user_id=user_id,
            from_plan_id=from_plan_id,
            to_plan_id=to_plan_id,
            payment_transaction_id=payment_transaction_id,
            idempotency_key=idempotency_key,
            status=status,
            requires_payment=requires_payment,
            checkout_url=checkout_url,
            message=message,
        )
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def update_status(
        self,
        request: SubscriptionChangeRequest,
        status: str,
        message: str | None = None,
        resolved: bool = False,
    ) -> SubscriptionChangeRequest:
        request.status = status
        request.message = message
        if resolved:
            request.resolved_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(request)
        return request
