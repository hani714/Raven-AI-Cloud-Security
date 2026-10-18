from typing import List, Optional

from .base import BaseIAMEnumerator
from .models import IAMUser


class UserEnumerator(BaseIAMEnumerator):
    async def list_all_users(self, exclude_users: List[str] = None) -> List[str]:
        exclude_users = exclude_users or ['cloudgoat']
        
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.list_users()
            return [
                user['UserName'] for user in response.get('Users', [])
                if user['UserName'] not in exclude_users
            ]
        except Exception as e:
            self._handle_error("list_users", e)
            return []

    async def get_user_access_keys(self, username: str) -> List[dict]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.list_access_keys(UserName=username)
            return [
                {
                    'access_key_id': key['AccessKeyId'],
                    'status': key['Status'],
                    'create_date': key['CreateDate'].isoformat() if key.get('CreateDate') else None
                }
                for key in response.get('AccessKeyMetadata', [])
            ]
        except Exception as e:
            self._handle_error("get_user_access_keys", e, username)
            return []

    async def get_user_groups(self, username: str) -> List[str]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.list_groups_for_user(UserName=username)
            return [group['GroupName'] for group in response.get('Groups', [])]
        except Exception as e:
            self._handle_error("get_user_groups", e, username)
            return []

    async def enumerate_user(self, scan_id, username: str) -> Optional[IAMUser]:
        try:
            # Get basic user info
            async with self.aiosession.client('iam') as iam:
                user_response = await iam.get_user(UserName=username)
            user_data = user_response['User']
            
            # Get managed policies with versions
            managed_policies = await self._get_managed_policies_with_versions('user', username)
            
            # Get inline policies
            inline_policies = await self._get_inline_policies('user', username)
            
            # Get groups
            groups = await self.get_user_groups(username)
            
            # Get access keys
            access_keys = await self.get_user_access_keys(username)
            
            # Get tags
            tags = await self._get_tags('user', username)
            
            return IAMUser(
                username=user_data['UserName'],
                user_id=user_data['UserId'],
                arn=user_data['Arn'],
                path=user_data['Path'],
                create_date=user_data['CreateDate'].isoformat() if user_data.get('CreateDate') else None,
                managed_policies=managed_policies,
                inline_policies=inline_policies,
                groups=groups,
                tags=tags,
                access_keys=access_keys,
                scan_id=scan_id
            )
            
        except Exception as e:
            self._handle_error("enumerate_user", e, username)
            return None

    async def enumerate_all_users(self, scan_id, exclude_users: List[str] = None) -> List[IAMUser]:
        users = []
        user_names = await self.list_all_users(exclude_users)
        
        for username in user_names:
            user = await self.enumerate_user(scan_id, username)
            if user:
                users.append(user)
        
        return users