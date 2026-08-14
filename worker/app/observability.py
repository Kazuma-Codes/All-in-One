import os
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration


def init_sentry():
    dsn = os.getenv("SENTRY_DSN")

    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=0.2,
        integrations=[CeleryIntegration()]
    )