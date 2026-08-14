from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv
from .observability import init_sentry

init_sentry()
load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

celery_app.conf.task_track_started = True
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1

# Register task modules so Celery can discover them
celery_app.conf.include = [
    'app.tasks.conversion',
    'app.tasks.cleanup',
]

celery_app.conf.beat_schedule = {
    "cleanup-expired-files-hourly": {
        "task": "worker.cleanup_expired_files",
        "schedule": crontab(minute=0, hour="*")
    }
}