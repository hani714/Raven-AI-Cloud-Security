from typing import List, Optional

from .base import BaseIAMEnumerator
from .models import IAMRole


class RoleEnumerator(BaseIAMEnumerator):
    async def list_all_roles(self, exclude_service_roles: bool = True) -> List[str]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.list_roles()
            roles = response.get('Roles', [])
            
            if exclude_service_roles:
                # Filter out AWS service roles
                roles = [
                    role for role in roles
                    if not role['Path'].startswith('/aws-service-role/') 
                    and not role['Path'].startswith('/service-role/')
                ]
            
            return [role['RoleName'] for role in roles]
            
        except Exception as e:
            self._handle_error("list_roles", e)
            return []

    async def enumerate_role(self, scan_id, role_name: str) -> Optional[IAMRole]:
        try:
            # Get basic role info
            async with self.aiosession.client('iam') as iam:
                role_response = await iam.get_role(RoleName=role_name)
            role_data = role_response['Role']
            
            # Get managed policies with versions
            managed_policies = await self._get_managed_policies_with_versions('role', role_name)
            
            # Get inline policies
            inline_policies = await self._get_inline_policies('role', role_name)
            
            # Get tags
            tags = await self._get_tags('role', role_name)
            
            return IAMRole(
                role_name=role_data['RoleName'],
                role_id=role_data['RoleId'],
                arn=role_data['Arn'],
                path=role_data['Path'],
                create_date=role_data['CreateDate'].isoformat() if role_data.get('CreateDate') else None,
                assume_role_policy=role_data['AssumeRolePolicyDocument'],
                managed_policies=managed_policies,
                inline_policies=inline_policies,
                tags=tags,
                scan_id=scan_id
            )
            
        except Exception as e:
            self._handle_error("enumerate_role", e, role_name)
            return None

    async def enumerate_all_roles(self, scan_id, exclude_service_roles: bool = True) -> List[IAMRole]:
        roles = []
        role_names = await self.list_all_roles(exclude_service_roles)
        
        for role_name in role_names:
            role = await self.enumerate_role(scan_id, role_name)
            if role:
                roles.append(role)
        
        return roles