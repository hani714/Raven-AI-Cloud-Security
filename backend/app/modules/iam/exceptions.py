import time
from typing import Optional, Dict, Any


class IAMEnumerationError(Exception):
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class CredentialsError(IAMEnumerationError):
    def __init__(self, message: str, credential_type: Optional[str] = None):
        super().__init__(message, error_code="CREDENTIALS_ERROR")
        self.credential_type = credential_type

    def __str__(self):
        if self.credential_type:
            return f"Credentials Error ({self.credential_type}): {self.message}"
        return f"Credentials Error: {self.message}"


class PermissionError(IAMEnumerationError):
    def __init__(
        self, message: str, required_permission: Optional[str] = None, resource_arn: Optional[str] = None
    ):
        super().__init__(message, error_code="ACCESS_DENIED")
        self.required_permission = required_permission
        self.resource_arn = resource_arn

    def __str__(self):
        base_msg = f"Permission Denied: {self.message}"
        if self.required_permission:
            base_msg += f" (Required: {self.required_permission})"
        if self.resource_arn:
            base_msg += f" (Resource: {self.resource_arn})"
        return base_msg


class ResourceNotFoundError(IAMEnumerationError):
    def __init__(
        self, message: str, resource_type: Optional[str] = None, resource_name: Optional[str] = None
    ):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_name = resource_name

    def __str__(self):
        base_msg = f"Resource Not Found: {self.message}"
        if self.resource_type and self.resource_name:
            base_msg += f" ({self.resource_type}: {self.resource_name})"
        return base_msg


class RateLimitError(IAMEnumerationError):
    def __init__(
        self, message: str, retry_after: Optional[int] = None, operation: Optional[str] = None
    ):
        super().__init__(message, error_code="RATE_LIMITED")
        self.retry_after = retry_after
        self.operation = operation

    def __str__(self):
        base_msg = f"Rate Limited: {self.message}"
        if self.operation:
            base_msg += f" (Operation: {self.operation})"
        if self.retry_after:
            base_msg += f" (Retry after: {self.retry_after}s)"
        return base_msg

    def get_retry_delay(self) -> int:
        """Get suggested retry delay in seconds"""
        return self.retry_after or 1


class PolicyParsingError(IAMEnumerationError):
    def __init__(
        self, message: str, policy_name: Optional[str] = None, policy_arn: Optional[str] = None
    ):
        super().__init__(message, error_code="POLICY_PARSING_ERROR")
        self.policy_name = policy_name
        self.policy_arn = policy_arn

    def __str__(self):
        base_msg = f"Policy Parsing Error: {self.message}"
        if self.policy_name:
            base_msg += f" (Policy: {self.policy_name})"
        return base_msg


class ServiceUnavailableError(IAMEnumerationError):
    def __init__(self, message: str, service_name: str = "IAM"):
        super().__init__(message, error_code="SERVICE_UNAVAILABLE")
        self.service_name = service_name

    def __str__(self):
        return f"Service Unavailable ({self.service_name}): {self.message}"