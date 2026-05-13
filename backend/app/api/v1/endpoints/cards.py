from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.card_service import CardScanService
from app.utils.responses import success_response

router = APIRouter(prefix="/cards", tags=["Business Card Scanner"])


@router.post("/scan")
def scan_card(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = CardScanService(db).scan(image, user_id=user.id)
    return success_response("Card scanned successfully", result)

