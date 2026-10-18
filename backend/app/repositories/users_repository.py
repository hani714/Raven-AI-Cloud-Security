from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models import Users, Subscriptions
from app.repositories.subscriptions_repository import SubscriptionsRepository

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.subs_repo = SubscriptionsRepository(db)

    # Return current environments number of a user
    async def get_current_environment(self, users_id: str):
        result = await self.db.execute(
                select(Users.current_environments)
                .where(Users.id == users_id)
            )
        return result.scalar()
    
    # Return current environments number and current scans per month of a user
    async def get_scan_activity(self, users_id: str):
        result = await self.db.execute(
            select(Subscriptions.current_environments, Subscriptions.current_scans_per_month)
            .where(Subscriptions.user_id == users_id)
        )
        return result.first()
    
    # Return user by ID
    async def get_user(self, users_id: str):
        result = await self.db.execute(
            select(Users)
            .where(Users.id == users_id)
            .options(selectinload(Users.subscription))
        )
        return result.scalar_one_or_none()

    # Return user by email
    async def get_user_by_email(self, email: str):
        result = await self.db.execute(
            select(Users)
            .where(Users.email == email)
        )
        return result.scalar_one_or_none()

    # Increment user's current environments count (called when new environment is created) and return updated user
    async def increment_environments(self, users_id: str):
        user = await self.get_user(users_id)
        if user:
            user.current_environments = (user.current_environments or 0) + 1
            await self.db.commit()
            await self.db.refresh(user)
        return user
    
    # Increment user's current scans per month count (called when new scan is created) and return updated user
    async def increment_scans_per_month(self, users_id: str):
        sub = await self.subs_repo.get_subscription_by_user(users_id)
        if sub:
            sub.current_scans_per_month = (sub.current_scans_per_month or 0) + 1
            await self.db.commit()
            await self.db.refresh(sub)
        return sub
    
    # Is user with email exists
    async def is_user_exists(self, email: str):
        return (await self.get_user_by_email(email)) is not None

    # Create new user
    async def create_user(self, email: str, hashed_password: str):
        new_user = Users(
            email=email,
            password=hashed_password,
            verified=False,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user
    
    # Check if user's email is verified
    async def is_email_verified(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return user.verified if user else False

    # Mark user's email as verified
    async def mark_email_verified(self, email: str):
        user = await self.get_user_by_email(email)
        if user:
            user.verified = True
            await self.db.commit()
            await self.db.refresh(user)
        return user
    
    # Verify user by setting verified field to True
    async def verify_user(self, user_id: str):
        user = await self.get_user(user_id)
        if user:
            user.verified = True
            await self.db.commit()
            await self.db.refresh(user)
        return user

    # Update user's password
    async def update_user_password(self, user_id: str, new_hashed_password: str):
        user = await self.get_user(user_id)
        if user:
            user.password = new_hashed_password
            await self.db.commit()
            await self.db.refresh(user)
        return user