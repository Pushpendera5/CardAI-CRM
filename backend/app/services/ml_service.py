import json
import time
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.core.exceptions import AppError
from app.repositories.ml_repository import MLModelRepository, TrainingDatasetRepository
from app.schemas.ml import TrainingRequest
from app.utils.files import save_upload, validate_upload

settings = get_settings()


class MLTrainingService:
    def __init__(self, db: Session) -> None:
        self.dataset_repo = TrainingDatasetRepository(db)
        self.model_repo = MLModelRepository(db)

    def upload_dataset(self, file: UploadFile):
        validate_upload(file, settings.allowed_dataset_type_set, max_mb=25)
        path = save_upload(file, Path(settings.dataset_dir))
        data = self._load_dataset(path)
        dataset = self.dataset_repo.create(
            {"file_name": file.filename or path.name, "file_path": str(path), "format": path.suffix.lstrip("."), "row_count": len(data)}
        )
        return dataset

    def train(self, payload: TrainingRequest):
        dataset = self.dataset_repo.get(payload.dataset_id) if payload.dataset_id else None
        version = time.strftime("%Y.%m.%d.%H%M%S")
        Path(settings.trained_model_dir).mkdir(parents=True, exist_ok=True)
        model_path = Path(settings.trained_model_dir) / f"{payload.model_name}-{version}.joblib"
        rows = self._load_dataset(Path(dataset.file_path)) if dataset else self._sample_rows()
        metrics: dict = {}
        try:
            import joblib
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics import accuracy_score
            from sklearn.model_selection import train_test_split
            from sklearn.pipeline import Pipeline
            from sklearn.svm import LinearSVC

            texts = [row["text"] for row in rows]
            labels = [json.dumps(row.get("entities", {}), sort_keys=True) for row in rows]

            # Train/test split only when enough samples
            acc = 0.0
            if len(rows) >= 4:
                x_train, x_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
            else:
                x_train, y_train, x_test, y_test = texts, labels, texts, labels

            pipeline = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=5000)), ("clf", LinearSVC())])
            pipeline.fit(x_train, y_train)
            if x_test:
                acc = round(accuracy_score(y_test, pipeline.predict(x_test)), 4)
            joblib.dump(pipeline, model_path)
            metrics = {"samples": len(rows), "accuracy": acc, "notes": "TF-IDF + LinearSVC field classification model."}
        except Exception as exc:
            # Fallback: persist a stub so the DB record is still created
            model_path.write_text(json.dumps({"type": "fallback", "error": str(exc)}), encoding="utf-8")
            metrics = {"samples": len(rows), "accuracy": 0.0, "notes": f"Training failed: {exc}"}
            acc = 0.0

        # Auto-activate: deactivate old active models, mark this one active
        self.model_repo.deactivate_all()
        model = self.model_repo.create(
            {
                "name": payload.model_name,
                "version": version,
                "file_path": str(model_path),
                "accuracy": metrics.get("accuracy", 0.0),
                "precision": metrics.get("accuracy", 0.0),  # approximation until separate eval
                "recall": metrics.get("accuracy", 0.0),
                "status": "active",
                "metrics_json": json.dumps(metrics),
            }
        )
        return model

    def activate_model(self, model_id: str):
        """Manually activate a specific trained model."""
        model = self.model_repo.get(model_id)
        if not model or model.is_deleted:
            raise AppError("Model not found", 404)
        if model.status not in ("trained", "active"):
            raise AppError(f"Cannot activate a model with status '{model.status}'", 400)
        self.model_repo.deactivate_all()
        return self.model_repo.update(model, {"status": "active"})

    def get_active_model(self):
        return self.model_repo.get_active()

    def status(self) -> dict:
        active = self.model_repo.get_active()
        return {
            "status": "idle",
            "active_model": {"id": active.id, "name": active.name, "version": active.version, "accuracy": active.accuracy} if active else None,
            "active_jobs": [],
        }

    def models(self):
        return self.model_repo.list(page=1, page_size=100)[0]

    def _load_dataset(self, path: Path) -> list[dict]:
        if path.suffix.lower() == ".csv":
            import pandas as pd

            return pd.read_csv(path).to_dict("records")
        if path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, list) else [data]
        raise AppError("Unsupported dataset format", 415)

    def _sample_rows(self) -> list[dict]:
        """Load built-in sample training data from datasets/sample_training_data.json."""
        sample_path = Path(settings.dataset_dir) / "sample_training_data.json"
        if sample_path.exists():
            try:
                return self._load_dataset(sample_path)
            except Exception:
                pass
        # Minimal fallback if file is missing
        return [
            {
                "text": "Rahul Sharma Sales Manager ABC Technologies Mobile 9876543210 rahul@abctech.com",
                "entities": {"name": "Rahul Sharma", "designation": "Sales Manager", "company": "ABC Technologies", "mobile": "9876543210", "email": "rahul@abctech.com"},
            },
            {
                "text": "Anita Rao Founder CloudNine Labs www.cloudnine.io anita@cloudnine.io",
                "entities": {"name": "Anita Rao", "designation": "Founder", "company": "CloudNine Labs", "website": "www.cloudnine.io", "email": "anita@cloudnine.io"},
            },
        ]

