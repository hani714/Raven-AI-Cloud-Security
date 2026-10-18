from pydantic import BaseModel, EmailStr, Field

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    code: str

class PasswordResetRequest(BaseModel):
    new_password: str = Field(alias="newPassword")