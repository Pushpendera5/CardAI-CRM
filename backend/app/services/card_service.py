import json
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.core.exceptions import AppError
from app.ml.field_extractor import BusinessCardFieldExtractor
from app.ocr.easyocr_engine import EasyOCREngine
from app.preprocessing.image_preprocessor import ImagePreprocessor
from app.repositories.card_repository import OCRLogRepository, ScannedCardRepository
from app.repositories.ml_repository import MLModelRepository
from app.schemas.contact import ContactCreate
from app.services.contact_service import ContactService
from app.utils.files import save_upload, validate_upload

settings = get_settings()


class CardScanService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.scan_repo = ScannedCardRepository(db)
        self.ocr_repo = OCRLogRepository(db)
        self.contacts = ContactService(db)
        self.preprocessor = ImagePreprocessor()
        self.ocr = EasyOCREngine()

        # Load the currently active ML model (if any) into the extractor
        active_model = MLModelRepository(db).get_active()
        model_path = active_model.file_path if active_model else None
        self.extractor = BusinessCardFieldExtractor(model_path=model_path)

    def scan(self, file: UploadFile, user_id: str | None = None) -> dict:
        validate_upload(file, settings.allowed_image_type_set)
        original = save_upload(file, Path(settings.upload_dir))
        try:
            processed = self.preprocessor.preprocess(original)
            raw_text, blocks, ocr_confidence, duration = self.ocr.extract(processed)
            fields = self.extractor.extract(raw_text)
            contact = self.contacts.create_contact(
                ContactCreate(
                    name=fields.name or "Unknown Contact",
                    designation=fields.designation or None,
                    company_name=fields.company or None,
                    mobile=fields.mobile or None,
                    alternate_mobile=fields.alternate_mobile or None,
                    email=fields.email or None,
                    website=fields.website or None,
                    address=fields.address or None,
                    social_links=fields.social_links or None,
                    confidence_score=max(fields.confidence_score, ocr_confidence),
                ),
                owner_id=user_id,
            )

            scan = self.scan_repo.create(
                {
                    "contact_id": contact.id,
                    "user_id": user_id,
                    "original_file_path": str(original),
                    "processed_file_path": str(processed),
                    "raw_text": raw_text,
                    "status": "completed",
                    "confidence_score": max(fields.confidence_score, ocr_confidence),
                }
            )
            self.ocr_repo.create(
                {
                    "scan_id": scan.id,
                    "engine": "pytesseract",
                    "language": ",".join(settings.ocr_language_list),
                    "raw_text": raw_text,
                    "bounding_boxes_json": json.dumps([block.model_dump() for block in blocks]),
                    "confidence_score": ocr_confidence,
                    "processing_time_ms": duration,
                }
            )
            return {
                "scan_id": scan.id,
                "contact_id": contact.id,
                "name": contact.name,
                "designation": contact.designation or "",
                "company": contact.company_name or "",
                "mobile": contact.mobile or "",
                "alternate_mobile": contact.alternate_mobile or "",
                "email": contact.email or "",
                "website": contact.website or "",
                "address": contact.address or "",
                "social_links": contact.social_links or "",
                "confidence_score": round(contact.confidence_score, 2),
                "raw_text": raw_text,
            }
        except Exception as exc:
            self.scan_repo.create(
                {
                    "user_id": user_id,
                    "original_file_path": str(original),
                    "status": "failed",
                    "error_message": str(exc),
                }
            )
            raise AppError("Card scan failed", 500, [{"detail": str(exc)}]) from exc


