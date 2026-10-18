from fastapi import APIRouter, BackgroundTasks, status

from app.utils.dependency import AuthService, PasswordResetUser, BlockToken
from app.schemas import UserResponse, UserRegister, UserLogin, TokenResponse, OTPRequest, OTPVerifyRequest, PasswordResetRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegister, service: AuthService):
    return await service.register(request)

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def login(request: UserLogin, service: AuthService):
    return await service.login(request)

@router.post("/otp/send", status_code=status.HTTP_200_OK)
async def send_otp(request: OTPRequest, service: AuthService, background_tasks: BackgroundTasks):
    return await service.send_otp(email=request.email, background_tasks=background_tasks)

@router.post("/otp/verify", status_code=status.HTTP_200_OK)
async def verify_otp(request: OTPVerifyRequest, service: AuthService):
    return await service.verify_otp(email=request.email, input_code=request.code)

@router.post("/verify-reset", status_code=status.HTTP_200_OK)
async def forgot_password(request: OTPVerifyRequest, service: AuthService):
    return await service.verify_reset_otp(email=request.email, input_code=request.code)

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: PasswordResetRequest, user: PasswordResetUser, service: AuthService):
    return await service.reset_password(email=user, password=request.new_password)

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(block_token: BlockToken):
    return {"message": "Logout successful"}