import uuid

from app.database.postgre import Base
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID


class SubscriptionChangeRequest(Base):
    __tablename__ = "subscription_change_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    from_plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    to_plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    payment_transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=True, unique=True)
    idempotency_key = Column(String, nullable=True, unique=True)

    status = Column(String, nullable=False, default="PENDING_PAYMENT", server_default="PENDING_PAYMENT")
    requires_payment = Column(Boolean, nullable=False, default=True, server_default="true")
    checkout_url = Column(String, nullable=True)
    message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('SUBMITTED', 'NO_OP', 'PENDING_PAYMENT', 'APPLIED', 'FAILED', 'CANCELED', 'REVOKE_SCHEDULED')",
            name="ck_subscription_change_requests_status",
        ),
    )