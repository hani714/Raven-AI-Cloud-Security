import time
from datetime import datetime, timezone

from app.modules.s3.enumerator import S3Enumerator
from app.modules.s3.exceptions import S3EnumerationError, S3CredentialsError

from app.database.mongodb import save_snapshot
from app.monitoring.metrics import enumeration_duration_seconds, enumeration_errors_total

async def get_s3_data(scan_id: str, session, enumerate_objects: bool = False, max_objects_per_bucket: int = 100, 
                detailed_objects: bool = False, concurrent: bool = True):
    start_time = time.time()
    try:
        # Use the S3 enumerator
        enumerator = S3Enumerator(session=session, max_workers=5)
        
        # Perform comprehensive enumeration
        result = await enumerator.enumerate_all(
            scan_id=scan_id,
            enumerate_objects=enumerate_objects,
            max_objects_per_bucket=max_objects_per_bucket,
            detailed_object_enum=detailed_objects
        )
                
        db_save_summary = None
        if save_snapshot:
            try:
                resource_mappings = {
                    "buckets": "buckets"
                }
                
                db_save_summary = await save_snapshot(
                    service_name="s3",
                    result=result,
                    resource_mappings=resource_mappings
                )
            except Exception as e:  # pragma: no cover - runtime DB issues
                raise S3EnumerationError(f"Failed to save S3 enumeration results to database: {str(e)}")

        return {"result": result, "db_save": db_save_summary}

    except S3CredentialsError as e:
        enumeration_errors_total.labels(service='s3', error_type='S3CredentialsError').inc()
        return {
            "error": f"Credentials error: {str(e)}",
            "error_type": "S3CredentialsError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except S3EnumerationError as e:
        enumeration_errors_total.labels(service='s3', error_type='S3EnumerationError').inc()
        return {
            "error": f"Enumeration error: {str(e)}",
            "error_type": "S3EnumerationError", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except Exception as e:
        enumeration_errors_total.labels(service='s3', error_type='UnknownError').inc()
        return {
            "error": f"Unexpected error: {str(e)}",
            "error_type": "UnknownError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
    
    finally:
        duration = time.time() - start_time
        enumeration_duration_seconds.labels(service='s3').observe(duration)