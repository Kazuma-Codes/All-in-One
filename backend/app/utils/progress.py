import json
import redis
from datetime import datetime
from ..core.config import settings

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


def publish_job_update(user_id: int, payload: dict):
    payload = payload.copy()
    payload["timestamp"] = datetime.utcnow().isoformat()

    _get_redis().publish(
        f"user:{user_id}:jobs",
        json.dumps(payload, default=str)
    )


def notify_job_progress(job, status=None, progress=None, error=None):
    payload = {
        "type": "job_update",
        "job_id": job.id,
        "operation": job.operation,
        "status": status or job.status,
        "progress": progress if progress is not None else job.progress,
    }

    if error:
        payload["error"] = error

    publish_job_update(job.user_id, payload)