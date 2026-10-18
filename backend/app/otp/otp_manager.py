import secrets
import hashlib
from datetime import datetime, timedelta, timezone

class OTPManager:
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    MAX_RESENDS = 3
    LOCKOUT_MINUTES = 15
    RATE_LIMIT_SECONDS = 60  # Min time between resends
    
    @staticmethod
    def generate_otp() -> str:
        """Generate cryptographically secure 6-digit OTP"""
        return ''.join(secrets.choice('0123456789') for _ in range(OTPManager.OTP_LENGTH))
    
    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash OTP using SHA-256"""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    @staticmethod
    def verify_otp(input_otp: str, stored_hash: str) -> bool:
        """Verify OTP against stored hash"""
        return OTPManager.hash_otp(input_otp) == stored_hash
    
    @staticmethod
    def get_expiry_time() -> datetime:
        """Get OTP expiration timestamp"""
        return datetime.now(timezone.utc) + timedelta(minutes=OTPManager.OTP_EXPIRY_MINUTES)