import os
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config import settings


async def upload_file(file: UploadFile) -> dict:
    """Upload a file and return its metadata."""
    if settings.STORAGE_BACKEND == "local":
        return await _upload_local(file)
    else:
        raise NotImplementedError(f"Storage backend '{settings.STORAGE_BACKEND}' not implemented")


async def _upload_local(file: UploadFile) -> dict:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_ext = os.path.splitext(file.filename or "file")[1]
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    return {
        "file_url": f"/uploads/{unique_name}",
        "file_name": file.filename or unique_name,
        "file_size_bytes": len(content),
        "mime_type": file.content_type or "application/octet-stream",
    }
