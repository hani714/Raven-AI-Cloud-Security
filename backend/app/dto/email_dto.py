from pydantic import BaseModel
from dataclasses import dataclass

class OTPEmailDTO(BaseModel):
    code: str
    expiry_minutes: int
    template_name: str = "otp.html"


@dataclass(frozen=True)
class EmailDTO:
    to: str
    subject: str
    html: str