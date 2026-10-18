import hashlib
import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException, status
from typing import Optional

from app.payment import PaddlePayment
from app.repositories import (
    BillingLedgerRepository,
    PaymentTransactionsRepository,
    PlanBillingRepository,
    SubscriptionChangeRequestsRepository,
    SubscriptionsRepository,
    WebhookEventsRepository,
)
from app.schemas import PlanPaddlePriceMappingResponse


logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.paddle = PaddlePayment()
        self.plan_billing_repo = PlanBillingRepository(db)
        self.subscriptions_repo = SubscriptionsRepository(db)
        self.payment_transactions_repo = PaymentTransactionsRepository(db)
        self.webhook_events_repo = WebhookEventsRepository(db)
        self.billing_ledger_repo = BillingLedgerRepository(db)
        self.subscription_change_requests_repo = SubscriptionChangeRequestsRepository(db)

    async def _parse_webhook_payload(self, request: Request):
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            payload = await request.json()
            if not isinstance(payload, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid webhook JSON payload",
                )
            return payload

        form = await request.form()
        payload = dict(form)

        if isinstance(payload.get("data"), str):
            try:
                payload["data"] = json.loads(payload["data"])
            except json.JSONDecodeError:
                pass

        return payload

    @staticmethod
    def _extract_webhook_metadata(raw_body: bytes, payload: dict) -> tuple[str, str]:
        fallback_event_id = hashlib.sha256(raw_body).hexdigest()

        provider_event_id = str(
            payload.get("event_id")
            or payload.get("notification_id")
            or payload.get("id")
            or fallback_event_id
        )
        event_type = str(
            payload.get("event_type")
            or payload.get("eventType")
            or payload.get("alert_name")
            or payload.get("type")
            or "unknown"
        )

        return provider_event_id, event_type

    @staticmethod
    def _extract_transaction_fields(payload: dict) -> tuple[str | None, str | None, str | None, float | None, str | None]:
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}

        transaction_id = (
            payload.get("transaction_id")
            or data.get("id")
            or payload.get("id")
        )
        event_status = payload.get("status") or data.get("status")
        customer_id = payload.get("customer_id") or data.get("customer_id")

        details = data.get("details") if isinstance(data.get("details"), dict) else {}
        totals = details.get("totals") if isinstance(details.get("totals"), dict) else {}

        raw_amount = totals.get("total") or data.get("amount")
        amount = None
        if raw_amount is not None:
            try:
                amount = float(raw_amount)
            except (TypeError, ValueError):
                amount = None

        currency = (
            totals.get("currency_code")
            or details.get("currency_code")
            or data.get("currency_code")
            or payload.get("currency")
        )

        return transaction_id, event_status, customer_id, amount, currency

    @staticmethod
    def _is_success_event(event_type: str, event_status: str | None) -> bool:
        event_type_lower = event_type.lower()
        status_lower = (event_status or "").lower()

        return (
            "transaction.completed" in event_type_lower
            or "transaction.paid" in event_type_lower
            or status_lower in {"paid", "completed", "succeeded", "billed"}
        )

    @staticmethod
    def _is_failure_event(event_type: str, event_status: str | None) -> bool:
        event_type_lower = event_type.lower()
        status_lower = (event_status or "").lower()

        return (
            "transaction.failed" in event_type_lower
            or "transaction.canceled" in event_type_lower
            or status_lower in {"failed", "declined", "canceled", "cancelled"}
        )

    async def _process_transaction_webhook(
        self,
        event_type: str,
        payload: dict,
        provider_event_id: str,
    ) -> dict:
        transaction_id, event_status, customer_id, amount, currency = self._extract_transaction_fields(payload)

        if not transaction_id:
            return {"outcome": "ignored", "reason": "missing_transaction_id"}

        transaction = await self.payment_transactions_repo.get_by_paddle_transaction_id(str(transaction_id))
        if not transaction:
            return {"outcome": "ignored", "reason": "unknown_transaction_id", "transaction_id": transaction_id}

        if self._is_success_event(event_type, event_status):
            await self.payment_transactions_repo.update_status(
                transaction=transaction,
                status="SUCCEEDED",
                paddle_customer_id=customer_id,
                amount=amount,
                currency=currency,
            )

            subscription = await self.subscriptions_repo.upsert_subscription(
                user_id=str(transaction.user_id),
                plan_id=str(transaction.to_plan_id),
            )

            change_request = await self.subscription_change_requests_repo.get_by_payment_transaction_id(
                str(transaction.id)
            )
            if change_request and change_request.status != "APPLIED":
                await self.subscription_change_requests_repo.update_status(
                    request=change_request,
                    status="APPLIED",
                    message="Payment succeeded and subscription was applied.",
                    resolved=True,
                )

            await self.billing_ledger_repo.create_entry(
                user_id=str(transaction.user_id),
                subscription_id=str(subscription.id),
                payment_transaction_id=str(transaction.id),
                provider_event_id=provider_event_id,
                entry_type="CHARGE",
                amount=amount,
                currency=currency,
                metadata_json={
                    "event_type": event_type,
                    "transaction_status": event_status,
                    "paddle_transaction_id": transaction.paddle_transaction_id,
                },
            )

            await self.billing_ledger_repo.create_entry(
                user_id=str(transaction.user_id),
                subscription_id=str(subscription.id),
                payment_transaction_id=str(transaction.id),
                provider_event_id=provider_event_id,
                entry_type="SUBSCRIPTION_CHANGE",
                metadata_json={
                    "event_type": event_type,
                    "from_plan_id": str(transaction.from_plan_id) if transaction.from_plan_id else None,
                    "to_plan_id": str(transaction.to_plan_id),
                },
            )

            return {
                "outcome": "processed",
                "status": "SUCCEEDED",
                "transaction_id": transaction.paddle_transaction_id,
                "subscription_id": str(subscription.id),
            }

        if self._is_failure_event(event_type, event_status):
            failed_status = "CANCELED" if (event_status or "").lower() in {"canceled", "cancelled"} else "FAILED"
            await self.payment_transactions_repo.update_status(
                transaction=transaction,
                status=failed_status,
                error_reason=f"Webhook signaled unsuccessful payment ({event_type})",
                paddle_customer_id=customer_id,
                amount=amount,
                currency=currency,
            )

            change_request = await self.subscription_change_requests_repo.get_by_payment_transaction_id(
                str(transaction.id)
            )
            if change_request and change_request.status not in {"FAILED", "CANCELED"}:
                await self.subscription_change_requests_repo.update_status(
                    request=change_request,
                    status=failed_status,
                    message="Payment failed; subscription change was not applied.",
                    resolved=True,
                )

            return {
                "outcome": "processed",
                "status": failed_status,
                "transaction_id": transaction.paddle_transaction_id,
            }

        return {
            "outcome": "ignored",
            "reason": "event_not_actionable",
            "transaction_id": transaction.paddle_transaction_id,
            "event_type": event_type,
            "event_status": event_status,
        }

    async def webhook_handler(self, request: Request):
        raw_body = await request.body()

        signature = request.headers.get("Paddle-Signature", "")
        if not signature:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Paddle-Signature header")
        
        if not self.paddle.verify_paddle_signature(raw_body, signature):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

        payload = await self._parse_webhook_payload(request)
        provider_event_id, event_type = self._extract_webhook_metadata(raw_body, payload)

        existing_event = await self.webhook_events_repo.get_by_provider_event_id(provider_event_id)
        if existing_event:
            return {"ok": True, "deduplicated": True, "event_id": provider_event_id}

        event = await self.webhook_events_repo.create_event(
            provider_event_id=provider_event_id,
            event_type=event_type,
            payload_json=payload,
        )

        try:
            result = await self._process_transaction_webhook(
                event_type=event_type,
                payload=payload,
                provider_event_id=provider_event_id,
            )

            if result.get("outcome") == "ignored":
                await self.webhook_events_repo.set_status(event, "IGNORED")
            else:
                await self.webhook_events_repo.set_status(event, "PROCESSED")

            return {"ok": True, **result}
        except Exception as exc:
            logger.exception("Failed to process Paddle webhook")
            await self.webhook_events_repo.set_status(event, "FAILED", processing_error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook processing failed",
            )

    async def create_transaction(
        self,
        plan_id: str,
        customer_email: Optional[str] = None,
        quantity: int = 1,
        user_id: Optional[str] = None,
        from_plan_id: Optional[str] = None,
        request_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ):
        mapping = await self.plan_billing_repo.get_active_price_mapping(
            plan_id=plan_id,
            paddle_environment=self.paddle.environment_name,
        )

        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"No active Paddle price mapping configured for plan_id={plan_id} "
                    f"in {self.paddle.environment_name} environment"
                ),
            )

        transaction = await self.paddle.create_transaction(
            price_id=mapping.paddle_price_id,
            customer_email=customer_email,
            quantity=quantity,
        )

        persisted_transaction = None
        if user_id:
            resolved_request_id = None
            if request_id:
                try:
                    resolved_request_id = str(uuid.UUID(request_id))
                except ValueError as exc:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="request_id must be a valid UUID",
                    ) from exc

            persisted_transaction = await self.payment_transactions_repo.create_transaction(
                user_id=user_id,
                from_plan_id=from_plan_id,
                to_plan_id=plan_id,
                paddle_transaction_id=transaction["transaction_id"],
                paddle_price_id=mapping.paddle_price_id,
                request_id=resolved_request_id,
                idempotency_key=idempotency_key,
                status="PENDING",
            )

        return {
            "checkout_url": transaction["checkout_url"],
            "transaction_id": transaction["transaction_id"],
            "payment_transaction_id": str(persisted_transaction.id) if persisted_transaction else None,
            "price_id": mapping.paddle_price_id,
            "environment": self.paddle.environment_name,
        }

    async def upsert_plan_price_mapping(
        self,
        plan_id: str,
        paddle_price_id: str,
        paddle_environment: Optional[str] = None,
        is_active: bool = True,
    ) -> PlanPaddlePriceMappingResponse:
        plan = await self.subscriptions_repo.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan not found for plan_id={plan_id}",
            )

        resolved_environment = paddle_environment or self.paddle.environment_name

        if resolved_environment not in {"sandbox", "production"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="paddle_environment must be either 'sandbox' or 'production'",
            )

        try:
            self.paddle.assert_price_exists(paddle_price_id)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        mapping = await self.plan_billing_repo.upsert_price_mapping(
            plan_id=plan_id,
            paddle_price_id=paddle_price_id,
            paddle_environment=resolved_environment,
            is_active=is_active,
        )

        return PlanPaddlePriceMappingResponse(
            id=mapping.id,
            plan_id=mapping.plan_id,
            paddle_price_id=mapping.paddle_price_id,
            paddle_environment=mapping.paddle_environment,
            is_active=mapping.is_active,
        )