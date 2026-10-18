from fastapi import HTTPException, status, BackgroundTasks
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import validate_email_address, hash_password, create_access_token, verify_password
from app.repositories import OTPRepository, UserRepository, SubscriptionsRepository
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.otp import OTPManager
from app.dto import OTPEmailDTO, EmailDTO
from app.utils import render_template, create_access_token, decode_access_token
from app.email import EmailService
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.otp_repo = OTPRepository(db)
        self.user_repo = UserRepository(db)
        self.email_service = EmailService()
        self.subs_repo = SubscriptionsRepository(db)


    # Register user
    async def register(self, user: UserRegister) -> UserResponse:
        # Validate password length
        if len(user.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )

        # Validate email address
        is_valid, error_msg = validate_email_address(user.email)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Check if user already exists
        existing_user = await self.user_repo.is_user_exists(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account with this email already exists"
            )
        
        if user.password != user.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password and confirm password do not match"
            )
        
        # Hash the password
        hashed_password = hash_password(user.password)
        
        # Create new user
        user = await self.user_repo.create_user(user.email, hashed_password)
        
        # Get default "Free" subscription plan ID
        plan_id = await self.subs_repo.get_plan_id("Free")
        if not plan_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default subscription plan is not configured"
            )

        # Link default plan to new user
        await self.subs_repo.create_subscription(user.id, plan_id)
        
        return user
    

    async def login(self, user_data: UserLogin) -> TokenResponse:
        # Find user by email
        user = await self.user_repo.get_user_by_email(user_data.email)

        # Check if user exists and is verified
        if user and not user.verified:
            logger.warning(
                    "Login failed: email not verified",
                    extra={"extra_data": {"email": user.email, "user_id": str(user.id)}}
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email address not verified. Please verify your email before logging in.",
            )
        
        # Check if user exists
        if not user:
            logger.warning(
                    "Login failed: user not found",
                    extra={"extra_data": {"email": user_data.email}}
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Verify password (plain passoword, hashed password)
        if not verify_password(user_data.password, user.password):
            logger.warning(
                    "Login failed: incorrect password",
                    extra={"extra_data": {"email": user.email, "user_id": str(user.id)}}
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        
        # Get user's subscription plan
        plan = await self.subs_repo.get_plan_by_user_id(user.id)
        
        # Prepare token payload
        token_payload = {
            "sub": user.email,
            "user_id": str(user.id),
            "subscription": {
                "id": str(plan.id),
                "name": plan.name,
                "scan_depth": plan.scan_depth.value,
                "analysis_level": plan.analysis_level.value,
                "max_scans_per_month": plan.max_scans_per_month,
                "max_environments": plan.max_environments,
            }
        }
        
        # Create access token
        access_token = create_access_token(
            data=token_payload
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    

    # Returns OTP
    async def send_otp(self, email: EmailStr, background_tasks: BackgroundTasks) -> dict:
        # Checks if user exist
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return {
                "message": "OTP sent successfully",
                "expires_in_minutes": OTPManager.OTP_EXPIRY_MINUTES
            }
    
        # Check rate limiting
        if await self.otp_repo.is_rate_limited(email):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {OTPManager.RATE_LIMIT_SECONDS} seconds before requesting another code"
            )

        # Check lockout
        if await self.otp_repo.is_locked(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Too many failed attempts. Account locked for {OTPManager.LOCKOUT_MINUTES} minutes"
            )

        # Check resend limit
        existing = await self.otp_repo.get_otp(email)
        if existing and existing.resend_count >= OTPManager.MAX_RESENDS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum OTP requests exceeded. Please try again later"
            )

        # Generate OTP
        otp_code = OTPManager.generate_otp()
        code_hash = OTPManager.hash_otp(otp_code)

        # Store in database
        otp_record = await self.otp_repo.create_or_update_otp(email, code_hash)

        # Send email in background
        data = OTPEmailDTO(
            code=otp_code,
            expiry_minutes=OTPManager.OTP_EXPIRY_MINUTES,
        )
        content = render_template(data)
        email_data = EmailDTO(
            to=email,
            subject="Raven Verification OTP",
            html=content
        )
        background_tasks.add_task(self.email_service.send_email_brevo, email_data)

        return {
            "message": "OTP sent successfully",
            "expires_in_minutes": OTPManager.OTP_EXPIRY_MINUTES
        }
        

    # Shared by both email verification and password reset flows
    async def _verify_otp_core(self, email: EmailStr, input_code: str):
        # Check lockout
        if await self.otp_repo.is_locked(email):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked due to too many failed attempts"
            )

        otp_record = await self.otp_repo.get_otp(email)

        if not otp_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No OTP found for this email"
            )

        # Check expiration
        if datetime.now(timezone.utc) > otp_record.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one"
            )

        # Verify code
        is_valid = OTPManager.verify_otp(input_code, otp_record.code_hash)

        if not is_valid:
            await self.otp_repo.increment_attempts(email)

            remaining = OTPManager.MAX_ATTEMPTS - otp_record.attempts - 1
            if remaining > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid OTP. {remaining} attempts remaining"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Too many failed attempts. Account locked temporarily"
                )

        # Clean up OTP record
        await self.otp_repo.mark_verified(email)
        await self.otp_repo.delete_otp(email)


    # Verify OTP — email verification flow
    async def verify_otp(self, email: EmailStr, input_code: str):
        await self._verify_otp_core(email, input_code)
        await self.user_repo.mark_email_verified(email)
        return { "message": "OTP verified successfully" }


    # Verify OTP for password reset — returns a short-lived reset token
    async def verify_reset_otp(self, email: EmailStr, input_code: str):
        await self._verify_otp_core(email, input_code)

        # Issue a short-lived token scoped exclusively to password reset
        access_token = create_access_token(
            data={"email": email, "purpose": "password_reset"},
            expires_delta=timedelta(minutes=10)
        )

        return {
            "message": "OTP verified successfully. You can now reset your password.",
            "access_token": access_token
        }


    # Reset password
    async def reset_password(self, email: EmailStr, password: str):
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )

        user = await self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        hashed_password = hash_password(password)
        await self.user_repo.update_user_password(user.id, hashed_password)

        return { "message": "Password reset successfully" }