"""
Lambda Custom Exceptions
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone


class LambdaEnumerationError(Exception):
    """Base exception for Lambda enumeration errors"""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 resource: Optional[str] = None, error_code: Optional[str] = None,
                 original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.operation = operation
        self.resource = resource
        self.error_code = error_code
        self.original_error = original_error
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/reporting"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "operation": self.operation,
            "resource": self.resource,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "original_error": str(self.original_error) if self.original_error else None
        }


class LambdaCredentialsError(LambdaEnumerationError):
    """Exception raised when Lambda credentials are invalid or insufficient"""
    
    def __init__(self, message: str = "Invalid or insufficient AWS credentials for Lambda access", 
                 credential_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.credential_type = credential_type
        
        # Add specific credential guidance
        if not message.endswith('.'):
            message += '.'
        
        suggestions = [
            "Verify AWS credentials are configured correctly",
            "Check if credentials have Lambda permissions",
            "Ensure credentials are not expired"
        ]
        
        if credential_type == "access_key":
            suggestions.append("Verify AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        elif credential_type == "role":
            suggestions.append("Check IAM role trust policy and permissions")
        
        self.suggestions = suggestions
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if hasattr(self, 'suggestions'):
            return f"{base_msg}\nSuggestions:\n" + "\n".join(f"- {s}" for s in self.suggestions)
        return base_msg


class LambdaPermissionError(LambdaEnumerationError):
    """Exception raised when Lambda operations fail due to insufficient permissions"""
    
    def __init__(self, message: str, action: Optional[str] = None, 
                 function_name: Optional[str] = None, layer_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.action = action
        self.function_name = function_name
        self.layer_name = layer_name
        
        # Generate required permissions suggestion
        self.required_permissions = self._get_required_permissions(action)
    
    def _get_required_permissions(self, action: Optional[str]) -> list:
        """Get list of required permissions for the action"""
        permission_map = {
            "list_functions": ["lambda:ListFunctions"],
            "get_function": ["lambda:GetFunction"],
            "get_function_configuration": ["lambda:GetFunctionConfiguration"],
            "get_function_code_signing_config": ["lambda:GetFunctionCodeSigningConfig"],
            "get_function_concurrency": ["lambda:GetProvisionedConcurrencyConfig"],
            "get_function_event_invoke_config": ["lambda:GetFunctionEventInvokeConfig"],
            "list_aliases": ["lambda:ListAliases"],
            "list_versions_by_function": ["lambda:ListVersionsByFunction"],
            "list_event_source_mappings": ["lambda:ListEventSourceMappings"],
            "list_function_event_invoke_configs": ["lambda:ListFunctionEventInvokeConfigs"],
            "get_policy": ["lambda:GetPolicy"],
            "list_layers": ["lambda:ListLayers"],
            "list_layer_versions": ["lambda:ListLayerVersions"],
            "get_layer_version": ["lambda:GetLayerVersion"],
            "get_layer_version_policy": ["lambda:GetLayerVersionPolicy"],
        }
        
        if action and action in permission_map:
            return permission_map[action]
        
        return ["lambda:*"] if action else []
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        
        details = []
        if self.action:
            details.append(f"Action: {self.action}")
        if self.function_name:
            details.append(f"Function: {self.function_name}")
        if self.layer_name:
            details.append(f"Layer: {self.layer_name}")
        if self.required_permissions:
            details.append(f"Required permissions: {', '.join(self.required_permissions)}")
        
        if details:
            return f"{base_msg}\nDetails:\n" + "\n".join(f"- {d}" for d in details)
        
        return base_msg


class LambdaResourceNotFoundError(LambdaEnumerationError):
    """Exception raised when Lambda resources are not found"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type
        self.resource_name = resource_name
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        
        if self.resource_type and self.resource_name:
            return f"{base_msg} (Resource: {self.resource_type}/{self.resource_name})"
        elif self.resource_type:
            return f"{base_msg} (Type: {self.resource_type})"
        
        return base_msg
    
    @classmethod
    def function_not_found(cls, function_name: str, **kwargs):
        """Create exception for function not found"""
        return cls(
            f"Lambda function '{function_name}' not found or access denied",
            resource_type="function",
            resource_name=function_name,
            **kwargs
        )
    
    @classmethod
    def layer_not_found(cls, layer_name: str, version: Optional[int] = None, **kwargs):
        """Create exception for layer not found"""
        resource_name = f"{layer_name}:{version}" if version else layer_name
        return cls(
            f"Lambda layer '{resource_name}' not found or access denied",
            resource_type="layer",
            resource_name=resource_name,
            **kwargs
        )


class LambdaRateLimitError(LambdaEnumerationError):
    """Exception raised when Lambda API rate limits are exceeded"""
    
    def __init__(self, message: str = "Lambda API rate limit exceeded", 
                 retry_after: Optional[int] = None, request_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.request_id = request_id
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        
        details = []
        if self.retry_after:
            details.append(f"Retry after: {self.retry_after} seconds")
        if self.request_id:
            details.append(f"Request ID: {self.request_id}")
        
        recommendations = [
            "Reduce concurrent requests",
            "Implement exponential backoff",
            "Consider request rate optimization"
        ]
        
        if details or recommendations:
            result = base_msg
            if details:
                result += f"\nDetails:\n" + "\n".join(f"- {d}" for d in details)
            result += f"\nRecommendations:\n" + "\n".join(f"- {r}" for r in recommendations)
            return result
        
        return base_msg
    
    @classmethod
    def from_aws_error(cls, aws_error, **kwargs):
        """Create LambdaRateLimitError from AWS ClientError"""
        retry_after = None
        request_id = None
        
        if hasattr(aws_error, 'response'):
            # Extract retry-after from headers if available
            headers = aws_error.response.get('ResponseMetadata', {}).get('HTTPHeaders', {})
            retry_after = headers.get('retry-after') or headers.get('Retry-After')
            request_id = aws_error.response.get('ResponseMetadata', {}).get('RequestId')
        
        return cls(
            f"Lambda rate limit exceeded: {str(aws_error)}",
            retry_after=int(retry_after) if retry_after else None,
            request_id=request_id,
            original_error=aws_error,
            **kwargs
        )


class LambdaConfigurationError(LambdaEnumerationError):
    """Exception raised when Lambda configuration is invalid or misconfigured"""
    
    def __init__(self, message: str, config_type: Optional[str] = None, 
                 config_value: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_type = config_type
        self.config_value = config_value
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        
        if self.config_type:
            base_msg += f" (Configuration: {self.config_type}"
            if self.config_value:
                base_msg += f" = {self.config_value}"
            base_msg += ")"
        
        return base_msg