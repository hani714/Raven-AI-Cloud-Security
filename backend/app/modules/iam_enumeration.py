import time
from datetime import datetime, timezone

from fastapi import HTTPException

from app.modules.iam.enumerator import IAMEnumerator
from app.modules.iam.controls import evaluate_iam_controls
from app.modules.iam.exceptions import IAMEnumerationError, CredentialsError
from app.database.mongodb import save_snapshot
from app.monitoring.metrics import enumeration_duration_seconds, enumeration_errors_total

async def get_iam_data(scan_id: str, session):
    start_time = time.time()
    try:
        enumerator = IAMEnumerator(max_workers=10, session=session)
        
        # Perform comprehensive enumeration
        result = await enumerator.enumerate_all(
            scan_id=scan_id,
            exclude_service_roles=True
        )
        
        db_save_summary = None
        try:
            # Define IAM resource mappings for normalization
            resource_mappings = {
                "users": "users",
                "roles": "roles",
                "groups": "groups"
            }
            
            db_save_summary = await save_snapshot(
                service_name="iam",
                result=result,
                resource_mappings=resource_mappings
            )
        except Exception as e:
            raise IAMEnumerationError(f"Failed to save IAM enumeration results to database: {str(e)}")

        controls_summary = None
        try:
            controls_summary = await evaluate_iam_controls(
                scan_id=scan_id,
                session=session,
                iam_result=result,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"IAM controls evaluation failed: {str(e)}")

        return {
            "result": result,
            "db_save": db_save_summary,
            "controls": controls_summary,
        }
        
    except CredentialsError as e:
        enumeration_errors_total.labels(service='iam', error_type='CredentialsError').inc()
        return {
            "error": f"Credentials error: {str(e)}",
            "error_type": "CredentialsError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except IAMEnumerationError as e:
        enumeration_errors_total.labels(service='iam', error_type='IAMEnumerationError').inc()
        return {
            "error": f"Enumeration error: {str(e)}",
            "error_type": "IAMEnumerationError", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except Exception as e:
        enumeration_errors_total.labels(service='iam', error_type='UnknownError').inc()
        return {
            "error": f"Unexpected error: {str(e)}",
            "error_type": "UnknownError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
    
    finally:
        duration = time.time() - start_time
        enumeration_duration_seconds.labels(service='iam').observe(duration)