import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError

from .exceptions import CredentialsError
from credentials import aws_credentials


logger = logging.getLogger(__name__)


class BaseIAMEnumerator:
    def __init__(self, session=None):
        self.session = session or aws_credentials.create_session()
        self.aiosession = self._build_aioboto3_session(self.session)
        self.errors = []
        self.permissions_checked = []

    def _build_aioboto3_session(self, session) -> aioboto3.Session:
        creds = session.get_credentials() if session else None
        frozen = creds.get_frozen_credentials() if creds else None
        return aioboto3.Session(
            aws_access_key_id=frozen.access_key if frozen else None,
            aws_secret_access_key=frozen.secret_key if frozen else None,
            aws_session_token=frozen.token if frozen else None,
            region_name=session.region_name if session else None,
        )

    async def _validate_credentials(self) -> None:
        try:
            async with self.aiosession.client('sts') as sts:
                await sts.get_caller_identity()
        except NoCredentialsError:
            raise CredentialsError("No valid AWS credentials found")
        except ClientError as e:
            raise CredentialsError(f"Invalid AWS credentials: {e}")

    def _handle_error(self, operation: str, error: Exception, context: str = "") -> None:
        error_msg = f"Error in {operation}: {str(error)}"
        if context:
            error_msg += f" (Context: {context})"
        
        logger.error(error_msg)
        self.errors.append({
            "operation": operation,
            "error": str(error),
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def _check_permission(self, action: str, resource: str = "*") -> bool:
        try:
            async with self.aiosession.client('sts') as sts:
                caller_identity = await sts.get_caller_identity()
            arn = caller_identity['Arn']
            async with self.aiosession.client('iam') as iam:
                response = await iam.simulate_principal_policy(
                    PolicySourceArn=arn,
                    ActionNames=[action],
                    ResourceArns=[resource]
                )
            
            result = response['EvaluationResults'][0]['EvalDecision'] == 'allowed'
            self.permissions_checked.append(f"{action}:{resource}:{result}")
            return result
            
        except Exception as e:
            self._handle_error("permission_check", e, f"{action} on {resource}")
            return False

    async def get_account_id(self) -> str:
        try:
            async with self.aiosession.client('sts') as sts:
                response = await sts.get_caller_identity()
            return response['Account']
        except Exception as e:
            self._handle_error("get_account_id", e)
            return "unknown"

    async def get_current_user(self) -> Optional[str]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.get_user()
            return response['User']['UserName']
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # User might be using a role
                try:
                    async with self.aiosession.client('sts') as sts:
                        caller_identity = await sts.get_caller_identity()
                    arn = caller_identity['Arn']
                    if ':assumed-role/' in arn:
                        return arn.split('/')[-2]  # Role name
                    return None
                except Exception:
                    return None
            self._handle_error("get_current_user", e)
            return None

    async def _get_policy_version_document(self, policy_arn: str, version_id: str) -> Dict[str, Any]:
        try:
            async with self.aiosession.client('iam') as iam:
                response = await iam.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=version_id
                )
            return response['PolicyVersion']['Document']
        except Exception as e:
            self._handle_error("get_policy_version", e, policy_arn)
            return {}

    async def _get_managed_policies_with_versions(self, resource_type: str, resource_name: str) -> List[Dict[str, Any]]:
        managed_policies = []
        
        try:
            # Get list of attached policies
            async with self.aiosession.client('iam') as iam:
                if resource_type == 'user':
                    response = await iam.list_attached_user_policies(UserName=resource_name)
                elif resource_type == 'role':
                    response = await iam.list_attached_role_policies(RoleName=resource_name)
                elif resource_type == 'group':
                    response = await iam.list_attached_group_policies(GroupName=resource_name)
                else:
                    raise ValueError(f"Invalid resource type: {resource_type}")
            
            for policy in response.get('AttachedPolicies', []):
                # Get policy versions
                async with self.aiosession.client('iam') as iam:
                    versions_response = await iam.list_policy_versions(PolicyArn=policy['PolicyArn'])
                policy_versions = []
                
                for version in versions_response['Versions']:
                    policy_doc = await self._get_policy_version_document(
                        policy['PolicyArn'], 
                        version['VersionId']
                    )
                    policy_versions.append({
                        'version_id': version['VersionId'],
                        'is_default': version['IsDefaultVersion'],
                        'document': policy_doc,
                        'create_date': version['CreateDate'].isoformat() if version.get('CreateDate') else None
                    })
                
                managed_policies.append({
                    'policy_name': policy['PolicyName'],
                    'policy_arn': policy['PolicyArn'],
                    'versions': policy_versions
                })
                
        except Exception as e:
            self._handle_error(f"get_{resource_type}_managed_policies", e, resource_name)
            
        return managed_policies

    async def _get_inline_policies(self, resource_type: str, resource_name: str) -> List[Dict[str, Any]]:
        inline_policies = []
        
        try:
            # Get list of inline policy names
            async with self.aiosession.client('iam') as iam:
                if resource_type == 'user':
                    response = await iam.list_user_policies(UserName=resource_name)
                elif resource_type == 'role':
                    response = await iam.list_role_policies(RoleName=resource_name)
                elif resource_type == 'group':
                    response = await iam.list_group_policies(GroupName=resource_name)
                else:
                    raise ValueError(f"Invalid resource type: {resource_type}")
            
            for policy_name in response.get('PolicyNames', []):
                async with self.aiosession.client('iam') as iam:
                    if resource_type == 'user':
                        policy_doc_response = await iam.get_user_policy(UserName=resource_name, PolicyName=policy_name)
                    elif resource_type == 'role':
                        policy_doc_response = await iam.get_role_policy(RoleName=resource_name, PolicyName=policy_name)
                    else:
                        policy_doc_response = await iam.get_group_policy(GroupName=resource_name, PolicyName=policy_name)
                inline_policies.append({
                    'policy_name': policy_name,
                    'document': policy_doc_response['PolicyDocument']
                })
                
        except Exception as e:
            self._handle_error(f"get_{resource_type}_inline_policies", e, resource_name)
            
        return inline_policies

    async def _get_tags(self, resource_type: str, resource_name: str) -> List[Dict[str, str]]:
        try:
            async with self.aiosession.client('iam') as iam:
                if resource_type == 'user':
                    response = await iam.list_user_tags(UserName=resource_name)
                elif resource_type == 'role':
                    response = await iam.list_role_tags(RoleName=resource_name)
                else:
                    raise ValueError(f"Invalid resource type: {resource_type}")
            
            return response.get('Tags', [])
            
        except Exception as e:
            self._handle_error(f"get_{resource_type}_tags", e, resource_name)
            return []