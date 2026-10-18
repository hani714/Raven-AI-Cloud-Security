from typing import Optional
from dataclasses import dataclass

@dataclass(frozen=True)
class EnvironmentCreateDTO:
    name: str
    access_key: str
    secret_access_key: str
    region: Optional[str]
