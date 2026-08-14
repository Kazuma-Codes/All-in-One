from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...core.database import get_db
from ...models.user import User
from ...models.file import File
from ...models.job import Job
from .deps import get_current_user

router = APIRouter()


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at
    }


@router.get("/me/usage")
def get_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_storage = db.query(func.sum(File.size)).filter(
        File.user_id == current_user.id,
        File.status == "UPLOADED"
    ).scalar() or 0

    total_jobs = db.query(Job).filter(
        Job.user_id == current_user.id
    ).count()

    completed_jobs = db.query(Job).filter(
        Job.user_id == current_user.id,
        Job.status == "COMPLETED"
    ).count()

    return {
        "storage_used_bytes": total_storage,
        "storage_limit_bytes": 500 * 1024 * 1024,
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs
    }