from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..core.storage import delete_object
from ..models.conversion import Conversion
from ..models.file import File
from ..models.job import Job
from ..models.usage import Usage
from ..models.user import User


def delete_expired_files(db: Session, now: datetime):
    expired_files = db.query(File).filter(
        File.expires_at != None,
        File.expires_at < now,
        File.status == "UPLOADED"
    ).all()

    for file in expired_files:
        delete_object(file.storage_key)
        file.status = "EXPIRED"


def purge_guests(db: Session, now: datetime):
    threshold = now - timedelta(days=settings.GUEST_PURGE_DAYS)

    guest_users = db.query(User).filter(
        User.email.like(f"%@{settings.GUEST_EMAIL_DOMAIN}"),
        User.created_at < threshold
    ).all()

    for user in guest_users:
        recent_job = db.query(Job.id).filter(
            Job.user_id == user.id,
            Job.created_at >= threshold
        ).first()

        if recent_job:
            continue

        job_ids = [
            job_id for (job_id,) in db.query(Job.id).filter(
                Job.user_id == user.id
            ).all()
        ]

        if job_ids:
            db.query(Conversion).filter(
                Conversion.job_id.in_(job_ids)
            ).delete(synchronize_session=False)

        db.query(Job).filter(Job.user_id == user.id).delete(synchronize_session=False)

        files = db.query(File).filter(File.user_id == user.id).all()

        for file in files:
            delete_object(file.storage_key)

        db.query(File).filter(File.user_id == user.id).delete(synchronize_session=False)
        db.query(Usage).filter(Usage.user_id == user.id).delete(synchronize_session=False)

        db.delete(user)


def run_cleanup():
    db = SessionLocal()

    try:
        now = datetime.utcnow()
        delete_expired_files(db, now)
        purge_guests(db, now)
        db.commit()
    finally:
        db.close()