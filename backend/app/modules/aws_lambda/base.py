import logging
from typing import Optional, Dict, Any, Callable
from botocore.exceptions import ClientError, NoCredentialsError

import aioboto3
from credentials import aws_credentials

from .exceptions import (
    LambdaEnumerationError,
    LambdaCredentialsError,
    LambdaPermissionError,
    LambdaResourceNotFoundError,
    LambdaRateLimitError,
    LambdaConfigurationError
)

logger = logging.getLogger(__name__)


class BaseLambdaEnumerator:
    def __init__(self, session=None):
        self.session = session or aws_credentials.create_session()
        self.aiosession = self._build_aioboto3_session(self.session)
        self.region = self.session.region_name or 'us-east-1'
        
        logger.info(f"Initialized Lambda enumerator for region: {self.region}")
    
    def _build_aioboto3_session(self, session) -> aioboto3.Session:
        creds = session.get_credentials() if session else None
        frozen = creds.get_frozen_credentials() if creds else None
        return aioboto3.Session(
            aws_access_key_id=frozen.access_key if frozen else None,
            aws_secret_access_key=frozen.secret_key if frozen else None,
            aws_session_token=frozen.token if frozen else None,
            region_name=session.region_name if session else None,
        )
    
    async def _safe_api_call(self, operation_name: str, client, method_name: str,
                      resource_identifier: Optional[str] = None, **kwargs) -> Optional[Dict[str, Any]]:
        try:
            logger.debug(f"Executing Lambda {operation_name}" + 
                        (f" for {resource_identifier}" if resource_identifier else ""))
            
            method = getattr(client, method_name)
            response = await method(**kwargs)
            
            logger.debug(f"Successfully executed {operation_name}")
            return response
            
        except NoCredentialsError as e:
            logger.error(f"No credentials available for {operation_name}")
            raise LambdaCredentialsError(
                f"No AWS credentials found for Lambda {operation_name}",
                operation=operation_name,
                resource=resource_identifier,
                original_error=e
            )
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            logger.warning(f"Lambda {operation_name} failed: {error_code} - {error_message}")
            
            # Handle specific error types
            if error_code in ['AccessDenied', 'UnauthorizedOperation', 'Forbidden']:
                raise LambdaPermissionError(
                    f"Access denied for Lambda {operation_name}: {error_message}",
                    action=operation_name,
                    function_name=resource_identifier if 'function' in operation_name.lower() else None,
                    layer_name=resource_identifier if 'layer' in operation_name.lower() else None,
                    operation=operation_name,
                    resource=resource_identifier,
                    error_code=error_code,
                    original_error=e
                )
                
            elif error_code in ['ResourceNotFoundException', 'FunctionNotFound', 'ResourceNotFound']:
                raise LambdaResourceNotFoundError(
                    f"Lambda resource not found for {operation_name}: {error_message}",
                    resource_type="function" if 'function' in operation_name.lower() else "layer",
                    resource_name=resource_identifier,
                    operation=operation_name,
                    resource=resource_identifier,
                    error_code=error_code,
                    original_error=e
                )
                
            elif error_code in ['TooManyRequestsException', 'Throttling', 'RequestLimitExceeded']:
                raise LambdaRateLimitError.from_aws_error(
                    e,
                    operation=operation_name,
                    resource=resource_identifier
                )
                
            elif error_code in ['InvalidParameterValue', 'InvalidParameter', 'ValidationException']:
                raise LambdaConfigurationError(
                    f"Invalid configuration for Lambda {operation_name}: {error_message}",
                    config_type=operation_name,
                    operation=operation_name,
                    resource=resource_identifier,
                    error_code=error_code,
                    original_error=e
                )
            
            # Handle specific Lambda error cases
            elif error_code == 'ResourceConflictException':
                logger.warning(f"Resource conflict for {operation_name}: {error_message}")
                return None
                
            elif error_code == 'ServiceException':
                logger.error(f"Lambda service error for {operation_name}: {error_message}")
                raise LambdaEnumerationError(
                    f"Lambda service error: {error_message}",
                    operation=operation_name,
                    resource=resource_identifier,
                    error_code=error_code,
                    original_error=e
                )
                
            elif error_code == 'KMSDisabledException':
                logger.warning(f"KMS key disabled for {operation_name}: {error_message}")
                return None
                
            elif error_code == 'KMSInvalidStateException':
                logger.warning(f"KMS key invalid state for {operation_name}: {error_message}")
                return None
                
            elif error_code == 'KMSAccessDeniedException':
                logger.warning(f"KMS access denied for {operation_name}: {error_message}")
                return None
                
            else:
                # Generic error handling
                logger.error(f"Unexpected error in {operation_name}: {error_code} - {error_message}")
                raise LambdaEnumerationError(
                    f"Unexpected Lambda API error: {error_message}",
                    operation=operation_name,
                    resource=resource_identifier,
                    error_code=error_code,
                    original_error=e
                )
                
        except Exception as e:
            logger.error(f"Unexpected exception in {operation_name}: {str(e)}")
            raise LambdaEnumerationError(
                f"Unexpected error during Lambda {operation_name}: {str(e)}",
                operation=operation_name,
                resource=resource_identifier,
                original_error=e
            )
    
    def _handle_error(self, operation: str, error: Exception, resource: Optional[str] = None):
        if isinstance(error, (LambdaEnumerationError, LambdaCredentialsError, 
                             LambdaPermissionError, LambdaResourceNotFoundError,
                             LambdaRateLimitError, LambdaConfigurationError)):
            # Re-raise our custom exceptions
            raise error
        else:
            # Wrap other exceptions
            logger.error(f"Error in {operation}: {str(error)}")
            raise LambdaEnumerationError(
                f"Error during {operation}: {str(error)}",
                operation=operation,
                resource=resource,
                original_error=error
            )
    
    async def _paginate_results(self, client, method_name: str, result_key: str, 
                         operation_name: str, **kwargs) -> list:
        results = []
        next_token = None
        
        while True:
            try:
                # Add pagination token if available
                if next_token:
                    kwargs['NextToken'] = next_token
                
                response = await self._safe_api_call(operation_name, client, method_name, **kwargs)
                
                if not response:
                    break
                
                # Add results from this page
                page_results = response.get(result_key, [])
                results.extend(page_results)
                
                # Check for next page
                next_token = response.get('NextToken')
                if not next_token:
                    break
                    
            except LambdaEnumerationError:
                # Stop pagination on errors but return what we have
                logger.warning(f"Pagination stopped due to error in {operation_name}")
                break
        
        return results
    
    def get_current_region(self) -> str:
        return self.region
    
    async def test_connectivity(self) -> bool:
        try:
            # Simple API call to test connectivity
            async with self.aiosession.client('lambda') as lambda_client:
                await lambda_client.list_functions(MaxItems=1)
            return True
        except Exception as e:
            logger.error(f"Lambda connectivity test failed: {str(e)}")
            return False