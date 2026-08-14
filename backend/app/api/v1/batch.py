from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

from ...core.database import get_db
from ...core.celery_client import celery_client
from ...core.rate_limit import limiter
from ...models.user import User
from ...models.file import File
from ...models.job import Job
from ...models.conversion import Conversion
from ...services.registry import CONVERSION_REGISTRY
from .deps import get_current_user

router = APIRouter()


class BatchRequest(BaseModel):
    file_ids: List[int]
    operation: str
    options: Dict[str, Any] = {}


@router.post("/")
@limiter.limit("10/minute")
def create_batch(
    request: Request,
    payload: BatchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.operation not in CONVERSION_REGISTRY:
        raise HTTPException(status_code=400, detail="Unsupported operation")

    files = db.query(File).filter(
        File.id.in_(payload.file_ids),
        File.user_id == current_user.id,
        File.status == "UPLOADED"
    ).all()

    if len(files) != len(payload.file_ids):
        raise HTTPException(status_code=400, detail="Some files were not found")

    job_ids = []
    meta = CONVERSION_REGISTRY[payload.operation]

    for file in files:
        job = Job(
            user_id=current_user.id,
            input_file_id=file.id,
            operation=payload.operation,
            status="QUEUED",
            progress=0,
            options=payload.options
        )

        db.add(job)
        db.flush()

        conversion = Conversion(
            job_id=job.id,
            converter=meta["category"],
            source_format=meta["source_format"],
            target_format=meta["target_format"],
            options=payload.options
        )

        db.add(conversion)

        job_ids.append(job.id)

    db.commit()

    for job_id in job_ids:
        celery_client.send_task("worker.process_conversion", args=[job_id])

    return {
        "job_ids": job_ids,
        "count": len(job_ids)
    }