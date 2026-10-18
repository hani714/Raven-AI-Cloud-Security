from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.exceptions import register_exception_handlers
from app.logging import lifespan, RequestLoggingMiddleware
from app.routers import environment_router, scan_router, genai_router, auth_router, dashboard_router, payment_router, subscription_router, byok_router

# Initialize FastAPI app
app = FastAPI(
    title="RAVEN - AWS Pentest API",
    description="Automated AWS penetration testing and vulnerability assessment",
    version="1.0.0",
    lifespan=lifespan,
)

# Prometheus instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health", "/docs", "/openapi.json", "/favicon.ico"],
)
instrumentator.instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

# Logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.10.2:5173",
        "https://raven.shoukan-labs.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - API Endpoints
app.include_router(auth_router.router)
app.include_router(scan_router.router)
app.include_router(byok_router.router)
app.include_router(genai_router.router)
app.include_router(payment_router.router)
app.include_router(dashboard_router.router)
app.include_router(environment_router.router)
app.include_router(subscription_router.router)

# Add health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "healthy", "service": "raven"}