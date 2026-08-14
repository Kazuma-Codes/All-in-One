import os
import sys
from datetime import datetime, timedelta
from celery import shared_task

BACKEND_PATH = os.environ.get("BACKEND_PATH", "/backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.storage import s3_client, delete_object
from app.models.user import User
from app.models.file import File
from app.models.job import Job
from app.models.conversion import Conversion
from app.models.usage import Usage

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@shared_task(name="worker.cleanup_expired_files")
def cleanup_expired_files():
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        expired_files = db.query(File).filter(
            File.expires_at != None,
            File.expires_at < now,
            File.status == "UPLOADED"
        ).all()

        for file in expired_files:
            delete_object(file.storage_key)
            file.status = "EXPIRED"

        purge_guests(db, now)

        db.commit()

    finally:
        db.close()


def purge_guests(db, now: datetime):
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
