import uuid
from sqlalchemy import Boolean, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgre import Base

class ProviderModels(Base):
    __tablename__ = "provider_models"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    provider = relationship("Providers", back_populates="models", foreign_keys=[provider_id])
    user_api_keys = relationship("UserApiKeys", back_populates="model", foreign_keys="UserApiKeys.model_id")
