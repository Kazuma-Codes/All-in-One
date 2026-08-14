import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from .config import settings


def init_sentry():
    dsn = getattr(settings, "SENTRY_DSN", None)

    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.2,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ]
    )