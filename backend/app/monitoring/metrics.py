from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps
from typing import Callable

# HTTP Metrics (Auto-instrumented by PrometheusMiddleware)

# Scan Operation Metrics

scans_total = Counter(
    'raven_scans_total',
    'Total number of scans created',
    ['status']  # completed, failed, running
)

scan_duration_seconds = Histogram(
    'raven_scan_duration_seconds',
    'Duration of scan operations',
    ['scan_type'],  # full, iam_only, s3_only, lambda_only
    buckets=[1, 5, 10, 30, 60, 120, 300, 600, 1800]  # 1s to 30min
)

active_scans = Gauge(
    'raven_active_scans',
    'Number of currently running scans'
)

# AWS Enumeration Metrics

aws_resources_discovered = Counter(
    'raven_aws_resources_discovered_total',
    'Total AWS resources discovered',
    ['service', 'resource_type']  # iam/users, s3/buckets, lambda/functions
)

enumeration_duration_seconds = Histogram(
    'raven_enumeration_duration_seconds',
    'Duration of AWS service enumeration',
    ['service'],  # iam, s3, lambda
    buckets=[0.5, 1, 2, 5, 10, 30, 60, 120]
)

aws_api_calls_total = Counter(
    'raven_aws_api_calls_total',
    'Total AWS API calls made',
    ['service', 'operation', 'status']  # iam/list_users/success
)

enumeration_errors_total = Counter(
    'raven_enumeration_errors_total',
    'Total enumeration errors',
    ['service', 'error_type']  # iam/AccessDenied
)

# GenAI/LLM Metrics

llm_calls_total = Counter(
    'raven_llm_calls_total',
    'Total LLM API calls',
    ['stage', 'status']  # triage/success, deep_analysis/error
)

llm_response_duration_seconds = Histogram(
    'raven_llm_response_duration_seconds',
    'LLM API response time',
    ['stage'],  # triage, deep_analysis, command_generation
    buckets=[0.5, 1, 2, 5, 10, 20, 30, 60]
)

attack_paths_generated = Counter(
    'raven_attack_paths_generated_total',
    'Total attack paths generated',
    ['risk_level']  # critical, high, medium, low
)

# Database Metrics

db_operations_total = Counter(
    'raven_db_operations_total',
    'Total database operations',
    ['db_type', 'operation', 'status']  # postgres/insert/success, mongodb/query/error
)

db_query_duration_seconds = Histogram(
    'raven_db_query_duration_seconds',
    'Database query duration',
    ['db_type', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 2, 5]
)

db_connection_pool_size = Gauge(
    'raven_db_connection_pool_size',
    'Database connection pool size',
    ['db_type', 'state']  # postgres/active, postgres/idle
)


# Decorators for Easy Instrumentation

def track_scan_duration(scan_type: str = 'full'):
    """Decorator to track scan operation duration."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            active_scans.inc()
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                scans_total.labels(status='completed').inc()
                return result
            except Exception as e:
                scans_total.labels(status='failed').inc()
                raise
            finally:
                duration = time.time() - start_time
                scan_duration_seconds.labels(scan_type=scan_type).observe(duration)
                active_scans.dec()
        return wrapper
    return decorator


def track_enumeration(service: str):
    """Decorator to track AWS enumeration duration."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                enumeration_duration_seconds.labels(service=service).observe(duration)
        return wrapper
    return decorator


def track_llm_call(stage: str):
    """Decorator to track LLM API calls."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                llm_calls_total.labels(stage=stage, status='success').inc()
                return result
            except Exception as e:
                llm_calls_total.labels(stage=stage, status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                llm_response_duration_seconds.labels(stage=stage).observe(duration)
        return wrapper
    return decorator


def track_db_operation(db_type: str, operation: str):
    """Decorator to track database operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                db_operations_total.labels(db_type=db_type, operation=operation, status='success').inc()
                return result
            except Exception as e:
                db_operations_total.labels(db_type=db_type, operation=operation, status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(db_type=db_type, operation=operation).observe(duration)
        return wrapper
    return decorator