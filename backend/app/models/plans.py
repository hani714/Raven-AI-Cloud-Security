import uuid
from app.database.postgre import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Integer, DateTime, Enum

from .enums import AnalysisLevel, ScanDepth

class Plans(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    name = Column(String, unique=True, nullable=False)
    price = Column(String, nullable=False)
    max_environments = Column(Integer, nullable=False)
    max_scans_per_month = Column(Integer, nullable=False)
    scan_depth = Column(Enum(ScanDepth, name="scan_depth_enum"), nullable=False)
    analysis_level = Column(Enum(AnalysisLevel, name="analysis_level_enum"), nullable=False)
    history_days = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Back references
    subscriptions = relationship("Subscriptions", back_populates="plan", foreign_keys="Subscriptions.plan_id")
    paddle_prices = relationship(
        "PlanPaddlePrice",
        back_populates="plan",
        foreign_keys="PlanPaddlePrice.plan_id",
        cascade="all, delete-orphan",
    )