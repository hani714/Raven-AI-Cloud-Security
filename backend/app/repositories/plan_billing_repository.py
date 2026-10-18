from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PlanPaddlePrice


class PlanBillingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_price_mapping(self, plan_id: str, paddle_environment: str) -> PlanPaddlePrice | None:
        result = await self.db.execute(
            select(PlanPaddlePrice)
            .where(PlanPaddlePrice.plan_id == plan_id)
            .where(PlanPaddlePrice.paddle_environment == paddle_environment)
            .where(PlanPaddlePrice.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def upsert_price_mapping(
        self,
        plan_id: str,
        paddle_price_id: str,
        paddle_environment: str,
        is_active: bool = True,
    ) -> PlanPaddlePrice:
        result = await self.db.execute(
            select(PlanPaddlePrice)
            .where(PlanPaddlePrice.plan_id == plan_id)
            .where(PlanPaddlePrice.paddle_environment == paddle_environment)
        )
        mapping = result.scalar_one_or_none()

        if mapping:
            mapping.paddle_price_id = paddle_price_id
            mapping.is_active = is_active
        else:
            mapping = PlanPaddlePrice(
                plan_id=plan_id,
                paddle_price_id=paddle_price_id,
                paddle_environment=paddle_environment,
                is_active=is_active,
            )
            self.db.add(mapping)

        await self.db.commit()
        await self.db.refresh(mapping)
        return mapping