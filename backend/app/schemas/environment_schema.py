from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from app.dto import EnvironmentCreateDTO

class EnvironmentCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    access_key: str = Field(..., alias="accessKey")
    secret_access_key: str = Field(..., alias="secretAccessKey")
    region: Optional[str] = "us-east-1"  # Default region if not provided

    def to_dto(self) -> EnvironmentCreateDTO:
        return EnvironmentCreateDTO(
            name=self.name,
            access_key=self.access_key,
            secret_access_key=self.secret_access_key,
            region=self.region
        )

class EnvironmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )
    
    id: UUID
    name: str
    access_key: str = Field(..., serialization_alias="accessKey")
    secret_access_key: str = Field(..., serialization_alias="secretAccessKey")
    region: Optional[str] = Field(default="us-east-1", serialization_alias="region")
    user_id: UUID = Field(..., serialization_alias="userId")
