from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from ..models.file import File
from ..models.job import Job

MAX_FILE_SIZE_BYTES = 250 * 1024 * 1024      # 250 MB
MAX_TOTAL_STORAGE_BYTES = 500 * 1024 * 1024  # 500 MB
MAX_ACTIVE_JOBS = 5


def check_upload_quota(user_id: int, file_size: int, db: Session):
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File exceeds 250MB free-tier limit"
        )

    total_used = db.query(func.sum(File.size)).filter(
        File.user_id == user_id,
        File.status == "UPLOADED"
    ).scalar() or 0

    if total_used + file_size > MAX_TOTAL_STORAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Storage quota exceeded. Delete old files."
        )

    active_jobs = db.query(Job).filter(
        Job.user_id == user_id,
        Job.status.in_(["QUEUED", "PROCESSING"])
    ).count()

    if active_jobs >= MAX_ACTIVE_JOBS:
        raise HTTPException(
            status_code=400,
            detail="Too many active jobs. Please wait."
        )