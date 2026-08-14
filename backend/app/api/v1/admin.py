from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...core.database import get_db
from ...core.storage import delete_object
from ...models.user import User
from ...models.job import Job
from ...models.file import File
from ...models.conversion import Conversion
from ...models.usage import Usage
from .deps import get_current_user, get_current_admin

router = APIRouter()


@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.get("/jobs")
def list_all_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(200).all()

    return [
        {
            "id": job.id,
            "user_id": job.user_id,
            "operation": job.operation,
            "status": job.status,
            "progress": job.progress,
            "created_at": job.created_at
        }
        for job in jobs
    ]


@router.get("/stats")
def stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_jobs = db.query(Job).count()
    total_files = db.query(File).count()

    completed_jobs = db.query(Job).filter(Job.status == "COMPLETED").count()
    failed_jobs = db.query(Job).filter(Job.status == "FAILED").count()

    return {
        "total_users": total_users,
        "total_jobs": total_jobs,
        "total_files": total_files,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")

    job_ids = [
        job_id for (job_id,) in db.query(Job.id).filter(Job.user_id == user_id).all()
    ]

    if job_ids:
        db.query(Conversion).filter(
            Conversion.job_id.in_(job_ids)
        ).delete(synchronize_session=False)

    db.query(Job).filter(Job.user_id == user_id).delete(synchronize_session=False)

    files = db.query(File).filter(File.user_id == user_id).all()

    for file in files:
        delete_object(file.storage_key)

    db.query(File).filter(File.user_id == user_id).delete(synchronize_session=False)
    db.query(Usage).filter(Usage.user_id == user_id).delete(synchronize_session=False)

    db.delete(user)
    db.commit()

    return {"success": True}