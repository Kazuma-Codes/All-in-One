from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from ...core.config import settings
from ...core.database import get_db
from ...core.rate_limit import limiter
from ...core.storage import (
    generate_presigned_upload_url,
    generate_presigned_download_url,
    object_exists,
    delete_object
)
from ...models.user import User
from ...models.file import File
from ...schemas.file import UploadURLRequest, UploadURLResponse, FileOut
from ...services.quota_service import check_upload_quota
from ...utils.validation import is_guest_user
from .deps import get_current_user

router = APIRouter()


@router.post("/upload-url", response_model=UploadURLResponse)
@limiter.limit("30/minute")
def get_upload_url(
    request: Request,
    payload: UploadURLRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_upload_quota(current_user.id, payload.size, db)

    presigned = generate_presigned_upload_url(
        filename=payload.filename,
        content_type=payload.content_type,
        user_id=current_user.id
    )

    extension = payload.filename.split(".")[-1].lower() if "." in payload.filename else None

    expires_at = None
    if is_guest_user(current_user):
        expires_at = datetime.utcnow() + timedelta(hours=settings.GUEST_FILE_TTL_HOURS)

    db_file = File(
        user_id=current_user.id,
        filename=payload.filename,
        mime_type=payload.content_type,
        extension=extension,
        size=payload.size,
        storage_key=presigned["storage_key"],
        status="PENDING",
        expires_at=expires_at
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return UploadURLResponse(
        upload_url=presigned["upload_url"],
        file_id=db_file.id,
        storage_key=db_file.storage_key
    )


@router.post("/{file_id}/complete", response_model=FileOut)
def complete_upload(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if not object_exists(file.storage_key):
        raise HTTPException(status_code=400, detail="Upload not found in storage")

    file.status = "UPLOADED"
    db.commit()
    db.refresh(file)

    return file


@router.get("/", response_model=List[FileOut])
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(File).filter(
        File.user_id == current_user.id,
        File.status == "UPLOADED"
    ).order_by(File.created_at.desc()).all()


@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    delete_object(file.storage_key)

    file.status = "DELETED"
    db.commit()

    return {"success": True}


@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file = db.query(File).filter(
        File.id == file_id,
        File.user_id == current_user.id,
        File.status == "UPLOADED"
    ).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    url = generate_presigned_download_url(file.storage_key)
    return {"download_url": url}