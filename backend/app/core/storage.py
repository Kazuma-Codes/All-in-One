import boto3
import uuid
from botocore.config import Config
from botocore.exceptions import ClientError
from .config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4")
)


def generate_presigned_upload_url(filename: str, content_type: str, user_id: int):
    safe_name = filename.replace("/", "_").replace("\\", "_")
    file_uuid = uuid.uuid4().hex
    storage_key = f"users/{user_id}/inputs/{file_uuid}/{safe_name}"

    upload_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": storage_key,
            "ContentType": content_type
        },
        ExpiresIn=3600
    )

    return {
        "upload_url": upload_url,
        "storage_key": storage_key
    }


def generate_presigned_download_url(storage_key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": storage_key
        },
        ExpiresIn=3600
    )


def object_exists(storage_key: str) -> bool:
    try:
        s3_client.head_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=storage_key
        )
        return True
    except ClientError:
        return False


def delete_object(storage_key: str) -> None:
    try:
        s3_client.delete_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=storage_key
        )
    except Exception:
        pass