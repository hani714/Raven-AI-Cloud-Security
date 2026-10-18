import uuid

from app.database.postgre import Base
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    from_plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    to_plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    paddle_transaction_id = Column(String, nullable=False, unique=True)
    paddle_customer_id = Column(String, nullable=True)
    paddle_price_id = Column(String, nullable=False)

    status = Column(String, nullable=False, default="PENDING", server_default="PENDING")
    amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)

    request_id = Column(UUID(as_uuid=True), nullable=True, unique=True)
    idempotency_key = Column(String, nullable=True, unique=True)
    error_reason = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "status IN ('INITIATED', 'PENDING', 'SUCCEEDED', 'FAILED', 'CANCELED')",
            name="ck_payment_transactions_status",
        ),
    )