import uuid

from app.database.postgre import Base
from sqlalchemy import CheckConstraint, Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    provider = Column(String, nullable=False, default="paddle", server_default="paddle")
    provider_event_id = Column(String, nullable=False, unique=True)
    event_type = Column(String, nullable=False)
    payload_json = Column(JSONB, nullable=False)

    processing_status = Column(String, nullable=False, default="RECEIVED", server_default="RECEIVED")
    processing_error = Column(Text, nullable=True)

    received_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "processing_status IN ('RECEIVED', 'PROCESSED', 'IGNORED', 'FAILED')",
            name="ck_webhook_events_processing_status",
        ),
    )