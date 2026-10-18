from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.sql import func
from app.database.postgre import Base

class OTP(Base):
    __tablename__ = "otp"
    
    # Primary key
    email = Column(String(255), primary_key=True, index=True)
    
    # Security fields
    code_hash = Column(String(255), nullable=False)
    
    # Timing controls
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_sent_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # Security counters
    attempts = Column(Integer, default=0, nullable=False)
    resend_count = Column(Integer, default=0, nullable=False)  # ← Track resend abuse
    
    # Status
    verified = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)  # ← Temporary lockout
    
    # Audit trail
    ip_address = Column(String(45), nullable=True)  # ← Track source IP
    user_agent = Column(String(512), nullable=True)  # ← Track client