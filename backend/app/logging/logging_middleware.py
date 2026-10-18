from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid
from typing import Callable

access_logger = logging.getLogger("access")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    EXCLUDE_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.EXCLUDE_PATHS:
            return await call_next(request)

        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            log_data = {
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "is_slow": duration_ms > 2000,
                "client_ip": request.client.host if request.client else None,
                "user_id": getattr(request.state, "user_id", None),
            }

            if duration_ms > 2000:
                access_logger.warning("Slow request", extra={"extra_data": log_data})
            
            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception:
            # Let the global exception handler log the error once with shared correlation id.
            raise
