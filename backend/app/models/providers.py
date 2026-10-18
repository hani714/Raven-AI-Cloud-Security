import uuid
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgre import Base


class Providers(Base):
    __tablename__ = "providers"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    slug = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    models = relationship("ProviderModels", back_populates="provider", foreign_keys="ProviderModels.provider_id", cascade="all, delete-orphan")
    user_api_keys = relationship("UserApiKeys", back_populates="provider", foreign_keys="UserApiKeys.provider_id")
