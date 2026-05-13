import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.config.settings import get_settings
from app.core.exceptions import AppError

settings = get_settings()


def ensure_runtime_dirs() -> None:
    for directory in (settings.upload_dir, settings.dataset_dir, settings.trained_model_dir):
        directory.mkdir(parents=True, exist_ok=True)


def validate_upload(file: UploadFile, allowed_types: set[str], max_mb: int | None = None) -> None:
    if file.content_type not in allowed_types:
        raise AppError("Unsupported file type", 415, [{"content_type": file.content_type}])
    max_bytes = (max_mb or settings.max_upload_size_mb) * 1024 * 1024
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_bytes:
        raise AppError("Uploaded file is too large", 413, [{"max_mb": max_mb or settings.max_upload_size_mb}])


def save_upload(file: UploadFile, target_dir: Path) -> Path:
    ensure_runtime_dirs()
    suffix = Path(file.filename or "").suffix.lower() or ".bin"
    safe_name = f"{uuid.uuid4()}{suffix}"
    path = target_dir / safe_name
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file.file.seek(0)
    return path

