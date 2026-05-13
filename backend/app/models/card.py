from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import UUIDAuditMixin


class ScannedCard(UUIDAuditMixin, Base):
    __tablename__ = "scanned_cards"

    contact_id: Mapped[str | None] = mapped_column(ForeignKey("contacts.id"), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    original_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    processed_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    ocr_logs: Mapped[list["OCRLog"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class OCRLog(UUIDAuditMixin, Base):
    __tablename__ = "ocr_logs"

    scan_id: Mapped[str] = mapped_column(ForeignKey("scanned_cards.id"), nullable=False, index=True)
    engine: Mapped[str] = mapped_column(String(80), default="easyocr", nullable=False)
    language: Mapped[str] = mapped_column(String(80), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    bounding_boxes_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    processing_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    scan: Mapped[ScannedCard] = relationship(back_populates="ocr_logs")

