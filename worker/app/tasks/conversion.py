import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError

# Allow worker to import backend models
BACKEND_PATH = os.environ.get("BACKEND_PATH", "/backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.storage import s3_client
from app.models.job import Job
from app.models.file import File
from app.models.usage import Usage

# Fixed imports: PDFCompressor is in pdf/compress.py, OfficeToPDFConverter in document/
from ..converters.image.convert import ImageConverter
from ..converters.pdf.compress import PDFCompressor
from ..converters.pdf.merge import PDFMerger
from ..converters.pdf.split import PDFSplitter
from ..converters.document.office_to_pdf import OfficeToPDFConverter

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


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


def update_usage(db, user_id: int, file_size: int, seconds: float):
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


@shared_task(name="worker.process_conversion", bind=True, max_retries=2)
def process_conversion(self, job_id: int):
    db = SessionLocal()
    tmp_dir = tempfile.mkdtemp()
    start_time = datetime.utcnow()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

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

            converter = ImageConverter()
            success = converter.execute(input_path, output_path, {"target_format": "PNG"})

            if not success:
                raise Exception("Image conversion failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + ".png"
            output_mime = "image/png"
            output_extension = "png"

        elif operation == "image.png_to_jpg":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "output.jpg")

            converter = ImageConverter()
            success = converter.execute(input_path, output_path, {"target_format": "JPEG"})

            if not success:
                raise Exception("Image conversion failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + ".jpg"
            output_mime = "image/jpeg"
            output_extension = "jpg"

        elif operation == "pdf.compress":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "compressed.pdf")

            converter = PDFCompressor()
            success = converter.execute(input_path, output_path, {})

            if not success:
                raise Exception("PDF compression failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + "_compressed.pdf"
            output_mime = "application/pdf"
            output_extension = "pdf"

        elif operation == "pdf.merge":
            input_keys = options.get("input_keys", [])

            if len(input_keys) < 2:
                raise Exception("Merge requires at least 2 files")

            local_paths = []
            for key in input_keys:
                local_paths.append(download_from_storage(key, tmp_dir))

            output_path = os.path.join(tmp_dir, "merged.pdf")

            converter = PDFMerger()
            success = converter.execute(local_paths, output_path, {})

            if not success:
                raise Exception("PDF merge failed")

            output_filename = "merged.pdf"
            output_mime = "application/pdf"
            output_extension = "pdf"

        elif operation == "pdf.split":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "split_pages.zip")

            converter = PDFSplitter()
            success = converter.execute(input_path, output_path, {})

            if not success:
                raise Exception("PDF split failed")

            output_filename = job.input_file.filename.rsplit(".", 1)[0] + "_pages.zip"
            output_mime = "application/zip"
            output_extension = "zip"

        elif operation == "document.docx_to_pdf":
            input_path = download_from_storage(job.input_file.storage_key, tmp_dir)
            output_path = os.path.join(tmp_dir, "converted.pdf")

            converter = OfficeToPDFConverter()
            success = converter.execute(input_path, output_path, {})

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

    except Exception as exc:
        db.rollback()

        job = db.query(Job).filter(Job.id == job_id).first()

        if job:
            try:
                # Only mark as permanently FAILED if we've exhausted retries
                self.retry(exc=exc, countdown=30)
            except MaxRetriesExceededError:
                job.status = "FAILED"
                job.error_message = str(exc)
                db.commit()

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        db.close()