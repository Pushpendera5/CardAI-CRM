from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.report_service import ReportService
from app.utils.responses import success_response

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("Report overview", ReportService(db).overview(user_id=user.id))


@router.get("/companies")
def company_report(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("Most scanned companies", ReportService(db).most_scanned_companies(user_id=user.id))


@router.get("/recent-scans")
def recent_scans(limit: int = 8, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("Recent scans", ReportService(db).recent_scans(user_id=user.id, limit=min(max(limit, 1), 20)))


@router.get("/processing-status")
def processing_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("Processing status", ReportService(db).processing_status(user_id=user.id))


@router.get("/insights")
def insights(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("AI insight", ReportService(db).ai_insight(user_id=user.id))


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return success_response("Dashboard data", ReportService(db).dashboard(user_id=user.id))

