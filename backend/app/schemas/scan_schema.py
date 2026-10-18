from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.modules.iam.models import IAMUser, IAMRole, IAMGroup, IAMControlFinding
from app.modules.s3.models import S3Bucket
from app.modules.aws_lambda.models import LambdaFunction, LambdaLayer
from app.models.enums import ScanMode

class ScanBase(BaseModel):
    scan_name: str
    environment_id: UUID
    mode: ScanMode

class ScanCreate(ScanBase):
    model_id: str
    pass

class ScanResponse(BaseModel):
    id: UUID
    scan_name: str = Field(alias="scanName")
    environment_id: UUID = Field(alias="environmentId")
    environment_name: str = Field(alias="environmentName")
    mode: ScanMode
    status: str
    created_at: datetime = Field(alias="createdAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ScanResultResponse(BaseModel):
    iam_users: List[IAMUser]
    iam_roles: List[IAMRole]
    iam_groups: List[IAMGroup]
    iam_controls: List[IAMControlFinding] = Field(default_factory=list)
    s3_buckets: List[S3Bucket]
    lambda_functions: List[LambdaFunction]
    lambda_layers: List[LambdaLayer]

    model_config = ConfigDict(
        from_attributes=True
    )