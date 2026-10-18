from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ByokKeyCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    provider: str
    model: str
    api_key: str = Field(..., alias="apiKey")
    label: Optional[str] = None


class ByokKeyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    provider: str
    model: str
    model_id: UUID = Field(..., alias="modelId")
    label: Optional[str] = None
    key_preview: str = Field(..., alias="keyPreview")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")


class ByokProviderOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    label: str
    default_model: str = Field("", alias="defaultModel")


class ByokProviderModelOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    value: str
    label: str
    is_default: bool = Field(False, alias="isDefault")
