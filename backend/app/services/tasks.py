from pathlib import Path

from app.core.celery_app import celery_app
from app.preprocessing.image_preprocessor import ImagePreprocessor


@celery_app.task(name="ocr.process_image")
def process_image_task(image_path: str) -> dict:
    processed = ImagePreprocessor().preprocess(Path(image_path))
    return {"processed_path": str(processed)}


@celery_app.task(name="ml.train_model")
def train_model_task(dataset_id: str | None = None) -> dict:
    return {"status": "queued", "dataset_id": dataset_id}


@celery_app.task(name="exports.generate")
def generate_export_task(export_type: str) -> dict:
    return {"status": "queued", "export_type": export_type}


@celery_app.task(name="cleanup.uploads")
def cleanup_uploads_task(days_old: int = 30) -> dict:
    return {"status": "scheduled", "days_old": days_old}

