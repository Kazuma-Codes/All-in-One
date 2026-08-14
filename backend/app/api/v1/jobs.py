from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ...core.config import settings
from ...core.database import get_db
from ...core.rate_limit import limiter
from ...core.storage import generate_presigned_download_url
from ...models.user import User
from ...models.file import File
from ...models.job import Job
from ...models.conversion import Conversion
from ...schemas.job import JobCreateRequest, JobOut
from ...services.registry import CONVERSION_REGISTRY
from ...services.conversion import acquire_slot, process_conversion, ConversionBusyError
from .deps import get_current_user

router = APIRouter()


def check_file_size(file: File):
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if file.size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {settings.MAX_FILE_SIZE_MB} MB limit"
        )


@router.post("/", response_model=JobOut)
@limiter.limit("20/minute")
def create_job(
    request: Request,
    payload: JobCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if payload.operation not in CONVERSION_REGISTRY:
        raise HTTPException(status_code=400, detail="Unsupported operation")

    meta = CONVERSION_REGISTRY[payload.operation]
    options = payload.options or {}

    input_file = None
    input_keys = []

    if payload.operation == "pdf.merge":
        if not payload.input_file_ids or len(payload.input_file_ids) < 2:
            raise HTTPException(status_code=400, detail="Merge requires at least 2 files")

        files = db.query(File).filter(
            File.id.in_(payload.input_file_ids),
            File.user_id == current_user.id,
            File.status == "UPLOADED"
        ).all()

        if len(files) != len(payload.input_file_ids):
            raise HTTPException(status_code=400, detail="One or more input files not found")

        for file in files:
            check_file_size(file)

        input_keys = [f.storage_key for f in files]
        input_file = files[0]
        options["input_keys"] = input_keys

    else:
        if not payload.input_file_id:
            raise HTTPException(status_code=400, detail="input_file_id is required")

        input_file = db.query(File).filter(
            File.id == payload.input_file_id,
            File.user_id == current_user.id,
            File.status == "UPLOADED"
        ).first()

        if not input_file:
            raise HTTPException(status_code=400, detail="Input file not found")

        check_file_size(input_file)

    job = Job(
        user_id=current_user.id,
        input_file_id=input_file.id,
        operation=payload.operation,
        status="QUEUED",
        progress=0,
        options=options
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    conversion = Conversion(
        job_id=job.id,
        converter=meta["category"],
        source_format=meta["source_format"],
        target_format=meta["target_format"],
        options=options
    )

    db.add(conversion)
    db.commit()

    try:
        with acquire_slot():
            process_conversion(job.id)
    except ConversionBusyError as exc:
        job.status = "CANCELLED"
        db.commit()
        raise HTTPException(status_code=429, detail=str(exc))

    return job


@router.get("/", response_model=List[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Job).filter(
        Job.user_id == current_user.id
    ).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.post("/{job_id}/cancel")
def cancel_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "QUEUED":
        raise HTTPException(status_code=400, detail="Only queued jobs can be cancelled")

    job.status = "CANCELLED"
    db.commit()

    return {"success": True}


@router.get("/{job_id}/download")
def download_job_output(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job is not completed")

    if not job.output_file:
        raise HTTPException(status_code=404, detail="Output file not found")

    url = generate_presigned_download_url(job.output_file.storage_key)
    return {"download_url": url}