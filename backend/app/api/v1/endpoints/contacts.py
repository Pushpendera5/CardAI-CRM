from pathlib import Path

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date

from app.api.v1.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.card import ScannedCard
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact_service import ContactService
from app.utils.responses import success_response

router = APIRouter(prefix="/contacts", tags=["Contacts"])


def _card_image_map(db: Session, contact_ids: list[str]) -> dict[str, str]:
    """Return {contact_id: '/uploads/<filename>'} for the latest scan per contact."""
    if not contact_ids:
        return {}
    rows = db.execute(
        select(ScannedCard.contact_id, ScannedCard.original_file_path)
        .where(ScannedCard.contact_id.in_(contact_ids), ScannedCard.original_file_path.isnot(None))
        .order_by(ScannedCard.created_at.desc())
    ).all()
    result: dict[str, str] = {}
    for contact_id, file_path in rows:
        if contact_id not in result:
            result[contact_id] = f"/uploads/{Path(file_path).name}"
    return result


@router.get("")
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    tag: str | None = None,
    company_id: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by: str = "created_at",
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    is_superadmin = user.role.value == "SuperAdmin"
    contacts, total = ContactService(db).list_contacts(
        page, page_size, search, sort_by, sort_order,
        owner_id=None if is_superadmin else user.id,
        tag=tag, company_id=company_id,
        date_from=date_from, date_to=date_to,
    )
    images = _card_image_map(db, [c.id for c in contacts])
    # For SuperAdmin: build owner_id → full_name map
    owner_names: dict[str, str] = {}
    if is_superadmin:
        from app.models.user import User as UserModel
        owner_ids = {c.owner_id for c in contacts if c.owner_id}
        if owner_ids:
            rows = db.execute(select(UserModel.id, UserModel.full_name).where(UserModel.id.in_(owner_ids))).all()
            owner_names = {r.id: r.full_name for r in rows}
    items = []
    for c in contacts:
        d = ContactRead.model_validate(c).model_dump()
        d["card_image_url"] = images.get(c.id)
        d["owner_name"] = owner_names.get(c.owner_id) if c.owner_id else None
        items.append(d)
    return success_response(
        "Contacts fetched",
        {"items": items, "total": total, "page": page, "page_size": page_size},
    )


@router.get("/{contact_id}")
def get_contact(contact_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = ContactService(db).get_contact(contact_id, owner_id=user.id)
    d = ContactRead.model_validate(contact).model_dump()
    d["card_image_url"] = _card_image_map(db, [contact.id]).get(contact.id)
    return success_response("Contact fetched", d)


@router.post("", status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = ContactService(db).create_contact(payload, owner_id=user.id)
    return success_response("Contact created", ContactRead.model_validate(contact).model_dump(), 201)


@router.put("/{contact_id}")
def update_contact(contact_id: str, payload: ContactUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    contact = ContactService(db).update_contact(contact_id, payload, owner_id=user.id)
    return success_response("Contact updated", ContactRead.model_validate(contact).model_dump())


@router.delete("/{contact_id}")
def delete_contact(contact_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ContactService(db).delete_contact(contact_id, owner_id=user.id)
    return success_response("Contact deleted", {})
