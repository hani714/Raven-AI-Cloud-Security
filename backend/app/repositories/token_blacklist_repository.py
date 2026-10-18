from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app import models

class TokenBlacklistRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_token(self, token: str, user_id: str, expires_at: datetime):
        # Database column is TIMESTAMP WITHOUT TIME ZONE, so persist naive UTC.
        if expires_at.tzinfo is not None:
            expires_at = expires_at.astimezone(timezone.utc).replace(tzinfo=None)

        blacklisted_token = models.BlackListToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(blacklisted_token)
        await self.db.commit()
        await self.db.refresh(blacklisted_token)
        return blacklisted_token

    async def is_blacklisted(self, token: str) -> bool:
        now_utc_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        result = await self.db.execute(
            select(models.BlackListToken)
            .where(
                models.BlackListToken.token == token,
                models.BlackListToken.expires_at > now_utc_naive
            )
        )
        record = result.scalar_one_or_none()
        return record is not None
