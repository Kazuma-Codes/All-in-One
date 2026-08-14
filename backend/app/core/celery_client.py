from celery import Celery
from .config import settings

celery_client = Celery(
    "backend",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)