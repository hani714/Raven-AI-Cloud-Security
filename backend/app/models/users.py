import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.postgre import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    subscription = relationship("Subscriptions", back_populates="user", foreign_keys="Subscriptions.user_id", uselist=False)
    environments = relationship("Environments", back_populates="users", foreign_keys="Environments.user_id", cascade="all, delete-orphan")
    user_api_keys = relationship("UserApiKeys", back_populates="user", foreign_keys="UserApiKeys.user_id", cascade="all, delete-orphan")