from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import uuid
from decimal import Decimal, InvalidOperation

from app.schemas import (
    PlanResponse,
    PlanCreate,
    PlanDetailedResponse,
    RevokeSubscriptionResponse,
    SubscriptionChangeResponse,
    SubscriptionChangeStatus,
)
from app.repositories import (
    BillingLedgerRepository,
    SubscriptionChangeRequestsRepository,
    SubscriptionsRepository,
)
from app.service.payment_service import PaymentService

class SubscriptionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subs_repo = SubscriptionsRepository(db)
        self.billing_ledger_repo = BillingLedgerRepository(db)
        self.subscription_change_requests_repo = SubscriptionChangeRequestsRepository(db)
        self.payment_service = PaymentService(db)

    @staticmethod
    def _is_paid_plan(price: str) -> bool:
        try:
            return Decimal(price) > 0
        except (InvalidOperation, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan price configuration",
            )

    async def get_plans(self):
        result = await self.subs_repo.get_plans()
        return [ PlanResponse.model_validate(row) for row in result ]

    async def create_plan(self, plan: PlanCreate):
        result = await self.subs_repo.create_plan(plan)
        return PlanDetailedResponse.model_validate(result)

    async def new_subscription(self, user_id: str, plan_id: str) -> SubscriptionChangeResponse:
        request_id = str(uuid.uuid7())

        target_plan = await self.subs_repo.get_plan_by_id(plan_id)
        if not target_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target plan not found",
            )

        current_sub = await self.subs_repo.get_current_subscription(user_id)
        current_plan_id = current_sub["plan_id"] if current_sub else None
        current_plan_name = current_sub["plan_name"] if current_sub else None

        if current_plan_id and str(current_plan_id) == str(target_plan.id):
            await self.subscription_change_requests_repo.create_request(
                user_id=user_id,
                from_plan_id=str(current_plan_id),
                to_plan_id=str(target_plan.id),
                status="NO_OP",
                requires_payment=False,
                idempotency_key=request_id,
                message="User is already on the requested plan.",
            )

            return SubscriptionChangeResponse(
                request_id=request_id,
                status=SubscriptionChangeStatus.NO_OP,
                user_id=user_id,
                target_plan_id=target_plan.id,
                target_plan_name=target_plan.name,
                current_plan_id=current_plan_id,
                current_plan_name=current_plan_name,
                subscription_id=current_sub["subscription_id"],
                requires_payment=False,
                effective_at=current_sub["expires_at"],
                message="User is already on the requested plan.",
            )

        if self._is_paid_plan(target_plan.price):
            transaction = await self.payment_service.create_transaction(
                plan_id=str(target_plan.id),
                user_id=user_id,
                from_plan_id=str(current_plan_id) if current_plan_id else None,
                request_id=request_id,
                idempotency_key=request_id,
            )

            await self.subscription_change_requests_repo.create_request(
                user_id=user_id,
                from_plan_id=str(current_plan_id) if current_plan_id else None,
                to_plan_id=str(target_plan.id),
                status="PENDING_PAYMENT",
                requires_payment=True,
                payment_transaction_id=transaction.get("payment_transaction_id"),
                idempotency_key=request_id,
                checkout_url=transaction.get("checkout_url"),
                message="Payment required before subscription change is applied.",
            )

            return SubscriptionChangeResponse(
                request_id=request_id,
                status=SubscriptionChangeStatus.PENDING_PAYMENT,
                user_id=user_id,
                target_plan_id=target_plan.id,
                target_plan_name=target_plan.name,
                current_plan_id=current_plan_id,
                current_plan_name=current_plan_name,
                subscription_id=current_sub["subscription_id"] if current_sub else None,
                requires_payment=True,
                checkout_url=transaction.get("checkout_url"),
                message="Payment required before subscription change is applied.",
            )

        updated_sub = await self.subs_repo.upsert_subscription(user_id, str(target_plan.id))

        await self.subscription_change_requests_repo.create_request(
            user_id=user_id,
            from_plan_id=str(current_plan_id) if current_plan_id else None,
            to_plan_id=str(target_plan.id),
            status="APPLIED",
            requires_payment=False,
            idempotency_key=request_id,
            message="Subscription updated successfully.",
        )

        await self.billing_ledger_repo.create_entry(
            user_id=user_id,
            subscription_id=str(updated_sub.id),
            entry_type="SUBSCRIPTION_CHANGE",
            metadata_json={
                "request_id": request_id,
                "from_plan_id": str(current_plan_id) if current_plan_id else None,
                "to_plan_id": str(target_plan.id),
                "applied_via": "free_plan_or_zero_amount",
            },
        )

        return SubscriptionChangeResponse(
            request_id=request_id,
            status=SubscriptionChangeStatus.APPLIED,
            user_id=user_id,
            target_plan_id=target_plan.id,
            target_plan_name=target_plan.name,
            current_plan_id=current_plan_id,
            current_plan_name=current_plan_name,
            subscription_id=updated_sub.id,
            requires_payment=False,
            effective_at=updated_sub.started_at,
            message="Subscription updated successfully.",
        )

    async def revoke_subscription(self, user_id: str) -> RevokeSubscriptionResponse:
        subscription = await self.subs_repo.get_subscription_by_user(user_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )

        current_plan = await self.subs_repo.get_plan_by_id(str(subscription.plan_id))
        if not current_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription plan not found",
            )

        if not self._is_paid_plan(current_plan.price):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Free plan subscriptions cannot be revoked.",
            )

        if subscription.cancel_at_period_end:
            return RevokeSubscriptionResponse(
                user_id=user_id,
                subscription_id=subscription.id,
                status=SubscriptionChangeStatus.REVOKE_SCHEDULED,
                effective_at=subscription.expires_at,
                message="Subscription revoke is already scheduled for period end.",
            )

        updated_subscription = await self.subs_repo.schedule_cancel_at_period_end(user_id)
        if not updated_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found",
            )

        request_id = str(uuid.uuid7())
        await self.subscription_change_requests_repo.create_request(
            user_id=user_id,
            from_plan_id=str(updated_subscription.plan_id),
            to_plan_id=str(updated_subscription.plan_id),
            status="REVOKE_SCHEDULED",
            requires_payment=False,
            idempotency_key=request_id,
            message="Subscription will be canceled at period end.",
        )

        await self.billing_ledger_repo.create_entry(
            user_id=user_id,
            subscription_id=str(updated_subscription.id),
            entry_type="REVOKE_SCHEDULED",
            metadata_json={
                "request_id": request_id,
                "effective_at": updated_subscription.expires_at.isoformat(),
            },
        )

        return RevokeSubscriptionResponse(
            user_id=user_id,
            subscription_id=updated_subscription.id,
            status=SubscriptionChangeStatus.REVOKE_SCHEDULED,
            effective_at=updated_subscription.expires_at,
            message="Subscription revoke scheduled for period end.",
        )
