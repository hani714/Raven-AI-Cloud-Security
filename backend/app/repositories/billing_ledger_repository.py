from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BillingLedger


class BillingLedgerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_entry(
        self,
        user_id: str,
        entry_type: str,
        subscription_id: str | None = None,
        payment_transaction_id: str | None = None,
        provider_event_id: str | None = None,
        amount: float | None = None,
        currency: str | None = None,
        metadata_json: dict | None = None,
    ) -> BillingLedger:
        entry = BillingLedger(
            user_id=user_id,
            subscription_id=subscription_id,
            payment_transaction_id=payment_transaction_id,
            provider_event_id=provider_event_id,
            entry_type=entry_type,
            amount=amount,
            currency=currency,
            metadata_json=metadata_json,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def list_for_user(self, user_id: str, limit: int = 100) -> list[BillingLedger]:
        result = await self.db.execute(
            select(BillingLedger)
            .where(BillingLedger.user_id == user_id)
            .order_by(desc(BillingLedger.event_timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
