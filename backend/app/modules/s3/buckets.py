from typing import List, Optional, Dict, Any
from botocore.exceptions import ClientError

from .base import BaseS3Enumerator
from .models import S3Bucket, S3Object


class BucketEnumerator(BaseS3Enumerator):
    async def list_all_buckets(self) -> List[str]:
        try:
            async with self.aiosession.client('s3') as s3:
                response = await s3.list_buckets()
            return [bucket['Name'] for bucket in response.get('Buckets', [])]
        except Exception as e:
            self._handle_error("list_buckets", e)
            return []

    async def get_bucket_location(self, bucket_name: str) -> Optional[str]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_location",
                s3,
                "get_bucket_location",
                bucket_name,
                Bucket=bucket_name
            )
        if response:
            # AWS returns None for us-east-1
            location = response.get('LocationConstraint')
            return location if location else 'us-east-1'
        return None

    async def get_bucket_acl(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_acl",
                s3,
                "get_bucket_acl",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_policy",
                s3,
                "get_bucket_policy",
                bucket_name,
                Bucket=bucket_name
            )
        if response and 'Policy' in response:
            import json
            try:
                return json.loads(response['Policy'])
            except json.JSONDecodeError:
                return {"raw_policy": response['Policy']}
        return {}

    async def get_bucket_policy_status(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_policy_status",
                s3,
                "get_bucket_policy_status",
                bucket_name,
                Bucket=bucket_name
            )
        return response.get('PolicyStatus', {}) if response else {}

    async def get_public_access_block(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_public_access_block",
                s3,
                "get_public_access_block",
                bucket_name,
                Bucket=bucket_name
            )
        return response.get('PublicAccessBlockConfiguration', {}) if response else {}

    async def get_bucket_website(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_website",
                s3,
                "get_bucket_website",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_cors(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_cors",
                s3,
                "get_bucket_cors",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_encryption",
                s3,
                "get_bucket_encryption",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_versioning(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_versioning",
                s3,
                "get_bucket_versioning",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_replication(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_replication",
                s3,
                "get_bucket_replication",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_logging(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_logging",
                s3,
                "get_bucket_logging",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_lifecycle_configuration(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_lifecycle_configuration",
                s3,
                "get_bucket_lifecycle_configuration",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_notification_configuration(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_notification_configuration",
                s3,
                "get_bucket_notification_configuration",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_tagging(self, bucket_name: str) -> List[Dict[str, str]]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_tagging",
                s3,
                "get_bucket_tagging",
                bucket_name,
                Bucket=bucket_name
            )
        return response.get('TagSet', []) if response else []

    async def get_bucket_accelerate_configuration(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_accelerate_configuration",
                s3,
                "get_bucket_accelerate_configuration",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def get_bucket_request_payment(self, bucket_name: str) -> Dict[str, Any]:
        async with self.aiosession.client('s3') as s3:
            response = await self._safe_api_call(
                "get_bucket_request_payment",
                s3,
                "get_bucket_request_payment",
                bucket_name,
                Bucket=bucket_name
            )
        return response or {}

    async def list_bucket_objects(self, bucket_name: str, max_objects: int = 1000) -> List[Dict[str, Any]]:
        objects = []
        continuation_token = None
        
        async with self.aiosession.client('s3') as s3:
            while len(objects) < max_objects:
                kwargs = {
                    'Bucket': bucket_name,
                    'MaxKeys': min(1000, max_objects - len(objects))
                }
                if continuation_token:
                    kwargs['ContinuationToken'] = continuation_token
                    
                response = await self._safe_api_call(
                    "list_objects_v2",
                    s3,
                    "list_objects_v2",
                    bucket_name,
                    **kwargs
                )
                
                if not response:
                    break
                    
                batch_objects = response.get('Contents', [])
                objects.extend(batch_objects)
                
                if not response.get('IsTruncated', False):
                    break
                    
                continuation_token = response.get('NextContinuationToken')
                if not continuation_token:
                    break
        
        return objects[:max_objects]

    async def enumerate_bucket(self, scan_id: str, bucket_name: str, enumerate_objects: bool = True, max_objects: int = 100) -> Optional[S3Bucket]:
        try:
            # Get bucket creation date from list_buckets (if available)
            creation_date = None
            async with self.aiosession.client('s3') as s3:
                buckets_response = await s3.list_buckets()
            for bucket in buckets_response.get('Buckets', []):
                if bucket['Name'] == bucket_name:
                    creation_date = bucket['CreationDate'].isoformat() if bucket.get('CreationDate') else None
                    break

            # Get all bucket configurations
            region = await self.get_bucket_location(bucket_name)
            acl = await self.get_bucket_acl(bucket_name)
            policy = await self.get_bucket_policy(bucket_name)
            policy_status = await self.get_bucket_policy_status(bucket_name)
            public_access_block = await self.get_public_access_block(bucket_name)
            website_config = await self.get_bucket_website(bucket_name)
            cors_config = await self.get_bucket_cors(bucket_name)
            encryption_config = await self.get_bucket_encryption(bucket_name)
            versioning_config = await self.get_bucket_versioning(bucket_name)
            replication_config = await self.get_bucket_replication(bucket_name)
            logging_config = await self.get_bucket_logging(bucket_name)
            lifecycle_config = await self.get_bucket_lifecycle_configuration(bucket_name)
            notification_config = await self.get_bucket_notification_configuration(bucket_name)
            tagging = await self.get_bucket_tagging(bucket_name)
            accelerate_config = await self.get_bucket_accelerate_configuration(bucket_name)
            request_payment_config = await self.get_bucket_request_payment(bucket_name)

            # Initialize objects list
            objects = []
            object_count = 0
            total_size = 0

            # Enumerate objects if requested
            if enumerate_objects:
                raw_objects = await self.list_bucket_objects(bucket_name, max_objects)
                object_count = len(raw_objects)
                
                # Calculate total size
                total_size = sum(obj.get('Size', 0) for obj in raw_objects)
                
                # Convert to S3Object models (basic info only for performance)
                for obj in raw_objects:
                    s3_object = S3Object(
                        key=obj['Key'],
                        size=obj.get('Size', 0),
                        last_modified=obj.get('LastModified').isoformat() if obj.get('LastModified') else None,
                        etag=obj.get('ETag', '').strip('"'),
                        storage_class=obj.get('StorageClass', 'STANDARD')
                    )
                    objects.append(s3_object)

            return S3Bucket(
                name=bucket_name,
                scan_id=scan_id,
                creation_date=creation_date,
                region=region,
                acl=acl,
                policy=policy,
                policy_status=policy_status,
                public_access_block=public_access_block,
                website_config=website_config,
                cors_config=cors_config,
                encryption_config=encryption_config,
                versioning_config=versioning_config,
                replication_config=replication_config,
                logging_config=logging_config,
                lifecycle_config=lifecycle_config,
                notification_config=notification_config,
                tagging=tagging,
                objects=objects,
                object_count=object_count,
                total_size=total_size
            )
            
        except Exception as e:
            self._handle_error("enumerate_bucket", e, bucket_name)
            return None

    async def enumerate_all_buckets(self, enumerate_objects: bool = True, max_objects_per_bucket: int = 100) -> List[S3Bucket]:
        buckets = []
        bucket_names = await self.list_all_buckets()
        
        for bucket_name in bucket_names:
            bucket = await self.enumerate_bucket(bucket_name, enumerate_objects, max_objects_per_bucket)
            if bucket:
                buckets.append(bucket)
        
        return buckets