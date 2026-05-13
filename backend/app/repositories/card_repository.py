from sqlalchemy.orm import Session

from app.models.card import OCRLog, ScannedCard
from app.repositories.base import BaseRepository


class ScannedCardRepository(BaseRepository[ScannedCard]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, ScannedCard)


class OCRLogRepository(BaseRepository[OCRLog]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, OCRLog)

