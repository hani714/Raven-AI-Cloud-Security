import uuid
from app.database.postgre import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, func

class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    
    current_environments = Column(Integer, nullable=False, default=0)
    current_scans_per_month = Column(Integer, nullable=False, default=0)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end = Column(Boolean, nullable=False, default=False, server_default="false")
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, default="ACTIVE", server_default="ACTIVE")

    # Relationships
    user = relationship("Users", back_populates="subscription", foreign_keys=[user_id])
    plan = relationship("Plans", back_populates="subscriptions", foreign_keys=[plan_id])

    __table_args__ = (
        CheckConstraint("current_environments >= 0", name="ck_sub_current_envs_non_negative"),
        CheckConstraint("current_scans_per_month >= 0", name="ck_sub_current_scans_non_negative"),
        CheckConstraint(
            "status IN ('ACTIVE', 'PENDING_PAYMENT', 'FAILED', 'EXPIRED', 'CANCELED')",
            name="ck_subscriptions_status",
        ),
    )