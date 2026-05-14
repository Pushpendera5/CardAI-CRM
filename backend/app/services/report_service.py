from datetime import UTC, datetime, timedelta

from sqlalchemy import cast, func, select
from sqlalchemy.orm import Session
from sqlalchemy.types import Date as SADate

from app.models.card import ScannedCard
from app.models.contact import Contact
from app.models.user import User


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def overview(self, user_id: str | None = None) -> dict:
        scan_filters = [ScannedCard.is_deleted == False]
        contact_filters = [Contact.is_deleted == False]
        if user_id:
            scan_filters.append(ScannedCard.user_id == user_id)
            contact_filters.append(Contact.owner_id == user_id)

        total_scans = self.db.scalar(select(func.count()).select_from(ScannedCard).where(*scan_filters)) or 0
        failed_scans = (
            self.db.scalar(select(func.count()).select_from(ScannedCard).where(*scan_filters, ScannedCard.status == "failed")) or 0
        )
        contacts = self.db.scalar(select(func.count()).select_from(Contact).where(*contact_filters)) or 0
        companies = (
            self.db.scalar(
                select(func.count(func.distinct(Contact.company_name))).where(
                    *contact_filters,
                    Contact.company_name.is_not(None),
                    Contact.company_name != "",
                )
            )
            or 0
        )
        avg_confidence = self.db.scalar(select(func.avg(ScannedCard.confidence_score)).where(*scan_filters)) or 0
        success_rate = round(((total_scans - failed_scans) / total_scans) * 100, 2) if total_scans else 0.0
        result: dict = {
            "total_scans": total_scans,
            "failed_scans": failed_scans,
            "contacts": contacts,
            "companies": companies,
            "ocr_accuracy": round(float(avg_confidence), 2),
            "ai_confidence_average": round(float(avg_confidence), 2),
            "scan_success_rate": success_rate,
        }
        if user_id is None:
            result["total_users"] = self.db.scalar(
                select(func.count()).select_from(User).where(User.is_deleted == False)
            ) or 0
        return result

    def most_scanned_companies(self, user_id: str | None = None, limit: int = 10) -> list[dict]:
        filters = [Contact.company_name.is_not(None), Contact.company_name != "", Contact.is_deleted == False]
        if user_id:
            filters.append(Contact.owner_id == user_id)
        rows = self.db.execute(
            select(Contact.company_name, func.count(Contact.id))
            .where(*filters)
            .group_by(Contact.company_name)
            .order_by(func.count(Contact.id).desc())
            .limit(limit)
        ).all()
        return [{"company": row[0], "count": row[1]} for row in rows]

    def recent_scans(self, user_id: str | None = None, limit: int = 8) -> list[dict]:
        stmt = (
            select(ScannedCard, Contact.name, Contact.company_name)
            .outerjoin(Contact, Contact.id == ScannedCard.contact_id)
            .where(ScannedCard.is_deleted == False)
        )
        if user_id:
            stmt = stmt.where(ScannedCard.user_id == user_id)
        rows = self.db.execute(stmt.order_by(ScannedCard.created_at.desc()).limit(limit)).all()
        items = []
        for scan, contact_name, company_name in rows:
            raw_preview = (scan.raw_text or "").replace("\n", " ").strip()
            items.append(
                {
                    "scan_id": scan.id,
                    "contact_id": scan.contact_id,
                    "name": contact_name or "Unknown Contact",
                    "company": company_name or "",
                    "status": scan.status,
                    "confidence_score": round(float(scan.confidence_score or 0), 2),
                    "scanned_at": scan.created_at.isoformat() if scan.created_at else None,
                    "raw_text_preview": raw_preview[:120],
                }
            )
        return items

    def processing_status(self, user_id: str | None = None) -> dict:
        base_filters = [ScannedCard.is_deleted == False]
        if user_id:
            base_filters.append(ScannedCard.user_id == user_id)
        stmt = (
            select(ScannedCard.status, func.count(ScannedCard.id))
            .where(*base_filters)
            .group_by(ScannedCard.status)
        )
        rows = self.db.execute(stmt).all()
        counts = {status: count for status, count in rows}

        completed = counts.get("completed", 0)
        failed = counts.get("failed", 0)
        queued = counts.get("queued", 0)
        processing = counts.get("processing", 0) + counts.get("in_progress", 0)
        total = completed + failed + queued + processing
        finalized = completed + failed

        ocr_progress = round((finalized / total) * 100, 2) if total else 0
        enrichment_progress = round((completed / total) * 100, 2) if total else 0
        crm_sync_progress = round((completed / total) * 100, 2) if total else 0

        return {
            "active_jobs": queued + processing,
            "queued_jobs": queued,
            "processing_jobs": processing,
            "failed_jobs": failed,
            "completed_jobs": completed,
            "total_jobs": total,
            "stages": {
                "ocr_extraction": ocr_progress,
                "entity_enrichment": enrichment_progress,
                "crm_sync": crm_sync_progress,
            },
        }

    def ai_insight(self, user_id: str | None = None) -> dict:
        stmt = select(Contact).where(Contact.is_deleted == False)
        if user_id:
            stmt = stmt.where(Contact.owner_id == user_id)
        contact = self.db.scalar(stmt.order_by(Contact.confidence_score.desc(), Contact.created_at.desc()).limit(1))
        if not contact:
            return {
                "title": "AI Insight",
                "message": "Scan more business cards to unlock lead quality and follow-up insights.",
            }

        company = contact.company_name or "their company"
        score = round(float(contact.confidence_score or 0), 2)
        return {
            "title": "AI Insight",
            "message": f"{contact.name} from {company} has the highest extraction confidence ({score}%). Prioritize this lead for outreach.",
        }

    def scan_trends(self, user_id: str | None = None, days: int = 7) -> list[dict]:
        """Daily scan counts for the last N days."""
        end = datetime.now(UTC).date()
        start = end - timedelta(days=days - 1)
        base_filters = [
            ScannedCard.is_deleted == False,
            cast(ScannedCard.created_at, SADate) >= start,
        ]
        if user_id:
            base_filters.append(ScannedCard.user_id == user_id)
        rows = self.db.execute(
            select(
                cast(ScannedCard.created_at, SADate).label("day"),
                func.count(ScannedCard.id).label("cnt"),
            )
            .where(*base_filters)
            .group_by(cast(ScannedCard.created_at, SADate))
            .order_by(cast(ScannedCard.created_at, SADate))
        ).all()
        counts = {str(r.day): r.cnt for r in rows}
        return [
            {"date": str(start + timedelta(days=i)), "count": counts.get(str(start + timedelta(days=i)), 0)}
            for i in range(days)
        ]

    def dashboard(self, user_id: str | None = None) -> dict:
        return {
            "overview": self.overview(user_id=user_id),
            "companies": self.most_scanned_companies(user_id=user_id, limit=10),
            "recent_scans": self.recent_scans(user_id=user_id, limit=8),
            "processing_status": self.processing_status(user_id=user_id),
            "insight": self.ai_insight(user_id=user_id),
            "scan_trends": self.scan_trends(user_id=user_id, days=7),
            "generated_at": datetime.now(UTC).isoformat(),
        }


