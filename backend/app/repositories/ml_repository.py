from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ml import MLModel, TrainingDataset
from app.repositories.base import BaseRepository


class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, MLModel)

    def get_active(self) -> MLModel | None:
        """Return the currently active model (status='active'), or None."""
        return self.db.scalar(
            select(MLModel)
            .where(MLModel.is_deleted == False, MLModel.status == "active")
            .order_by(MLModel.created_at.desc())
            .limit(1)
        )

    def deactivate_all(self) -> None:
        """Set all active models back to 'trained' status."""
        rows = self.db.scalars(
            select(MLModel).where(MLModel.is_deleted == False, MLModel.status == "active")
        ).all()
        for model in rows:
            model.status = "trained"
        self.db.commit()


class TrainingDatasetRepository(BaseRepository[TrainingDataset]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, TrainingDataset)


