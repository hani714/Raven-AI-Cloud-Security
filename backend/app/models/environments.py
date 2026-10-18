from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.postgre import Base

class Environments(Base):
    __tablename__ = "environments"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid7)
    
    name = Column(String, nullable=False)
    access_key = Column(String, nullable=False)
    secret_access_key = Column(String, nullable=False)
    region = Column(String, nullable=False)
    
    # Foreign key to Users table
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationship to User
    users = relationship("Users", back_populates="environments", foreign_keys=[user_id])
    
    # Relationship to Scans
    scans = relationship(
        "Scans",
        back_populates="environment",
        foreign_keys="Scans.environment_id",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='uix_user_environment_name'),
        Index('ix_environments_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<Environment(id={self.id}, name={self.name}, user_id={self.user_id})>"
