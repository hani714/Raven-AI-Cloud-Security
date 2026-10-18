from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PaymentTransaction


class PaymentTransactionsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_transaction(
        self,
        user_id: str,
        to_plan_id: str,
        paddle_transaction_id: str,
        paddle_price_id: str,
        from_plan_id: str | None = None,
        request_id: str | None = None,
        idempotency_key: str | None = None,
        status: str = "PENDING",
    ) -> PaymentTransaction:
        transaction = PaymentTransaction(
            user_id=user_id,
            from_plan_id=from_plan_id,
            to_plan_id=to_plan_id,
            paddle_transaction_id=paddle_transaction_id,
            paddle_price_id=paddle_price_id,
            request_id=request_id,
            idempotency_key=idempotency_key,
            status=status,
        )
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_by_paddle_transaction_id(self, paddle_transaction_id: str) -> PaymentTransaction | None:
        result = await self.db.execute(
            select(PaymentTransaction).where(PaymentTransaction.paddle_transaction_id == paddle_transaction_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        transaction: PaymentTransaction,
        status: str,
        error_reason: str | None = None,
        paddle_customer_id: str | None = None,
        amount: float | None = None,
        currency: str | None = None,
    ) -> PaymentTransaction:
        transaction.status = status
        transaction.error_reason = error_reason
        if paddle_customer_id:
            transaction.paddle_customer_id = paddle_customer_id
        if amount is not None:
            transaction.amount = amount
        if currency:
            transaction.currency = currency

        if status == "SUCCEEDED":
            transaction.completed_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
