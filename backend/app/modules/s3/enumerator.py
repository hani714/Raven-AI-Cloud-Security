"""
Main S3 Enumerator
Orchestrates all S3 enumeration operations with concurrent processing
"""

import asyncio
import logging
from datetime import datetime
import boto3

from .buckets import BucketEnumerator
from .models import S3Bucket, S3EnumerationResult
from .objects import ObjectEnumerator


logger = logging.getLogger(__name__)


class S3Enumerator:
    def __init__(self, session: boto3.Session = None, max_workers: int = 5):
        self.session = session
        self.max_workers = max_workers

        self.bucket_enumerator = BucketEnumerator(self.session)
        self.object_enumerator = ObjectEnumerator(self.session)

        self.all_errors = []
        self.all_permissions_checked = []

    async def _collect_errors_and_permissions(self) -> None:
        self.all_errors.extend(self.bucket_enumerator.errors)
        self.all_errors.extend(self.object_enumerator.errors)

        self.all_permissions_checked.extend(self.bucket_enumerator.permissions_checked)
        self.all_permissions_checked.extend(self.object_enumerator.permissions_checked)

    async def _enumerate_single_bucket(
        self,
        scan_id: str,
        bucket_name: str,
        enumerate_objects: bool,
        max_objects_per_bucket: int,
        detailed_object_enum: bool,
    ) -> S3Bucket:
        bucket = await self.bucket_enumerator.enumerate_bucket(
            scan_id, bucket_name, enumerate_objects, max_objects_per_bucket
        )

        if bucket and detailed_object_enum and bucket.objects:
            object_keys = [obj.key for obj in bucket.objects[:10]]
            detailed_objects = await self.object_enumerator.enumerate_objects_detailed(bucket_name, object_keys)
            if detailed_objects:
                bucket.objects = detailed_objects + bucket.objects[len(detailed_objects):]

        return bucket

    async def enumerate_all(
        self,
        scan_id: str,
        enumerate_objects: bool = True,
        max_objects_per_bucket: int = 100,
        detailed_object_enum: bool = False,
    ) -> S3EnumerationResult:
        logger.info("Starting comprehensive S3 enumeration...")
        start_time = datetime.utcnow()

        current_user = await self.bucket_enumerator.get_current_user()
        account_id = await self.bucket_enumerator.get_account_id()

        bucket_names = await self.bucket_enumerator.list_all_buckets()
        
        if not bucket_names:
            logger.info("No buckets found or access denied")
            buckets = []
        else:
            logger.info(f"Found {len(bucket_names)} buckets, enumerating concurrently...")
            # Create concurrent tasks for all buckets
            tasks = [
                self._enumerate_single_bucket(
                    scan_id,
                    bucket_name,
                    enumerate_objects,
                    max_objects_per_bucket,
                    detailed_object_enum,
                )
                for bucket_name in bucket_names
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            buckets = []
            for bucket_name, result in zip(bucket_names, results):
                if isinstance(result, Exception):
                    logger.error(f"Error enumerating bucket {bucket_name}: {result}")
                elif result:
                    buckets.append(result)
                    logger.info(f"Enumerated bucket: {bucket_name} ({result.object_count} objects)")
                else:
                    logger.warning(f"Failed to enumerate bucket: {bucket_name}")

        await self._collect_errors_and_permissions()

        total_buckets = len(buckets)
        total_objects = sum(bucket.object_count for bucket in buckets)
        total_size = sum(bucket.total_size for bucket in buckets)

        end_time = datetime.utcnow()
        enumeration_time = (end_time - start_time).total_seconds()

        logger.info(f"S3 enumeration completed in {enumeration_time:.2f} seconds")
        logger.info(f"Found: {total_buckets} buckets, {total_objects} objects, {total_size} bytes")
        logger.info(f"Encountered {len(self.all_errors)} errors during enumeration")

        return S3EnumerationResult(
            account_id=account_id,
            current_user=current_user,
            buckets=buckets,
            enumeration_time=end_time.isoformat(),
            total_buckets=total_buckets,
            total_objects=total_objects,
            total_size=total_size,
            errors=self.all_errors,
            permissions_checked=self.all_permissions_checked,
        )