import uuid
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgre import Base

class UserApiKeys(Base):
    __tablename__ = "user_api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("provider_models.id", ondelete="CASCADE"), nullable=False)
    label = Column(String, nullable=True)
    encrypted_key = Column(Text, nullable=False)
    key_preview = Column(String(4), nullable=False)

    # Relationships
    user = relationship("Users", back_populates="user_api_keys", foreign_keys=[user_id])
    provider = relationship("Providers", back_populates="user_api_keys", foreign_keys=[provider_id])
    model = relationship("ProviderModels", back_populates="user_api_keys", foreign_keys=[model_id])