from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import require_admin
from app.database.session import get_db
from app.models.user import User
from app.schemas.ml import DatasetRead, MLModelRead, TrainingRequest
from app.services.ml_service import MLTrainingService
from app.utils.responses import success_response

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.post("/upload-dataset", status_code=201)
def upload_dataset(
    dataset: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    saved = MLTrainingService(db).upload_dataset(dataset)
    return success_response("Dataset uploaded", DatasetRead.model_validate(saved).model_dump(), 201)


@router.post("/train")
def train(payload: TrainingRequest, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    model = MLTrainingService(db).train(payload)
    return success_response("Model training completed — model is now active", MLModelRead.model_validate(model).model_dump())


@router.post("/activate/{model_id}")
def activate_model(model_id: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Manually activate a specific trained model so it is used for all future card scans."""
    model = MLTrainingService(db).activate_model(model_id)
    return success_response("Model activated — will be used for all future card scans", MLModelRead.model_validate(model).model_dump())


@router.get("/active")
def active_model(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Get the currently active ML model."""
    svc = MLTrainingService(db)
    model = svc.get_active_model()
    if not model:
        return success_response("No active model found. Train one via POST /ml/train.", None)
    return success_response("Active model", MLModelRead.model_validate(model).model_dump())


@router.get("/status")
def status(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return success_response("ML status", MLTrainingService(db).status())


@router.get("/models")
def models(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    items = MLTrainingService(db).models()
    return success_response("ML models fetched", [MLModelRead.model_validate(item).model_dump() for item in items])

