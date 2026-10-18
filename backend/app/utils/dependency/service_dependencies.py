from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgre import get_db

# Dependency to get ScanService instance
async def get_scan_service(db: AsyncSession = Depends(get_db)) -> ScanService:
    from app.service import ScanService
    return ScanService(db)

# Dependency to get EnvironmentService instance
async def get_environment_service(db: AsyncSession = Depends(get_db)) -> EnvironmentService:
    from app.service import EnvironmentService
    return EnvironmentService(db)

# Dependency to get GenAIService instance
async def get_genai_service(db: AsyncSession = Depends(get_db)) -> GenAIService:
    from app.service import GenAIService
    return GenAIService(db)

# Dependency to get AuthService instance
async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    from app.service import AuthService
    return AuthService(db)

# Dependency to get DashboardService instance
async def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    from app.service import DashboardService
    return DashboardService(db)

# Dependency to get PaymentService instance
async def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    from app.service import PaymentService
    return PaymentService(db)

# Dependency to get SubscriptionService instance
async def get_subscription_service(db: AsyncSession = Depends(get_db)) -> SubscriptionService:
    from app.service import SubscriptionService
    return SubscriptionService(db)

# Dependency to get BYOKService instance
async def get_byok_service(db: AsyncSession = Depends(get_db)) -> BYOKService:
    from app.service import BYOKService
    return BYOKService(db)