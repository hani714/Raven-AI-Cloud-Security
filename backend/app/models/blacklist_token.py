import uuid
from sqlalchemy import Column, String, func, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.database.postgre import Base

class BlackListToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid7)
    
    token = Column(String, nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
    expires_at = Column(DateTime, nullable=False)