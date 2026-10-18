from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models

class EnvironmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Return only one environment by environment ID
    async def get_by_id(self, environment_id: str):
        result = await self.db.execute(
            select(models.Environments)
            .where(models.Environments.id == environment_id)
        )
        return result.scalar_one_or_none()

    # Return all environments for a specific user
    async def get_by_user(self, user_id: str):
        result = await self.db.execute(
            select(models.Environments)
            .where(models.Environments.user_id == user_id)
        )
        return result.scalars().all()

    # Create a new environment and increment user's current environments count
    async def create(self, environment: models.Environments, sub: models.Subscriptions):
        if environment.user_id is None:
            environment.user_id = sub.user_id

        self.db.add(environment)
        sub.current_environments = (sub.current_environments or 0) + 1
        await self.db.commit()
        await self.db.refresh(environment)
        return environment
    
    # Delete an environment
    async def delete(self, environment: models.Environments, sub: models.Subscriptions):
        await self.db.delete(environment)
        sub.current_environments = max((sub.current_environments or 1) - 1, 0)
        await self.db.commit()
        return environment
