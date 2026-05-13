from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.base import UUIDAuditMixin


class TrainingDataset(UUIDAuditMixin, Base):
    __tablename__ = "training_datasets"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="uploaded", nullable=False)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)


class MLModel(UUIDAuditMixin, Base):
    __tablename__ = "ml_models"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    version: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    model_type: Mapped[str] = mapped_column(String(80), default="sklearn-spacy-hybrid", nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    precision: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="created", nullable=False)
    metrics_json: Mapped[str | None] = mapped_column(Text, nullable=True)

