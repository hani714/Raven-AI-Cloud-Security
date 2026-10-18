import asyncio
import logging
from datetime import datetime, timezone

import boto3

from .groups import GroupEnumerator
from .models import IAMEnumerationResult
from .roles import RoleEnumerator
from .users import UserEnumerator


logger = logging.getLogger(__name__)


class IAMEnumerator:
    def __init__(self, session: boto3.Session = None, max_workers: int = 10):
        self.session = session
        self.max_workers = max_workers

        self.user_enumerator = UserEnumerator(self.session)
        self.role_enumerator = RoleEnumerator(self.session)
        self.group_enumerator = GroupEnumerator(self.session)

        self.all_errors = []
        self.all_permissions_checked = []

    async def _collect_errors_and_permissions(self) -> None:
        self.all_errors.extend(self.user_enumerator.errors)
        self.all_errors.extend(self.role_enumerator.errors)
        self.all_errors.extend(self.group_enumerator.errors)

        self.all_permissions_checked.extend(self.user_enumerator.permissions_checked)
        self.all_permissions_checked.extend(self.role_enumerator.permissions_checked)
        self.all_permissions_checked.extend(self.group_enumerator.permissions_checked)

    async def _enumerate_concurrent(self, scan_id, exclude_users, exclude_service_roles):
        user_task = self.user_enumerator.enumerate_all_users(scan_id, exclude_users)
        role_task = self.role_enumerator.enumerate_all_roles(scan_id, exclude_service_roles)
        group_task = self.group_enumerator.enumerate_all_groups(scan_id)

        users, roles, groups = await asyncio.gather(user_task, role_task, group_task)
        logger.info(f"Enumerated {len(users)} users")
        logger.info(f"Enumerated {len(roles)} roles")
        logger.info(f"Enumerated {len(groups)} groups")
        return users, roles, groups

    async def enumerate_all(
        self,
        scan_id: str,
        exclude_users: list = None,
        exclude_service_roles: bool = True,
    ) -> IAMEnumerationResult:
        await self.user_enumerator._validate_credentials()
        current_user = await self.user_enumerator.get_current_user()
        users, roles, groups = await self._enumerate_concurrent(
            scan_id, exclude_users, exclude_service_roles
        )

        await self._collect_errors_and_permissions()
        end_time = datetime.now(timezone.utc)

        return IAMEnumerationResult(
            current_user=current_user,
            users=users,
            roles=roles,
            groups=groups,
            enumeration_time=end_time.isoformat(),
            errors=self.all_errors,
            permissions_checked=self.all_permissions_checked,
        )