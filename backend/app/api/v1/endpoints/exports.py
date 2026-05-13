from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.database.session import get_db
from app.exports.export_service import ExportService
from app.models.user import User

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.get("/contacts.csv")
def export_csv(
    search: str | None = None,
    tag: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return Response(
        content=ExportService(db).csv_bytes(owner_id=user.id, search=search, tag=tag, date_from=date_from, date_to=date_to),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts.csv"},
    )


@router.get("/contacts.xlsx")
def export_excel(
    search: str | None = None,
    tag: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return Response(
        content=ExportService(db).excel_bytes(owner_id=user.id, search=search, tag=tag, date_from=date_from, date_to=date_to),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=contacts.xlsx"},
    )


@router.get("/contacts.pdf")
def export_pdf(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return Response(
        content=ExportService(db).pdf_bytes(owner_id=user.id),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=contacts.pdf"},
    )

