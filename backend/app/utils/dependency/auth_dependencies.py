import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone

from app.schemas import CurrentUser
from app.models.enums import ScanDepth, AnalysisLevel
from app.utils import decode_access_token
from app.database.postgre import get_db
from app.repositories import UserRepository, TokenBlacklistRepository

# HTTP Bearer token scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)) -> CurrentUser:
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = decode_access_token(token)    
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )

    # Check if token has been blacklisted (logged out)
    if await TokenBlacklistRepository(db).is_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    user = await UserRepository(db).get_user(payload["user_id"])

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    subscription = payload.get("subscription")
    if not subscription:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return CurrentUser(
        id=payload["user_id"],
        email=payload["sub"],
        subscription_id=subscription["id"],
        subscription_name=subscription["name"],
        scan_depth=ScanDepth(subscription["scan_depth"]),
        analysis_level=AnalysisLevel(subscription["analysis_level"]),
        max_environments=subscription["max_environments"],
        max_scans_per_month=subscription["max_scans_per_month"]
    )


async def get_password_reset_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token purpose")

    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return email


async def block_token_logout(credentials: HTTPAuthorizationCredentials = Depends(security), db = Depends(get_db)) -> bool:
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    exp = payload.get("exp")
    if not exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has no expiry")

    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc).replace(tzinfo=None)

    await TokenBlacklistRepository(db).add_token(token, payload["user_id"], expires_at)

    return True