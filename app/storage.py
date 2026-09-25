"""
Unified file storage for the portfolio.

Backends:
  - "local": saves files to app/static/uploads/ (dev)
  - "r2":    uploads files to Cloudflare R2 (production)
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from flask import current_app

try:
    import boto3
    from botocore.config import Config as BotoConfig
except ImportError:
    boto3 = None


# ─────────────────────────────────────────────────────────────
# Public helpers
# ─────────────────────────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_file(file_storage, folder: str = "images") -> str:
    if file_storage is None or file_storage.filename == "":
        raise ValueError("No file provided.")

    if not allowed_file(file_storage.filename):
        raise ValueError("File type not allowed.")

    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    backend = current_app.config.get("STORAGE_BACKEND", "local")
    if backend == "r2":
        return _save_to_r2(file_storage, folder, unique_name)
    return _save_to_local(file_storage, folder, unique_name)


def delete_file(file_url: str) -> bool:
    if not file_url:
        return False
    backend = current_app.config.get("STORAGE_BACKEND", "local")
    try:
        if backend == "r2":
            return _delete_from_r2(file_url)
        return _delete_from_local(file_url)
    except Exception as e:
        current_app.logger.warning(f"Failed to delete {file_url}: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# LOCAL backend
# ─────────────────────────────────────────────────────────────
def _save_to_local(file_storage, folder: str, unique_name: str) -> str:
    base = Path(current_app.config["UPLOAD_FOLDER"])
    target_dir = base / folder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / unique_name
    file_storage.save(str(target_path))

    prefix = current_app.config["LOCAL_UPLOAD_URL_PREFIX"]
    return f"{prefix}/{folder}/{unique_name}"


def _delete_from_local(file_url: str) -> bool:
    prefix = current_app.config["LOCAL_UPLOAD_URL_PREFIX"]
    if not file_url.startswith(prefix):
        return False
    relative = file_url[len(prefix):].lstrip("/")
    base = Path(current_app.config["UPLOAD_FOLDER"])
    target = base / relative
    if target.exists():
        target.unlink()
        return True
    return False


# ─────────────────────────────────────────────────────────────
# R2 backend (S3-compatible)
# ─────────────────────────────────────────────────────────────
def _get_r2_client():
    if boto3 is None:
        raise RuntimeError("boto3 is not installed. Add it to requirements.txt.")
    return boto3.client(
        "s3",
        endpoint_url=f"https://{current_app.config['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=current_app.config["R2_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["R2_SECRET_ACCESS_KEY"],
        config=BotoConfig(signature_version="s3v4"),
        region_name="auto",
    )


def _save_to_r2(file_storage, folder: str, unique_name: str) -> str:
    client = _get_r2_client()
    bucket = current_app.config["R2_BUCKET_NAME"]
    key = f"{folder}/{unique_name}"
    content_type = file_storage.mimetype or "application/octet-stream"

    client.upload_fileobj(
        file_storage, bucket, key,
        ExtraArgs={"ContentType": content_type},
    )

    public_base = current_app.config["R2_PUBLIC_URL"].rstrip("/")
    return f"{public_base}/{key}"


def _delete_from_r2(file_url: str) -> bool:
    client = _get_r2_client()
    bucket = current_app.config["R2_BUCKET_NAME"]
    public_base = current_app.config["R2_PUBLIC_URL"].rstrip("/")
    if not file_url.startswith(public_base):
        return False
    key = file_url[len(public_base):].lstrip("/")
    client.delete_object(Bucket=bucket, Key=key)
    return True