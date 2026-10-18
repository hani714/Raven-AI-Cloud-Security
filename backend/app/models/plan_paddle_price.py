import uuid

from app.database.postgre import Base
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class PlanPaddlePrice(Base):
    __tablename__ = "plan_paddle_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    paddle_price_id = Column(String, nullable=False, unique=True)
    paddle_environment = Column(String, nullable=False, default="sandbox")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    plan = relationship("Plans", back_populates="paddle_prices", foreign_keys=[plan_id])

    __table_args__ = (
        UniqueConstraint("plan_id", "paddle_environment", name="uq_plan_paddle_price_plan_env"),
        CheckConstraint(
            "paddle_environment IN ('sandbox', 'production')",
            name="ck_plan_paddle_price_environment",
        ),
    )