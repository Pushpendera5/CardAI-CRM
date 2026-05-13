from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel


class TrainingRequest(BaseModel):
    dataset_id: str | None = None
    model_name: str = "cardai-field-extractor"


class MLModelRead(ORMModel):
    id: str
    name: str
    version: str
    model_type: str
    accuracy: float | None = None
    status: str
    metrics_json: str | None = None


class DatasetRead(ORMModel):
    id: str
    file_name: str
    format: str
    row_count: int
    status: str
    metrics_json: str | None = None


class TrainingStatus(BaseModel):
    status: str
    active_jobs: list[dict[str, Any]] = []

