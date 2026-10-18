# Secure Authentication (FastAPI + OTP + JWT)

This document explains the complete authentication design, with a strong focus on security controls and implementation details.

## What This Auth System Covers

1. User registration with hashed password storage
2. Email OTP verification with anti-abuse controls
3. Login gated by email verification
4. Password reset using OTP + short-lived purpose-scoped token
5. Logout with JWT revocation (token blacklist)

## Security Goals

The flow is designed to prevent:

1. Unauthorized login before email ownership is verified
2. OTP brute-force and OTP resend spam
3. Reset-token misuse outside password reset flow
4. Continued use of access tokens after logout

## High-Level Flow

1. Register: create user (`verified=False`)
2. Send OTP: `POST /auth/otp/send`
3. Verify OTP: `POST /auth/otp/verify` -> marks user verified
4. Login: `POST /auth/login` -> JWT only for verified users
5. Forgot password:
   1. `POST /auth/otp/send`
   2. `POST /auth/verify-reset` -> short-lived token (`purpose=password_reset`)
   3. `POST /auth/reset-password` with reset token
6. Logout: `POST /auth/logout` -> token added to blacklist

## Core Endpoints

```python
# backend/app/routers/auth_router.py

@router.post("/register")
def register(request: UserRegister, service: AuthService):
    return service.register(request)

@router.post("/login")
def login(request: UserLogin, service: AuthService):
    return service.login(request)

@router.post("/otp/send")
async def send_otp(request: OTPRequest, service: AuthService, background_tasks: BackgroundTasks):
    return service.send_otp(email=request.email, background_tasks=background_tasks)

@router.post("/otp/verify")
def verify_otp(request: OTPVerifyRequest, service: AuthService):
    return service.verify_otp(email=request.email, input_code=request.code)

@router.post("/verify-reset")
def forgot_password(request: OTPVerifyRequest, service: AuthService):
    return service.verify_reset_otp(email=request.email, input_code=request.code)

@router.post("/reset-password")
def reset_password(request: PasswordResetRequest, user: PasswordResetUser, service: AuthService):
    return service.reset_password(email=user, password=request.new_password)

@router.post("/logout")
def logout(block_token: BlockToken):
    return {"message": "Logout successful"}
```

## Request Validation

```python
# backend/app/schemas/user_schema.py
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str = Field(alias="confirmPassword")

# backend/app/schemas/otp_schema.py
class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str

class PasswordResetRequest(BaseModel):
    new_password: str = Field(alias="newPassword")
```

## OTP Security Model

```python
# backend/app/otp/otp_manager.py
class OTPManager:
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    MAX_RESENDS = 3
    LOCKOUT_MINUTES = 15
    RATE_LIMIT_SECONDS = 60
```

Controls implemented:

1. Cryptographically secure OTP generation (`secrets`)
2. OTP hash storage (`SHA-256`) instead of plaintext
3. 10-minute OTP TTL
4. Resend rate limit (60s)
5. Max resend cap (3)
6. Max failed attempts (5) + temporary lockout (15m)

## Registration Logic

```python
def register(self, user: UserRegister) -> UserResponse:
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    is_valid, error_msg = validate_email_address(user.email)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    if self.user_repo.is_user_exists(user.email):
        raise HTTPException(status_code=400, detail="Account with this email already exists")

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Password and confirm password do not match")

    hashed_password = hash_password(user.password)
    return self.user_repo.create_user(user.email, hashed_password)
```

Security notes:

1. Password is never stored plaintext
2. User remains unverified until OTP verification succeeds

## OTP Send + Verify Logic

```python
def send_otp(self, email: EmailStr, background_tasks: BackgroundTasks) -> dict:
    if self.otp_repo.is_rate_limited(email):
        raise HTTPException(status_code=429, detail="Please wait before requesting another code")

    if self.otp_repo.is_locked(email):
        raise HTTPException(status_code=403, detail="Account locked temporarily")

    existing = self.otp_repo.get_otp(email)
    if existing and existing.resend_count >= OTPManager.MAX_RESENDS:
        raise HTTPException(status_code=429, detail="Maximum OTP requests exceeded")

    otp_code = OTPManager.generate_otp()
    code_hash = OTPManager.hash_otp(otp_code)
    self.otp_repo.create_or_update_otp(email, code_hash)

    background_tasks.add_task(self.email_service.send_email, email_data)
    return {"message": "OTP sent successfully"}
```

```python
def _verify_otp_core(self, email: EmailStr, input_code: str):
    if self.otp_repo.is_locked(email):
        raise HTTPException(status_code=403, detail="Account is temporarily locked")

    otp_record = self.otp_repo.get_otp(email)
    if not otp_record:
        raise HTTPException(status_code=404, detail="No OTP found for this email")

    if datetime.now(timezone.utc) > otp_record.expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired")

    if not OTPManager.verify_otp(input_code, otp_record.code_hash):
        self.otp_repo.increment_attempts(email)
        raise HTTPException(status_code=400, detail="Invalid OTP")

    self.otp_repo.mark_verified(email)
    self.otp_repo.delete_otp(email)
```

`verify_otp` uses this core and marks user email verified.

## Login Logic

```python
def login(self, user_data: UserLogin) -> TokenResponse:
    user = self.user_repo.get_user_by_email(user_data.email)

    if user and not user.verified:
        raise HTTPException(status_code=401, detail="Email address not verified")

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token(data={
        "sub": user.email,
        "user_id": str(user.id),
        "subscription": {...}
    })

    return {"access_token": access_token, "token_type": "bearer", "user": user}
```

Security behavior:

1. Unverified users are denied
2. Password verification uses Argon2 helper
3. JWT includes expiry claim (`exp`)

## Password Reset (Scoped Token)

```python
def verify_reset_otp(self, email: EmailStr, input_code: str):
    self._verify_otp_core(email, input_code)
    access_token = create_access_token(
        data={"email": email, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=10)
    )
    return {"message": "OTP verified", "access_token": access_token}
```

```python
def get_password_reset_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(credentials.credentials)
    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=401, detail="Invalid token purpose")
    return payload.get("email")
```

This prevents normal access tokens from being used to reset passwords.

## Logout + Token Revocation

```python
def block_token_logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> bool:
    token = credentials.credentials
    payload = decode_access_token(token)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    TokenBlacklistRepository(db).add_token(token, payload["user_id"], expires_at)
    return True
```

```python
def get_current_user(...):
    payload = decode_access_token(token)
    if TokenBlacklistRepository(db).is_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
```

This gives immediate logout invalidation, even for unexpired JWTs.


## Data Model Notes

### OTP Table

1. `email` (PK)
2. `code_hash`
3. `expires_at`
4. `last_sent_at`
5. `attempts`
6. `resend_count`
7. `verified`
8. `locked_until`
9. optional audit fields (`ip_address`, `user_agent`)

### Users Table

1. `email`
2. `password` (hashed)
3. `verified`

## Final Takeaway

This auth flow is a strong security baseline: verification-first onboarding, abuse-resistant OTP lifecycle, scoped password reset, and revocable JWT sessions. With secret management and a few operational hardening steps, it is production-ready for security-sensitive workloads.


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