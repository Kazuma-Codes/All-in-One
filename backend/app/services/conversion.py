import os
import shutil
import tempfile
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.database import SessionLocal
from ..core.storage import s3_client
from ..models.file import File
from ..models.job import Job
from ..models.usage import Usage

from ..converters.image.convert import ImageConverter
from ..converters.pdf.compress import PDFCompressor
from ..converters.pdf.merge import PDFMerger
from ..converters.pdf.split import PDFSplitter
from ..converters.document.office_to_pdf import OfficeToPDFConverter

conversion_slots = threading.BoundedSemaphore(settings.MAX_CONCURRENT_JOBS)


class ConversionBusyError(Exception):
    pass


@contextmanager
def acquire_slot():
    if not conversion_slots.acquire(blocking=False):
        raise ConversionBusyError(
            f"Too many conversions running right now (max {settings.MAX_CONCURRENT_JOBS}). Try again in a moment."
        )
    try:
        yield
    finally:
        conversion_slots.release()


def download_from_storage(storage_key: str, tmp_dir: str) -> str:
    filename = os.path.basename(storage_key)
    local_path = os.path.join(tmp_dir, filename)

    s3_client.download_file(
        settings.S3_BUCKET_NAME,
        storage_key,
        local_path
    )

    return local_path


def upload_to_storage(local_path: str, storage_key: str):
    s3_client.upload_file(
        local_path,
        settings.S3_BUCKET_NAME,
        storage_key
    )


def update_usage(db: Session, user_id: int, file_size: int, seconds: float):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    usage = db.query(Usage).filter(
        Usage.user_id == user_id,
        Usage.date == today
    ).first()

    if not usage:
        usage = Usage(
            user_id=user_id,
            date=today,
            files_processed=0,
            bytes_processed=0,
            processing_seconds=0.0
        )
        db.add(usage)

    usage.files_processed += 1
    usage.bytes_processed += file_size
    usage.processing_seconds += seconds

    db.commit()


def process_conversion(job_id: int) -> str:
    """Convert a job inline. Returns the final job status."""
    db = SessionLocal()
    tmp_dir = tempfile.mkdtemp()
    start_time = datetime.utcnow()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return "NOT_FOUND"

        if job.status in ("COMPLETED", "CANCELLED", "FAILED"):
            return job.status

        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if job.input_file and job.input_file.size > max_bytes:
            job.status = "FAILED"
            job.error_message = f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit"
            job.completed_at = datetime.utcnow()
            db.commit()
            return job.status

        job.status = "PROCESSING"
        job.started_at = datetime.utcnow()
        job.progress = 10
        db.commit()

        operation = job.operation
        options = job.options or {}

        output_path = None
        output_filename = None
        output_mime = None
        output_extension = None

        if operation == "image.jpg_to_png":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "output.png")

            success = ImageConverter().execute(input_path, output_path, {"target_format": "PNG"})
            if not success:
                raise Exception("Image conversion failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + ".png"
            output_mime = "image/png"
            output_extension = "png"

        elif operation == "image.png_to_jpg":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "output.jpg")

            success = ImageConverter().execute(input_path, output_path, {"target_format": "JPEG"})
            if not success:
                raise Exception("Image conversion failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + ".jpg"
            output_mime = "image/jpeg"
            output_extension = "jpg"

        elif operation == "pdf.compress":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "compressed.pdf")

            success = PDFCompressor().execute(input_path, output_path, {})
            if not success:
                raise Exception("PDF compression failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + "_compressed.pdf"
            output_mime = "application/pdf"
            output_extension = "pdf"

        elif operation == "pdf.merge":
            input_keys = options.get("input_keys", [])

            if len(input_keys) < 2:
                raise Exception("Merge requires at least 2 files")

            local_paths = [download_from_storage(key, tmp_dir) for key in input_keys]
            output_path = os.path.join(tmp_dir, "merged.pdf")

            success = PDFMerger().execute(local_paths, output_path, {})
            if not success:
                raise Exception("PDF merge failed")

            output_filename = "merged.pdf"
            output_mime = "application/pdf"
            output_extension = "pdf"

        elif operation == "pdf.split":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "split_pages.zip")

            success = PDFSplitter().execute(input_path, output_path, {})
            if not success:
                raise Exception("PDF split failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + "_pages.zip"
            output_mime = "application/zip"
            output_extension = "zip"

        elif operation == "document.docx_to_pdf":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "converted.pdf")

            success = OfficeToPDFConverter().execute(input_path, output_path, {})
            if not success:
                raise Exception("Document conversion failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + ".pdf"
            output_mime = "application/pdf"
            output_extension = "pdf"

        else:
            raise Exception(f"Unsupported operation: {operation}")

        job.progress = 70
        db.commit()

        output_storage_key = f"users/{job.user_id}/outputs/{job.id}/{output_filename}"

        upload_to_storage(output_path, output_storage_key)

        output_file = File(
            user_id=job.user_id,
            filename=output_filename,
            mime_type=output_mime,
            extension=output_extension,
            size=os.path.getsize(output_path),
            storage_key=output_storage_key,
            status="UPLOADED",
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )

        db.add(output_file)
        db.flush()

        job.output_file_id = output_file.id
        job.status = "COMPLETED"
        job.progress = 100
        job.completed_at = datetime.utcnow()

        db.commit()

        processing_seconds = (datetime.utcnow() - start_time).total_seconds()
        update_usage(db, job.user_id, os.path.getsize(output_path), processing_seconds)

        return job.status

    except Exception as exc:
        db.rollback()

        job = db.query(Job).filter(Job.id == job_id).first()

        if job:
            job.status = "FAILED"
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()
            db.commit()

        return "FAILED"

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        db.close()


def repair_stale_jobs():
    """Mark jobs left QUEUED/PROCESSING by a previous process as FAILED."""
    db = SessionLocal()

    try:
        stale = db.query(Job).filter(
            Job.status.in_(["QUEUED", "PROCESSING"]),
            Job.created_at < datetime.utcnow() - timedelta(hours=1)
        ).all()

        for job in stale:
            job.status = "FAILED"
            job.error_message = "Interrupted by a server restart"

        if stale:
            db.commit()
    finally:
        db.close()