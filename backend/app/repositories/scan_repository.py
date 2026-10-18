from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

class ScanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: str):
        result = await self.db.execute(
            select(models.Scans)
            .options(selectinload(models.Scans.environment))
            .join(models.Environments, models.Scans.environment_id == models.Environments.id)
            .where(models.Environments.user_id == user_id)
            .order_by(models.Scans.created_at.desc())
        )
        return result.scalars().all()

    # Fetch only scan IDs for a user
    async def get_scan_ids(self, user_id: str):
        result = await self.db.execute(
            select(models.Scans.id)
            .join(models.Environments, models.Scans.environment_id == models.Environments.id)
            .where(models.Environments.user_id == user_id)
            .order_by(models.Scans.created_at.desc())
        )
        return result.scalars().all()

    # Get scan by ID with user ID for validation
    async def get_scan_by_id(self, scan_id: uuid.UUID, user_id: str):
        result = await self.db.execute(
            select(models.Scans)
            .join(models.Environments, models.Scans.environment_id == models.Environments.id)
            .where(models.Scans.id == scan_id, models.Environments.user_id == user_id)
        )
        return result.scalar_one_or_none()

    # Get scan by ID with user ID for validation
    async def get_latest_scan_id(self, user_id: str):
        latest_scan = await self.db.execute(
            select(models.Scans.id)
            .join(models.Environments, models.Scans.environment_id == models.Environments.id)
            .where(models.Environments.user_id == user_id)
            .order_by(models.Scans.created_at.desc())
            .limit(1)
        )

        return latest_scan.scalar_one_or_none()

    async def create(self, scan_data: schemas.ScanCreate, status: str):
        result = await self.db.execute(
            select(models.Environments)
            .where(models.Environments.id == scan_data.environment_id)
        )

        environment = result.scalar_one_or_none()

        if not environment:
            raise ValueError("Environment not found for scan creation")

        new_scan = models.Scans(
            id=uuid.uuid7(),
            scan_name=scan_data.scan_name,
            environment_id=environment.id,
            status=status,
            mode=scan_data.mode,
        )
        # Keep relationship loaded for response serialization that reads environment_name.
        new_scan.environment = environment
        self.db.add(new_scan)
        await self.db.commit()
        return new_scan
    
    # Validate if scan exists by scan_id
    async def get_by_scan_id(self, scan_id: uuid.UUID):
        result = await self.db.execute(
                select(models.Scans.id.label("scan_id"),
                       models.Environments.user_id.label("user_id"))
                .join(models.Environments, models.Scans.environment_id == models.Environments.id)
                .where(models.Scans.id == scan_id)
            )
        
        record = result.first()
        
        if record:
            return {"scan_id": record.scan_id, "user_id": record.user_id}
        
        return None
    
    async def update_status(self, scan_id: uuid.UUID, status: str):
        try:
            result  = await self.db.execute(
                    select(models.Scans)
                    .where(models.Scans.id == scan_id)
                )
            
            scan = result.scalar_one_or_none()
            
            if not scan:
                return None
            
            scan.status = status
            
            await self.db.commit()
            
            return scan
            
        except Exception as e:
            await self.db.rollback()
            raise