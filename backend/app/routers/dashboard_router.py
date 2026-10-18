from fastapi import APIRouter, status
from typing import Optional

from app.schemas import AttackPathSummary, UserActivity
from app.utils.dependency import CurrentUser, DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/last-pentest", response_model=Optional[AttackPathSummary], status_code=status.HTTP_200_OK)
async def get_last_pentest(current_user: CurrentUser, service: DashboardService):
    return await service.last_pentest(current_user.id)

@router.get("/vuln-summary", response_model = None, status_code=status.HTTP_200_OK)
async def get_vulnerability_summary(current_user: CurrentUser, service: DashboardService):
    return await service.vulnerability_summary(current_user.id)

@router.get("/activity", response_model = UserActivity, status_code=status.HTTP_200_OK)
async def scan_activity(current_user: CurrentUser, service: DashboardService):
    return await service.scan_activity(current_user)