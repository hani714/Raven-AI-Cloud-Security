from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

from app.models import Plans, Subscriptions
from app.schemas import PlanCreate

class SubscriptionsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _calculate_expiry(self, started_at: datetime) -> datetime:
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        else:
            started_at = started_at.astimezone(timezone.utc)

        # Move to next month same day
        next_month = started_at + relativedelta(months=1)

        # Set to end of that day (23:59:59)
        expires_at = next_month.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        return expires_at
    
    # Get plan by ID (id)
    async def get_plan_by_id(self, plan_id: str):
        result = await self.db.execute(
            select(Plans)
            .where(Plans.id == plan_id)
        )
        return result.scalar_one_or_none()

    # Get plan ID by name
    async def get_plan_id(self, plan_name: str):
        result = await self.db.execute(
            select(Plans.id)
            .filter(Plans.name == plan_name)
        )
        return result.scalar_one_or_none()

    # Get all plans
    async def get_plans(self):
        result = await self.db.execute(select(Plans))
        return result.scalars().all()

    # Create new plan
    async def create_plan(self, plan: PlanCreate):
        new_plan = Plans(
            name=plan.name,
            price=plan.price,
            max_environments=plan.max_environments,
            max_scans_per_month=plan.max_scans_per_month,
            scan_depth=plan.scan_depth,
            analysis_level=plan.analysis_level,
            history_days=plan.history_days
        )
        self.db.add(new_plan)
        await self.db.commit()
        await self.db.refresh(new_plan)
        return new_plan

    # Create new subscription
    async def create_subscription(self, u_id: str, p_id: str):
        now = datetime.now(timezone.utc)
        expires_at = self._calculate_expiry(now)
        new_subscription = Subscriptions(
            user_id=u_id,
            plan_id=p_id,
            current_environments=0,
            current_scans_per_month=0,
            expires_at=expires_at,
            current_period_start=now,
            current_period_end=expires_at,
            cancel_at_period_end=False,
            canceled_at=None,
            status="ACTIVE",
        )
        self.db.add(new_subscription)
        await self.db.commit()
        await self.db.refresh(new_subscription)
        return new_subscription

    # Get subscription by user ID
    async def get_subscription_by_user(self, user_id: str):
        result = await self.db.execute(
            select(Subscriptions)
            .where(Subscriptions.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert_subscription(self, user_id: str, plan_id: str):
        now = datetime.now(timezone.utc)
        expires_at = self._calculate_expiry(now)
        subscription = await self.get_subscription_by_user(user_id)

        if subscription:
            subscription.plan_id = plan_id
            subscription.started_at = now
            subscription.expires_at = expires_at
            subscription.current_period_start = now
            subscription.current_period_end = expires_at
            subscription.cancel_at_period_end = False
            subscription.canceled_at = None
            subscription.status = "ACTIVE"
            await self.db.commit()
            await self.db.refresh(subscription)
            return subscription

        return await self.create_subscription(user_id, plan_id)
    
    # Get current subscription by user ID (id, name)
    async def get_current_subscription(self, user_id: str):
        result = await self.db.execute(
            select(
                Subscriptions.id.label("subscription_id"),
                Plans.id.label("plan_id"),
                Plans.name.label("plan_name"),
                Subscriptions.expires_at.label("expires_at"),
            )
            .join(Plans, Subscriptions.plan_id == Plans.id)
            .where(Subscriptions.user_id == user_id)
            .where(Subscriptions.expires_at > func.now())
            .where(Subscriptions.status != "CANCELED")
        )
        return result.mappings().one_or_none()

    async def schedule_cancel_at_period_end(self, user_id: str):
        subscription = await self.get_subscription_by_user(user_id)
        if not subscription:
            return None

        subscription.cancel_at_period_end = True
        subscription.status = "ACTIVE"

        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription
    
    # Get plan by user ID
    async def get_plan_by_user_id(self, user_id: str):
        result = await self.db.execute(
            select(Plans)
            .join(Subscriptions, Subscriptions.plan_id == Plans.id)
            .filter(Subscriptions.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    # Get current environments of a user
    async def get_current_environment(self, subscription_id: str):
        result = await self.db.execute(
            select(Subscriptions)
            .where(Subscriptions.id == subscription_id)
        )
        return result.scalar_one_or_none()