from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.repositories import ScanRepository, UserRepository
from app.database.mongodb import get_by_scan_id, get_vuln_summary
from app.schemas import AttackPathSummary, CurrentUser, UserActivity

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scan_repo = ScanRepository(db)
        self.user_repo = UserRepository(db)

    async def last_pentest(self, user_id: str) -> Optional[AttackPathSummary]:
        scan_id = await self.scan_repo.get_latest_scan_id(user_id)
        if not scan_id:
            return None

        doc = await get_by_scan_id("attack_analysis", scan_id)
        if not doc:
            return None

        return AttackPathSummary(**doc[0])

    async def vulnerability_summary(self, user_id: str):
        scans = await self.scan_repo.get_scan_ids(user_id)
        scan_ids = [str(scan_id) for scan_id in scans]
        return await get_vuln_summary("attack_analysis", scan_ids)
    
    async def scan_activity(self, current_user: CurrentUser):
        env_scans = await self.user_repo.get_scan_activity(current_user.id)

        return UserActivity(
            current_environments=env_scans.current_environments,
            current_scans_per_month=env_scans.current_scans_per_month,
            max_scans_per_month=current_user.max_scans_per_month,
            max_environments=current_user.max_environments,
            analysis_level=current_user.analysis_level,
        )
