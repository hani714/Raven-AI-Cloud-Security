"""
Lambda Function Enumerator
Handles enumeration of Lambda functions and their configurations
"""

import json
import logging
from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError

from .base import BaseLambdaEnumerator
from .models import LambdaFunction, LambdaEventSourceMapping, LambdaAlias

logger = logging.getLogger(__name__)


class FunctionEnumerator(BaseLambdaEnumerator):
    """Handles enumeration of Lambda functions and their configurations"""
    
    async def list_all_functions(self) -> List[str]:
        """Get list of all Lambda function names"""
        try:
            async with self.aiosession.client('lambda') as lambda_client:
                functions = await self._paginate_results(
                    lambda_client, 'list_functions', 'Functions', 'list_functions'
                )
            return [func['FunctionName'] for func in functions]
        except Exception as e:
            self._handle_error("list_functions", e)
            return []
    
    async def get_function_configuration(self, function_name: str) -> Dict[str, Any]:
        """Get function configuration"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_function_configuration",
                lambda_client,
                "get_function_configuration",
                function_name,
                FunctionName=function_name
            )
        return response or {}
    
    async def get_function_code(self, function_name: str) -> Dict[str, Any]:
        """Get function code information"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_function",
                lambda_client,
                "get_function",
                function_name,
                FunctionName=function_name
            )
        return response or {}
    
    async def get_function_policy(self, function_name: str) -> Dict[str, Any]:
        """Get function resource policy"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_policy",
                lambda_client,
                "get_policy",
                function_name,
                FunctionName=function_name
            )
        
        if response and 'Policy' in response:
            try:
                return json.loads(response['Policy'])
            except json.JSONDecodeError:
                return {"raw_policy": response['Policy']}
        return {}
    
    async def list_function_aliases(self, function_name: str) -> List[Dict[str, Any]]:
        """List aliases for a function"""
        async with self.aiosession.client('lambda') as lambda_client:
            return await self._paginate_results(
                lambda_client, 'list_aliases', 'Aliases', 'list_aliases',
                FunctionName=function_name
            )
    
    async def list_function_versions(self, function_name: str) -> List[Dict[str, Any]]:
        """List versions for a function"""
        async with self.aiosession.client('lambda') as lambda_client:
            return await self._paginate_results(
                lambda_client, 'list_versions_by_function', 'Versions', 'list_versions_by_function',
                FunctionName=function_name
            )
    
    async def list_function_event_source_mappings(self, function_name: str) -> List[Dict[str, Any]]:
        """List event source mappings for a function"""
        async with self.aiosession.client('lambda') as lambda_client:
            return await self._paginate_results(
                lambda_client, 'list_event_source_mappings', 'EventSourceMappings', 'list_event_source_mappings',
                FunctionName=function_name
            )
    
    async def list_function_event_invoke_configs(self, function_name: str) -> List[Dict[str, Any]]:
        """List event invoke configurations for a function"""
        async with self.aiosession.client('lambda') as lambda_client:
            return await self._paginate_results(
                lambda_client, 'list_function_event_invoke_configs', 'FunctionEventInvokeConfigs', 'list_function_event_invoke_configs',
                FunctionName=function_name
            )
    
    async def get_function_concurrency(self, function_name: str) -> Dict[str, Any]:
        """Get function concurrency configuration"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_provisioned_concurrency_config",
                lambda_client,
                "get_provisioned_concurrency_config",
                function_name,
                FunctionName=function_name
            )
        return response or {}
    
    async def get_function_code_signing_config(self, function_name: str) -> Dict[str, Any]:
        """Get function code signing configuration"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "get_function_code_signing_config",
                lambda_client,
                "get_function_code_signing_config",
                function_name,
                FunctionName=function_name
            )
        return response or {}
    
    async def list_function_tags(self, function_arn: str) -> List[Dict[str, str]]:
        """Get function tags"""
        async with self.aiosession.client('lambda') as lambda_client:
            response = await self._safe_api_call(
                "list_tags",
                lambda_client,
                "list_tags",
                function_arn,
                Resource=function_arn
            )
        
        if response and 'Tags' in response:
            # Convert to list of key-value pairs
            return [{"Key": k, "Value": v} for k, v in response['Tags'].items()]
        return []
    
    async def enumerate_function(self, scan_id, function_name: str, get_detailed_config: bool = True) -> Optional[LambdaFunction]:
        """
        Get complete details for a specific Lambda function
        
        Args:
            function_name: The Lambda function name to enumerate
            get_detailed_config: Whether to get detailed configurations (slower)
            
        Returns:
            LambdaFunction object or None if enumeration fails
        """
        try:
            # Get basic function information
            func_response = await self.get_function_code(function_name)
            
            if not func_response:
                logger.warning(f"Could not get function details for {function_name}")
                return None
            
            # Extract configuration and code info
            config = func_response.get('Configuration', {})
            code_info = func_response.get('Code', {})
            
            # Create base function object
            lambda_function = LambdaFunction(
                scan_id=scan_id,
                function_name=config.get('FunctionName', function_name),
                function_arn=config.get('FunctionArn', ''),
                runtime=config.get('Runtime'),
                role=config.get('Role'),
                handler=config.get('Handler'),
                code_size=config.get('CodeSize'),
                description=config.get('Description'),
                timeout=config.get('Timeout'),
                memory_size=config.get('MemorySize'),
                last_modified=config.get('LastModified'),
                code_sha256=config.get('CodeSha256'),
                version=config.get('Version'),
                environment=config.get('Environment', {}),
                dead_letter_config=config.get('DeadLetterConfig', {}),
                kms_key_arn=config.get('KMSKeyArn'),
                tracing_config=config.get('TracingConfig', {}),
                vpc_config=config.get('VpcConfig', {}),
                layers=config.get('Layers', []),
                state=config.get('State'),
                state_reason=config.get('StateReason'),
                state_reason_code=config.get('StateReasonCode'),
                last_update_status=config.get('LastUpdateStatus'),
                last_update_status_reason=config.get('LastUpdateStatusReason'),
                last_update_status_reason_code=config.get('LastUpdateStatusReasonCode'),
                package_type=config.get('PackageType'),
                architectures=config.get('Architectures', []),
                ephemeral_storage=config.get('EphemeralStorage', {}),
                image_config=config.get('ImageConfig', {}),
                code_signing_config_arn=config.get('CodeSigningConfigArn'),
                signing_profile_version_arn=config.get('SigningProfileVersionArn'),
                signing_job_arn=config.get('SigningJobArn'),
                reserved_concurrent_executions=config.get('ReservedConcurrentExecutions')
            )
            
            # Get detailed configurations if requested
            if get_detailed_config:
                try:
                    # Get function policy
                    policy = await self.get_function_policy(function_name)
                    lambda_function.policy = policy
                    
                    # Get aliases
                    aliases = await self.list_function_aliases(function_name)
                    lambda_function.aliases = aliases
                    
                    # Get versions (limit to avoid too much data)
                    versions = await self.list_function_versions(function_name)
                    lambda_function.versions = versions[:10]  # Limit to latest 10 versions
                    
                    # Get event source mappings
                    event_mappings = await self.list_function_event_source_mappings(function_name)
                    lambda_function.event_source_mappings = event_mappings
                    
                    # Get event invoke configurations
                    invoke_configs = await self.list_function_event_invoke_configs(function_name)
                    lambda_function.event_invoke_configs = invoke_configs
                    
                    # Get concurrency configuration
                    concurrency_config = await self.get_function_concurrency(function_name)
                    lambda_function.concurrency_config = concurrency_config
                    
                    # Get code signing configuration
                    code_signing_config = await self.get_function_code_signing_config(function_name)
                    if code_signing_config:
                        lambda_function.code_signing_config_arn = code_signing_config.get('CodeSigningConfigArn')
                    
                    # Get tags
                    if lambda_function.function_arn:
                        tags = await self.list_function_tags(lambda_function.function_arn)
                        lambda_function.tags = tags
                        
                except Exception as e:
                    logger.warning(f"Could not get detailed config for {function_name}: {str(e)}")
            
            return lambda_function
            
        except Exception as e:
            self._handle_error("enumerate_function", e, function_name)
            return None
    
    async def enumerate_all_functions(self, scan_id, get_detailed_config: bool = True) -> List[LambdaFunction]:
        """
        Enumerate all Lambda functions
        
        Args:
            get_detailed_config: Whether to get detailed configurations for each function
            
        Returns:
            List of LambdaFunction objects
        """
        functions = []
        function_names = await self.list_all_functions()
        
        logger.info(f"Found {len(function_names)} Lambda functions to enumerate")
        
        for function_name in function_names:
            try:
                function = await self.enumerate_function(scan_id, function_name, get_detailed_config)
                if function:
                    functions.append(function)
                    logger.debug(f"Successfully enumerated function: {function_name}")
                else:
                    logger.warning(f"Failed to enumerate function: {function_name}")
                    
            except Exception as e:
                logger.error(f"Error enumerating function {function_name}: {str(e)}")
                continue
        
        logger.info(f"Successfully enumerated {len(functions)} Lambda functions")
        return functions
    
    async def get_function_basic_info(self, function_name: str) -> Optional[Dict[str, Any]]:
        """
        Get basic function information without detailed configs (faster)
        
        Args:
            function_name: The Lambda function name
            
        Returns:
            Basic function info dict or None
        """
        try:
            config = await self.get_function_configuration(function_name)
            return config
        except Exception as e:
            logger.warning(f"Could not get basic info for function {function_name}: {str(e)}")
            return None