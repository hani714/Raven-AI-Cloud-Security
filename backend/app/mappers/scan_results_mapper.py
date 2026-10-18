from app.modules.iam.models import IAMUser, IAMRole, IAMGroup, IAMControlFinding
from app.modules.s3.models import S3Bucket, S3Object
from app.modules.aws_lambda.models import LambdaFunction, LambdaLayer

class ScanResultMapper:

    def document_to_iam_user(self, doc: dict) -> IAMUser:
        doc.pop("_id", None)
        
        return IAMUser(
            username=doc.get("username", ""),
            user_id=doc.get("user_id", ""),
            arn=doc.get("arn", ""),
            path=doc.get("path", ""),
            create_date=doc.get("create_date", ""),
            scan_id=doc.get("scan_id", ""),
            managed_policies=doc.get("managed_policies", []),
            inline_policies=doc.get("inline_policies", []),
            groups=doc.get("groups", []),
            tags=doc.get("tags", []),
            access_keys=doc.get("access_keys", []),
        )

    def document_to_iam_role(self, doc: dict) -> IAMRole:
        doc.pop("_id", None)

        return IAMRole(
            role_name=doc.get("role_name", ""),
            role_id=doc.get("role_id", ""),
            arn=doc.get("arn", ""),
            path=doc.get("path", ""),
            create_date=doc.get("create_date", ""),
            scan_id=doc.get("scan_id", ""),
            assume_role_policy=doc.get("assume_role_policy", {}),
            managed_policies=doc.get("managed_policies", []),
            inline_policies=doc.get("inline_policies", []),
            tags=doc.get("tags", []),
        )

    def document_to_iam_group(self, doc: dict) -> IAMGroup:
        doc.pop("_id", None)

        return IAMGroup(
            group_name=doc.get("group_name", ""),
            group_id=doc.get("group_id", ""),
            arn=doc.get("arn", ""),
            path=doc.get("path", ""),
            create_date=doc.get("create_date", ""),
            scan_id=doc.get("scan_id", ""),
            managed_policies=doc.get("managed_policies", []),
            inline_policies=doc.get("inline_policies", []),
            members=doc.get("members", []),
        )

    def document_to_iam_control(self, doc: dict) -> IAMControlFinding:
        doc.pop("_id", None)

        return IAMControlFinding(
            scan_id=doc.get("scan_id", ""),
            control_id=doc.get("control_id", ""),
            title=doc.get("title", ""),
            severity=doc.get("severity", ""),
            status=doc.get("status", ""),
            resource_type=doc.get("resource_type", ""),
            resource_id=doc.get("resource_id", ""),
            reason=doc.get("reason", ""),
            evidence=doc.get("evidence", {}),
            created_at=doc.get("created_at"),
        )

    def document_to_s3_object(self, doc: dict) -> S3Object:
        """Map document to S3Object model."""
        return S3Object(
            key=doc.get("key", ""),
            size=doc.get("size", 0),
            last_modified=doc.get("last_modified"),
            etag=doc.get("etag"),
            storage_class=doc.get("storage_class"),
            acl=doc.get("acl", {}),
            tags=doc.get("tags", []),
            metadata=doc.get("metadata", {}),
            version_id=doc.get("version_id"),
        )

    def document_to_s3_bucket(self, doc: dict) -> S3Bucket:
        """Map document to S3Bucket model."""
        doc.pop("_id", None)
        
        # Map nested objects if present
        objects = [
            self.document_to_s3_object(obj) if isinstance(obj, dict) else obj
            for obj in doc.get("objects", [])
        ]

        return S3Bucket(
            name=doc.get("name", ""),
            scan_id=doc.get("scan_id", ""),
            creation_date=doc.get("creation_date"),
            region=doc.get("region"),
            acl=doc.get("acl", {}),
            policy=doc.get("policy", {}),
            policy_status=doc.get("policy_status", {}),
            public_access_block=doc.get("public_access_block", {}),
            website_config=doc.get("website_config", {}),
            cors_config=doc.get("cors_config", {}),
            encryption_config=doc.get("encryption_config", {}),
            versioning_config=doc.get("versioning_config", {}),
            replication_config=doc.get("replication_config", {}),
            logging_config=doc.get("logging_config", {}),
            lifecycle_config=doc.get("lifecycle_config", {}),
            notification_config=doc.get("notification_config", {}),
            tagging=doc.get("tagging", []),
            objects=objects,
            object_count=doc.get("object_count", 0),
            total_size=doc.get("total_size", 0),
        )

    def document_to_lambda_function(self, doc: dict) -> LambdaFunction:
        """Map document to LambdaFunction model."""
        doc.pop("_id", None)

        return LambdaFunction(
            function_name=doc.get("function_name", ""),
            function_arn=doc.get("function_arn", ""),
            scan_id=doc.get("scan_id", ""),
            runtime=doc.get("runtime"),
            role=doc.get("role"),
            handler=doc.get("handler"),
            code_size=doc.get("code_size"),
            description=doc.get("description"),
            timeout=doc.get("timeout"),
            memory_size=doc.get("memory_size"),
            last_modified=doc.get("last_modified"),
            code_sha256=doc.get("code_sha256"),
            version=doc.get("version"),
            environment=doc.get("environment", {}),
            dead_letter_config=doc.get("dead_letter_config", {}),
            kms_key_arn=doc.get("kms_key_arn"),
            tracing_config=doc.get("tracing_config", {}),
            vpc_config=doc.get("vpc_config", {}),
            layers=doc.get("layers", []),
            state=doc.get("state"),
            state_reason=doc.get("state_reason"),
            state_reason_code=doc.get("state_reason_code"),
            last_update_status=doc.get("last_update_status"),
            last_update_status_reason=doc.get("last_update_status_reason"),
            last_update_status_reason_code=doc.get("last_update_status_reason_code"),
            package_type=doc.get("package_type"),
            architectures=doc.get("architectures", []),
            ephemeral_storage=doc.get("ephemeral_storage", {}),
            image_config=doc.get("image_config", {}),
            code_signing_config_arn=doc.get("code_signing_config_arn"),
            signing_profile_version_arn=doc.get("signing_profile_version_arn"),
            signing_job_arn=doc.get("signing_job_arn"),
            aliases=doc.get("aliases", []),
            versions=doc.get("versions", []),
            event_source_mappings=doc.get("event_source_mappings", []),
            event_invoke_configs=doc.get("event_invoke_configs", []),
            concurrency_config=doc.get("concurrency_config", {}),
            policy=doc.get("policy", {}),
            tags=doc.get("tags", []),
            reserved_concurrent_executions=doc.get("reserved_concurrent_executions"),
        )

    def document_to_lambda_layer(self, doc: dict) -> LambdaLayer:
        """Map document to LambdaLayer model."""
        doc.pop("_id", None)

        return LambdaLayer(
            layer_name=doc.get("layer_name", ""),
            layer_arn=doc.get("layer_arn", ""),
            scan_id=doc.get("scan_id", ""),
            version=doc.get("version"),
            description=doc.get("description"),
            created_date=doc.get("created_date"),
            content=doc.get("content", {}),
            compatible_runtimes=doc.get("compatible_runtimes", []),
            compatible_architectures=doc.get("compatible_architectures", []),
            license_info=doc.get("license_info"),
            policy=doc.get("policy", {}),
        )