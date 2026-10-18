from typing import List, Optional

from .base import BaseIAMEnumerator
from .models import IAMGroup


class GroupEnumerator(BaseIAMEnumerator):
    async def list_all_groups(self) -> List[str]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.list_groups()
            return [group['GroupName'] for group in response.get('Groups', [])]
        except Exception as e:
            self._handle_error("list_groups", e)
            return []

    async def enumerate_group(self, scan_id, group_name: str) -> Optional[IAMGroup]:
        try:
            # Get basic group info
            async with self.aiosession.client('iam') as iam:
                group_response = await iam.get_group(GroupName=group_name)
            group_data = group_response['Group']
            members = [user['UserName'] for user in group_response.get('Users', [])]

            # Get managed policies with versions
            managed_policies = await self._get_managed_policies_with_versions('group', group_name)

            # Get inline policies
            inline_policies = await self._get_inline_policies('group', group_name)

            return IAMGroup(
                group_name=group_data['GroupName'],
                group_id=group_data['GroupId'],
                arn=group_data['Arn'],
                path=group_data['Path'],
                create_date=group_data['CreateDate'].isoformat() if group_data.get('CreateDate') else None,
                managed_policies=managed_policies,
                inline_policies=inline_policies,
                members=members,
                scan_id=scan_id
            )
        except Exception as e:
            self._handle_error("enumerate_group", e, group_name)
            return None

    async def enumerate_all_groups(self, scan_id) -> List[IAMGroup]:
        groups = []
        group_names = await self.list_all_groups()
        
        for group_name in group_names:
            group = await self.enumerate_group(scan_id, group_name)
            if group:
                groups.append(group)
        
        return groups