import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.utils import settings

def init_sentry():
    sentry_dsn = settings.SENTRY_DSN
    
    if not sentry_dsn:
        return
    
    sentry_logging = LoggingIntegration(
        level=None,
        event_level="ERROR"
    )

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FastApiIntegration(transaction_style="url"),
            sentry_logging
        ],
        traces_sample_rate=0.05,
        environment=settings.SENTRY_ENVIRONMENT,
        release=f"raven-backend@1.0.0",
        send_default_pii=True,    # IMPORTANT (security)
        max_breadcrumbs=50,
        before_send=_filter_sensitive_data,
    )

def _filter_sensitive_data(event, hint):
    # Remove sensitive headers
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        for sensitive_header in ['authorization', 'cookie', 'x-api-key', 'x-access-token']:
            if sensitive_header in headers:
                headers[sensitive_header] = '[Filtered]'
    
    return event
