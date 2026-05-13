from pydantic import BaseModel

from app.schemas.contact import ContactBase


class CardScanResult(ContactBase):
    raw_text: str = ""
    scan_id: str | None = None


class OCRBlock(BaseModel):
    text: str
    confidence: float
    bbox: list | None = None

