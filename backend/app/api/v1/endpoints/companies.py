from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.services.contact_service import CompanyService
from app.utils.responses import success_response

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("")
def list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    companies, total = CompanyService(db).list_companies(page, page_size, sort_by, sort_order)
    return success_response(
        "Companies fetched",
        {"items": [CompanyRead.model_validate(item).model_dump() for item in companies], "total": total, "page": page, "page_size": page_size},
    )


@router.post("", status_code=201)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    company = CompanyService(db).create_company(payload)
    return success_response("Company created", CompanyRead.model_validate(company).model_dump(), 201)


@router.get("/{company_id}")
def get_company(company_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    company = CompanyService(db).get_company(company_id)
    return success_response("Company fetched", CompanyRead.model_validate(company).model_dump())


@router.put("/{company_id}")
def update_company(company_id: str, payload: CompanyUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    company = CompanyService(db).update_company(company_id, payload)
    return success_response("Company updated", CompanyRead.model_validate(company).model_dump())


@router.delete("/{company_id}", status_code=204)
def delete_company(company_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    CompanyService(db).delete_company(company_id)
