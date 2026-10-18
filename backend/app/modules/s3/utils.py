from typing import Dict, Any, List
from .models import S3EnumerationResult, S3Bucket, S3Object


class S3FormatConverter:
    @staticmethod
    def to_dict(result: S3EnumerationResult) -> Dict[str, Any]:
        return {
            "account_id": result.account_id,
            "current_user": result.current_user,
            "enumeration_time": result.enumeration_time,
            "total_buckets": result.total_buckets,
            "total_objects": result.total_objects,
            "total_size": result.total_size,
            "buckets": [S3FormatConverter._bucket_to_dict(bucket) for bucket in result.buckets],
            "errors": result.errors,
            "permissions_checked": result.permissions_checked
        }
    
    @staticmethod
    def _bucket_to_dict(bucket: S3Bucket) -> Dict[str, Any]:
        return {
            "name": bucket.name,
            "creation_date": bucket.creation_date,
            "region": bucket.region,
            "object_count": bucket.object_count,
            "total_size": bucket.total_size,
            "configurations": {
                "acl": bucket.acl,
                "policy": bucket.policy,
                "policy_status": bucket.policy_status,
                "public_access_block": bucket.public_access_block,
                "website_config": bucket.website_config,
                "cors_config": bucket.cors_config,
                "encryption_config": bucket.encryption_config,
                "versioning_config": bucket.versioning_config,
                "replication_config": bucket.replication_config,
                "logging_config": bucket.logging_config,
                "lifecycle_config": bucket.lifecycle_config,
                "notification_config": bucket.notification_config,
                "tagging": bucket.tagging
            },
            "objects": [S3FormatConverter._object_to_dict(obj) for obj in bucket.objects]
        }
    
    @staticmethod
    def _object_to_dict(obj: S3Object) -> Dict[str, Any]:
        return {
            "key": obj.key,
            "size": obj.size,
            "last_modified": obj.last_modified,
            "etag": obj.etag,
            "storage_class": obj.storage_class,
            "version_id": obj.version_id,
            "acl": obj.acl,
            "tags": obj.tags,
            "metadata": obj.metadata
        }
    
    @staticmethod
    def to_summary(result: S3EnumerationResult) -> Dict[str, Any]:
        bucket_summaries = []
        
        for bucket in result.buckets:
            # Identify potential security issues
            security_issues = S3FormatConverter._identify_security_issues(bucket)
            
            bucket_summaries.append({
                "name": bucket.name,
                "region": bucket.region,
                "object_count": bucket.object_count,
                "total_size": bucket.total_size,
                "is_public": S3FormatConverter._is_bucket_public(bucket),
                "has_policy": bool(bucket.policy),
                "has_website": bool(bucket.website_config),
                "has_cors": bool(bucket.cors_config),
                "versioning_enabled": bucket.versioning_config.get('Status') == 'Enabled',
                "encryption_enabled": bool(bucket.encryption_config),
                "security_issues": security_issues
            })
        
        return {
            "account_id": result.account_id,
            "current_user": result.current_user,
            "enumeration_time": result.enumeration_time,
            "summary": {
                "total_buckets": result.total_buckets,
                "total_objects": result.total_objects,
                "total_size": result.total_size,
                "public_buckets": sum(1 for bucket in bucket_summaries if bucket["is_public"]),
                "encrypted_buckets": sum(1 for bucket in bucket_summaries if bucket["encryption_enabled"]),
                "versioned_buckets": sum(1 for bucket in bucket_summaries if bucket["versioning_enabled"])
            },
            "buckets": bucket_summaries,
            "error_count": len(result.errors)
        }
    
    @staticmethod
    def _is_bucket_public(bucket: S3Bucket) -> bool:
        # Check public access block
        public_block = bucket.public_access_block
        if public_block:
            if not public_block.get('BlockPublicAcls', True):
                return True
            if not public_block.get('BlockPublicPolicy', True):
                return True
            if not public_block.get('IgnorePublicAcls', True):
                return True
            if not public_block.get('RestrictPublicBuckets', True):
                return True
        
        # Check policy status
        policy_status = bucket.policy_status
        if policy_status and policy_status.get('IsPublic', False):
            return True
        
        return False
    
    @staticmethod
    def _identify_security_issues(bucket: S3Bucket) -> List[str]:
        issues = []
        
        # Check if bucket is public
        if S3FormatConverter._is_bucket_public(bucket):
            issues.append("bucket_is_public")
        
        # Check for missing encryption
        if not bucket.encryption_config:
            issues.append("no_encryption")
        
        # Check for disabled versioning
        if bucket.versioning_config.get('Status') != 'Enabled':
            issues.append("versioning_disabled")
        
        # Check for missing logging
        if not bucket.logging_config.get('LoggingEnabled'):
            issues.append("no_access_logging")
        
        # Check for overly permissive CORS
        cors_rules = bucket.cors_config.get('CORSRules', [])
        for rule in cors_rules:
            if '*' in rule.get('AllowedOrigins', []):
                issues.append("permissive_cors")
                break
        
        # Check for website hosting (potential exposure)
        if bucket.website_config:
            issues.append("website_hosting_enabled")
        
        return issues


class S3SecurityAnalyzer:
    @staticmethod
    def analyze_bucket_security(bucket: S3Bucket) -> Dict[str, Any]:
        analysis = {
            "bucket_name": bucket.name,
            "risk_level": "low",
            "findings": [],
            "recommendations": []
        }
        
        # Analyze public access
        if S3FormatConverter._is_bucket_public(bucket):
            analysis["risk_level"] = "high"
            analysis["findings"].append({
                "severity": "high",
                "category": "public_access",
                "description": "Bucket allows public access",
                "details": bucket.public_access_block
            })
            analysis["recommendations"].append("Enable all public access block settings")
        
        # Analyze encryption
        if not bucket.encryption_config:
            if analysis["risk_level"] != "high":
                analysis["risk_level"] = "medium"
            analysis["findings"].append({
                "severity": "medium",
                "category": "encryption",
                "description": "Bucket encryption not configured",
                "details": None
            })
            analysis["recommendations"].append("Enable server-side encryption")
        
        # Analyze versioning
        if bucket.versioning_config.get('Status') != 'Enabled':
            analysis["findings"].append({
                "severity": "low",
                "category": "versioning",
                "description": "Object versioning not enabled",
                "details": bucket.versioning_config
            })
            analysis["recommendations"].append("Enable object versioning for data protection")
        
        # Analyze logging
        if not bucket.logging_config.get('LoggingEnabled'):
            analysis["findings"].append({
                "severity": "low",
                "category": "logging",
                "description": "Access logging not configured",
                "details": bucket.logging_config
            })
            analysis["recommendations"].append("Enable access logging for audit trail")
        
        return analysis