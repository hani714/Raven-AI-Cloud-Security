import logging
from datetime import datetime
from typing import Dict, Optional

import aioboto3
from botocore.exceptions import ClientError, NoCredentialsError

from .exceptions import S3CredentialsError, S3PermissionError
from credentials import aws_credentials


logger = logging.getLogger(__name__)


class BaseS3Enumerator:
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
            raise S3CredentialsError("No valid AWS credentials found")
        except ClientError as e:
            raise S3CredentialsError(f"Invalid AWS credentials: {e}")

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
            
            # Note: simulate_principal_policy is IAM, not available for S3 directly
            # This is a placeholder - in real scenarios, you'd test permissions by trying the action
            self.permissions_checked.append(f"{action}:{resource}:unknown")
            return True  # Assume true for now, will be tested during actual operations
            
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
            async with self.aiosession.client('sts') as sts:
                caller_identity = await sts.get_caller_identity()
            arn = caller_identity['Arn']
            
            # Extract user/role name from ARN
            if ':user/' in arn:
                return arn.split(':user/')[-1]
            elif ':assumed-role/' in arn:
                return arn.split('/')[-2]  # Role name
            elif ':root' in arn:
                return "root"
            return arn.split('/')[-1]  # Fallback
            
        except Exception as e:
            self._handle_error("get_current_user", e)
            return None

    async def _safe_api_call(self, operation: str, client, method_name: str, context: str = "", **kwargs) -> Optional[Dict]:
        try:
            method = getattr(client, method_name)
            response = await method(**kwargs)
            return response
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code in ['NoSuchBucket', 'NoSuchKey', 'NotFound']:
                self._handle_error(operation, S3PermissionError(f"Resource not found: {error_code}"), context)
            elif error_code in ['AccessDenied', 'Forbidden']:
                self._handle_error(operation, S3PermissionError(f"Access denied: {error_code}"), context)
            elif error_code == 'NoSuchBucketPolicy':
                return None
            elif error_code == 'NoSuchWebsiteConfiguration':
                return None
            elif error_code == 'NoSuchCORSConfiguration':
                return None
            elif error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                return None
            elif error_code == 'ReplicationConfigurationNotFoundError':
                return None
            elif error_code == 'NoSuchLifecycleConfiguration':
                return None
            elif error_code == 'NotificationConfigurationNotFoundError':
                return None
            else:
                self._handle_error(operation, e, context)
            return None
        except Exception as e:
            self._handle_error(operation, e, context)
            return None