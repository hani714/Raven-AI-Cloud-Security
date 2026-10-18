import logging
import asyncio
import time
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import ScanRepository, EnvironmentRepository, UserRepository, SubscriptionsRepository
from app.schemas import CurrentUser
from app.models.enums import ScanMode
from app.modules import Enumerator
from .genai_service import GenAIService
from app.database.mongodb import get_by_scan_id
from app.mappers.scan_results_mapper import ScanResultMapper
from app.utils import collections, get_cached, set_cached
from app.monitoring.metrics import (
    scans_total,
    active_scans,
    scan_duration_seconds,
    aws_resources_discovered
)

logger = logging.getLogger(__name__)

class ScanService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.genai_service = GenAIService(db)
        self.scan_repo = ScanRepository(db)
        self.user_repo = UserRepository(db)
        self.env_repo = EnvironmentRepository(db)
        self.sub_repo = SubscriptionsRepository(db)
        self.enum = Enumerator(db)
        self.srm = ScanResultMapper()

    @staticmethod
    def _extract_service_result(results: dict, service_name: str):
        service_payload = results.get(service_name) or {}
        if isinstance(service_payload, dict):
            return service_payload.get("result")
        return None


    # Get scans by user ID
    async def get_scans_by_user(self, user_id: str):
        return await self.scan_repo.get_by_user(user_id)


    # Create a new scan
    async def create_scan(self, scan_data, current_user: CurrentUser):
        active_scans.inc()
        start_time = time.time()
        scan = None
        
        try:
            sub = await self.sub_repo.get_subscription_by_user(current_user.id)
            if sub.current_scans_per_month >= current_user.max_scans_per_month:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Scan limit reached for the current subscription."
                )
            
            # Ensure environment belongs to this user
            environment = await self.env_repo.get_by_id(scan_data.environment_id)
            if not environment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Environment not found",
                )
            if str(environment.user_id) != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized access to environment",
                )
            
            # Create scan with selected mode and 'running' status.
            scan = await self.scan_repo.create(scan_data, status="running")

            # Enumeration always runs first and produces normalized scan artifacts.
            results = await self.enum.run_enumeration(scan.id, environment)
            
            # Track discovered resources
            iam_result = self._extract_service_result(results, 'iam')
            if iam_result:
                if getattr(iam_result, 'users', None):
                    aws_resources_discovered.labels(service='iam', resource_type='users').inc(len(iam_result.users))
                if getattr(iam_result, 'roles', None):
                    aws_resources_discovered.labels(service='iam', resource_type='roles').inc(len(iam_result.roles))
                if getattr(iam_result, 'groups', None):
                    aws_resources_discovered.labels(service='iam', resource_type='groups').inc(len(iam_result.groups))

            s3_result = self._extract_service_result(results, 's3')
            if s3_result and getattr(s3_result, 'buckets', None):
                aws_resources_discovered.labels(service='s3', resource_type='buckets').inc(len(s3_result.buckets))

            lambda_result = self._extract_service_result(results, 'lambda')
            if lambda_result and getattr(lambda_result, 'functions', None):
                aws_resources_discovered.labels(service='lambda', resource_type='functions').inc(len(lambda_result.functions))
            
            # Analysis mode includes GenAI attack path generation on top of enumeration output.
            if scan_data.mode == ScanMode.analysis:
                scan_results = await self.get_scan_results(str(scan.id), current_user.id)
                await self.genai_service.attack_path(str(scan.id), str(scan_data.model_id), current_user, scan_results)

            # Mark scan as completed only if everything succeeded
            await self.scan_repo.update_status(scan.id, "completed")
            await self.user_repo.increment_scans_per_month(current_user.id)
            scans_total.labels(status='completed').inc()

            return scan
            
        except Exception as e:
            # Mark scan as failed if it was created
            if scan:
                await self.scan_repo.update_status(scan.id, "failed")
            
            scans_total.labels(status='failed').inc()
            logger.error(f"Scan creation failed: {str(e)}")
            raise
        finally:
            duration = time.time() - start_time
            scan_duration_seconds.labels(scan_type=scan_data.mode.value).observe(duration)
            active_scans.dec()


    async def get_scan_results(self, scan_id: str, user_id: str, cache=None) -> dict:
        scan = await self.scan_repo.get_by_scan_id(scan_id)
        if not scan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
        if str(scan["user_id"]) != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access to scan results")

        cache_key = f"scan_results:{scan_id}"

        if cached := await get_cached(cache, cache_key):
            return cached

        mon_collections = collections()
        results_list = await asyncio.gather(*[get_by_scan_id(col, scan_id) for col in mon_collections])
        results = dict(zip(mon_collections, results_list))

        data = {
            "iam_users":        [self.srm.document_to_iam_user(doc)        for doc in results["iam_users"]],
            "iam_roles":        [self.srm.document_to_iam_role(doc)        for doc in results["iam_roles"]],
            "iam_groups":       [self.srm.document_to_iam_group(doc)       for doc in results["iam_groups"]],
            "iam_controls":     [self.srm.document_to_iam_control(doc)     for doc in results["iam_controls"]],
            "s3_buckets":       [self.srm.document_to_s3_bucket(doc)       for doc in results["s3_buckets"]],
            "lambda_functions": [self.srm.document_to_lambda_function(doc) for doc in results["lambda_functions"]],
            "lambda_layers":    [self.srm.document_to_lambda_layer(doc)    for doc in results["lambda_layers"]],
        }

        encoded_data = jsonable_encoder(data)
        await set_cached(cache, cache_key, encoded_data)
        return encoded_data