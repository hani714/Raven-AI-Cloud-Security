import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("main")


async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.error(
        "Unhandled exception",
        extra={
            "extra_data": {
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "error": str(exc),
            }
        },
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    validation_errors = [
        {
            "field": err["loc"][-1],
            "message": err["msg"],
        }
        for err in exc.errors()
    ]

    logger.warning(
        "Request validation failed",
        extra={
            "extra_data": {
                "url": str(request.url),
                "errors": validation_errors,
            }
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "details": validation_errors,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
