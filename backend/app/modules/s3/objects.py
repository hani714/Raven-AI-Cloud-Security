from typing import List, Optional, Dict, Any

from .base import BaseS3Enumerator
from .models import S3Object


class ObjectEnumerator(BaseS3Enumerator):
    async def get_object_acl(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_object_acl",
                s3,
                "get_object_acl",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key
            )
        return response or {}

    async def get_object_tagging(self, bucket_name: str, object_key: str) -> List[Dict[str, str]]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_object_tagging",
                s3,
                "get_object_tagging",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key
            )
        return response.get('TagSet', []) if response else []

    async def head_object(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "head_object",
                s3,
                "head_object",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key
            )
        return response or {}

    async def get_object_attributes(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_object_attributes",
                s3,
                "get_object_attributes",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key,
                ObjectAttributes=[
                    'ETag', 'Checksum', 'ObjectParts', 'StorageClass', 'ObjectSize'
                ]
            )
        return response or {}

    async def get_object_legal_hold(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_object_legal_hold",
                s3,
                "get_object_legal_hold",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key
            )
        return response or {}

    async def get_object_retention(self, bucket_name: str, object_key: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_object_retention",
                s3,
                "get_object_retention",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Key=object_key
            )
        return response or {}

    async def list_object_versions(self, bucket_name: str, object_key: str) -> List[Dict[str, Any]]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "list_object_versions",
                s3,
                "list_object_versions",
                f"{bucket_name}/{object_key}",
                Bucket=bucket_name,
                Prefix=object_key
            )
        
        if not response:
            return []
            
        versions = []
        
        # Get versions
        for version in response.get('Versions', []):
            if version['Key'] == object_key:
                versions.append(version)
        
        # Get delete markers
        for delete_marker in response.get('DeleteMarkers', []):
            if delete_marker['Key'] == object_key:
                versions.append({**delete_marker, 'IsDeleteMarker': True})
        
        return versions

    async def enumerate_object_detailed(self, bucket_name: str, object_key: str) -> Optional[S3Object]:
        try:
            # Get basic object metadata
            head_response = await self.head_object(bucket_name, object_key)
            
            if not head_response:
                return None
            
            # Get ACL
            acl = await self.get_object_acl(bucket_name, object_key)
            
            # Get tags
            tags = await self.get_object_tagging(bucket_name, object_key)
            
            # Get advanced attributes (if available)
            attributes = await self.get_object_attributes(bucket_name, object_key)
            
            # Get legal hold and retention (for compliance)
            legal_hold = await self.get_object_legal_hold(bucket_name, object_key)
            retention = await self.get_object_retention(bucket_name, object_key)
            
            # Get versions (if versioning is enabled)
            versions = await self.list_object_versions(bucket_name, object_key)
            
            # Extract metadata
            metadata = head_response.get('Metadata', {})
            
            # Add compliance information to metadata
            if legal_hold:
                metadata['legal_hold'] = legal_hold
            if retention:
                metadata['retention'] = retention
            if versions:
                metadata['versions'] = versions
            if attributes:
                metadata['attributes'] = attributes
            
            return S3Object(
                key=object_key,
                size=head_response.get('ContentLength', 0),
                last_modified=head_response.get('LastModified').isoformat() if head_response.get('LastModified') else None,
                etag=head_response.get('ETag', '').strip('"'),
                storage_class=head_response.get('StorageClass', 'STANDARD'),
                acl=acl,
                tags=tags,
                metadata=metadata,
                version_id=head_response.get('VersionId')
            )
            
        except Exception as e:
            self._handle_error("enumerate_object_detailed", e, f"{bucket_name}/{object_key}")
            return None

    async def enumerate_objects_detailed(self, bucket_name: str, object_keys: List[str]) -> List[S3Object]:
        objects = []
        
        for object_key in object_keys:
            obj = await self.enumerate_object_detailed(bucket_name, object_key)
            if obj:
                objects.append(obj)
        
        return objects