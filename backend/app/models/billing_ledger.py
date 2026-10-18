import uuid

from app.database.postgre import Base
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID


class BillingLedger(Base):
    __tablename__ = "billing_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True)
    payment_transaction_id = Column(UUID(as_uuid=True), ForeignKey("payment_transactions.id"), nullable=True)

    provider = Column(String, nullable=False, default="paddle", server_default="paddle")
    provider_event_id = Column(String, nullable=True)
    entry_type = Column(String, nullable=False)

    amount = Column(Numeric(10, 2), nullable=True)
    currency = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    event_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('CHARGE', 'REFUND', 'ADJUSTMENT', 'SUBSCRIPTION_CHANGE', 'REVOKE_SCHEDULED', 'REVOKE_EFFECTIVE')",
            name="ck_billing_ledger_entry_type",
        ),
    )