from typing import Optional, Dict, Any
from datetime import datetime, timezone


class S3EnumerationError(Exception):
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
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "operation": self.operation,
            "resource": self.resource,
            "error_code": self.error_code,
            "timestamp": self.timestamp,
            "original_error": str(self.original_error) if self.original_error else None
        }


class S3CredentialsError(S3EnumerationError):
    def __init__(self, message: str = "Invalid or insufficient AWS credentials for S3 access", 
                 credential_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.credential_type = credential_type
        
        # Add specific credential guidance
        if not message.endswith('.'):
            message += '.'
        
        suggestions = [
            "Verify AWS credentials are configured correctly",
            "Check if credentials have S3 permissions",
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


class S3PermissionError(S3EnumerationError):
    def __init__(self, message: str, action: Optional[str] = None, 
                 bucket: Optional[str] = None, object_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.action = action
        self.bucket = bucket
        self.object_key = object_key
        
        # Generate required permissions suggestion
        self.required_permissions = self._get_required_permissions(action)
    
    def _get_required_permissions(self, action: Optional[str]) -> list:
        permission_map = {
            "list_buckets": ["s3:ListAllMyBuckets"],
            "get_bucket_location": ["s3:GetBucketLocation"],
            "get_bucket_acl": ["s3:GetBucketAcl"],
            "get_bucket_policy": ["s3:GetBucketPolicy"],
            "list_objects": ["s3:ListBucket"],
            "get_object": ["s3:GetObject"],
            "get_object_acl": ["s3:GetObjectAcl"],
            "put_object": ["s3:PutObject"],
            "delete_object": ["s3:DeleteObject"],
        }
        
        if action and action in permission_map:
            return permission_map[action]
        
        return ["s3:*"] if action else []
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        
        details = []
        if self.action:
            details.append(f"Action: {self.action}")
        if self.bucket:
            details.append(f"Bucket: {self.bucket}")
        if self.object_key:
            details.append(f"Object: {self.object_key}")
        if self.required_permissions:
            details.append(f"Required permissions: {', '.join(self.required_permissions)}")
        
        if details:
            return f"{base_msg}\nDetails:\n" + "\n".join(f"- {d}" for d in details)
        
        return base_msg


class S3ResourceNotFoundError(S3EnumerationError):
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
    def bucket_not_found(cls, bucket_name: str, **kwargs):
        return cls(
            f"S3 bucket '{bucket_name}' not found or access denied",
            resource_type="bucket",
            resource_name=bucket_name,
            **kwargs
        )
    
    @classmethod
    def object_not_found(cls, bucket_name: str, object_key: str, **kwargs):
        return cls(
            f"S3 object '{object_key}' not found in bucket '{bucket_name}'",
            resource_type="object",
            resource_name=f"{bucket_name}/{object_key}",
            **kwargs
        )


class S3RateLimitError(S3EnumerationError):
    def __init__(self, message: str = "S3 API rate limit exceeded", 
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
        retry_after = None
        request_id = None
        
        if hasattr(aws_error, 'response'):
            # Extract retry-after from headers if available
            headers = aws_error.response.get('ResponseMetadata', {}).get('HTTPHeaders', {})
            retry_after = headers.get('retry-after') or headers.get('Retry-After')
            request_id = aws_error.response.get('ResponseMetadata', {}).get('RequestId')
        
        return cls(
            f"S3 rate limit exceeded: {str(aws_error)}",
            retry_after=int(retry_after) if retry_after else None,
            request_id=request_id,
            original_error=aws_error,
            **kwargs
        )


class S3ConfigurationError(S3EnumerationError):
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