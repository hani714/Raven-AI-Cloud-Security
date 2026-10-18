from datetime import datetime, timezone

# Import the Lambda enumeration system
from app.database.mongodb import save_snapshot
from app.modules.aws_lambda.enumerator import LambdaEnumerator
from app.modules.aws_lambda.exceptions import LambdaEnumerationError, LambdaCredentialsError
from app.monitoring.metrics import enumeration_errors_total

async def get_lambda_data(scan_id: str, session, enumerate_functions: bool = True, enumerate_layers: bool = True,
                   get_detailed_function_config: bool = True, get_all_layer_versions: bool = False,
                   max_versions_per_layer: int = 5, concurrent: bool = True):
    try:        
        # Use the Lambda enumerator
        enumerator = LambdaEnumerator(session=session, max_workers=5)
        
        # Perform comprehensive enumeration
        result = await enumerator.enumerate_all(
            scan_id=scan_id,
            enumerate_functions=enumerate_functions,
            enumerate_layers=enumerate_layers,
            get_detailed_function_config=get_detailed_function_config,
            get_all_layer_versions=get_all_layer_versions,
            max_versions_per_layer=max_versions_per_layer,
            concurrent=concurrent
        )
        
        db_save_summary = None
        if save_snapshot:
            try:
                # Define resource mappings for Lambda normalization (optional)
                resource_mappings = {}
                if enumerate_functions:
                    resource_mappings["functions"] = "functions"
                if enumerate_layers:
                    resource_mappings["layers"] = "layers"
                
                db_save_summary = await save_snapshot(
                    service_name="lambda",
                    result=result,
                    resource_mappings=resource_mappings
                )
            except Exception as e:  # pragma: no cover - runtime DB issues
                raise LambdaEnumerationError(f"Failed to save Lambda enumeration results to database: {str(e)}")

        return {"result": result, "db_save": db_save_summary}

    except LambdaCredentialsError as e:
        enumeration_errors_total.labels(service='lambda', error_type='LambdaCredentialsError').inc()
        return {
            "error": f"Credentials error: {str(e)}",
            "error_type": "LambdaCredentialsError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except LambdaEnumerationError as e:
        enumeration_errors_total.labels(service='lambda', error_type='LambdaEnumerationError').inc()
        return {
            "error": f"Enumeration error: {str(e)}",
            "error_type": "LambdaEnumerationError", 
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }
        
    except Exception as e:
        enumeration_errors_total.labels(service='lambda', error_type='UnknownError').inc()
        return {
            "error": f"Unexpected error: {str(e)}",
            "error_type": "UnknownError",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": None
        }

