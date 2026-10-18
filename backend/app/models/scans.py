import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgre import Base

from .enums import ScanMode

class Scans(Base):
    __tablename__ = "scans"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    scan_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    mode = Column(Enum(ScanMode, name="scan_mode_enum"), default=ScanMode.enumeration, nullable=False)

    # Foreign key to Environments table
    environment_id = Column(UUID(as_uuid=True), ForeignKey("environments.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to Environment
    environment = relationship("Environments", back_populates="scans", foreign_keys=[environment_id])

    # Constraints
    __table_args__ = (
        UniqueConstraint('scan_name', 'environment_id', name='uix_environment_scan_name'),
        Index('ix_scans_environment_id', 'environment_id'),
    )

    @property
    def environment_name(self):
        return self.environment.name if self.environment else None
    
    def __repr__(self):
        return f"<Scan(id={self.id}, scan_name={self.scan_name}, environment_id={self.environment_id})>"
