from fastapi import Depends
from typing import Annotated

import redis.asyncio as redis
from app.redis import get_redis
from .auth_dependencies import get_current_user, get_password_reset_user, block_token_logout
from .service_dependencies import get_scan_service, get_environment_service, get_genai_service, get_auth_service, get_dashboard_service, get_payment_service, get_subscription_service, get_byok_service

# Import classes with private prefix to avoid name collision
from app.schemas import CurrentUser as _CurrentUser
from app.service import ScanService as _ScanService
from app.service import GenAIService as _GenAIService
from app.service import EnvironmentService as _EnvironmentService
from app.service import AuthService as _AuthService
from app.service import DashboardService as _DashboardService
from app.service import PaymentService as _PaymentService
from app.service import SubscriptionService as _SubscriptionService
from app.service import BYOKService as _BYOKService

# Annotated types for dependency injection
Redis = Annotated[redis.Redis, Depends(get_redis)]
CurrentUser = Annotated[_CurrentUser, Depends(get_current_user)]
PasswordResetUser = Annotated[str, Depends(get_password_reset_user)]
BlockToken = Annotated[bool, Depends(block_token_logout)]
DashboardService = Annotated[_DashboardService, Depends(get_dashboard_service)]
ScanService = Annotated[_ScanService, Depends(get_scan_service)]
BYOKService = Annotated[_BYOKService, Depends(get_byok_service)]
EnvService = Annotated[_EnvironmentService, Depends(get_environment_service)]
PaymentService = Annotated[_PaymentService, Depends(get_payment_service)]
GenAIService = Annotated[_GenAIService, Depends(get_genai_service)]
SubscriptionService = Annotated[_SubscriptionService, Depends(get_subscription_service)]
AuthService = Annotated[_AuthService, Depends(get_auth_service)]