from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from app.models import OTP
from app.otp import OTPManager

class OTPRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_or_update_otp(self, email: str, code_hash: str, ip: str = None) -> OTP:
        result = await self.db.execute(
            select(OTP).where(OTP.email == email)
        )
        otp_record = result.scalar_one_or_none()

        if otp_record:
            # Update existing
            otp_record.code_hash = code_hash
            otp_record.expires_at = OTPManager.get_expiry_time()
            otp_record.last_sent_at = datetime.now(timezone.utc)
            otp_record.resend_count += 1
            otp_record.attempts = 0  # Reset attempts on new code
            # otp_record.ip_address = ip
        else:
            # Create new
            otp_record = OTP(
                email=email,
                code_hash=code_hash,
                expires_at=OTPManager.get_expiry_time(),
                last_sent_at=datetime.now(timezone.utc),
                # ip_address=ip
            )
            self.db.add(otp_record)
        
        await self.db.commit()
        await self.db.refresh(otp_record)
        return otp_record
    
    async def get_otp(self, email: str) -> OTP | None:
        result = await self.db.execute(
            select(OTP).where(OTP.email == email)
        )
        return result.scalar_one_or_none()
    
    async def increment_attempts(self, email: str) -> int:
        otp_record = await self.get_otp(email)
        if otp_record:
            otp_record.attempts += 1
            
            # Lock after max attempts
            if otp_record.attempts >= OTPManager.MAX_ATTEMPTS:
                otp_record.locked_until = datetime.now(timezone.utc) + timedelta(minutes=OTPManager.LOCKOUT_MINUTES)
            
            await self.db.commit()
            return otp_record.attempts
        return 0
    
    async def mark_verified(self, email: str):
        otp_record = await self.get_otp(email)
        if otp_record:
            otp_record.verified = True
            await self.db.commit()
    
    async def delete_otp(self, email: str):
        result = await self.db.execute(
            select(OTP).where(OTP.email == email)
        )
        otp_record = result.scalar_one_or_none()
        if otp_record:
            await self.db.delete(otp_record)
            await self.db.commit()

    async def is_rate_limited(self, email: str) -> bool:
        otp_record = await self.get_otp(email)
        if not otp_record:
            return False
        
        time_since_last = (datetime.now(timezone.utc) - otp_record.last_sent_at).total_seconds()
        return time_since_last < OTPManager.RATE_LIMIT_SECONDS
    
    async def is_locked(self, email: str) -> bool:
        otp_record = await self.get_otp(email)
        if not otp_record or not otp_record.locked_until:
            return False
        
        return datetime.now(timezone.utc) < otp_record.locked_until