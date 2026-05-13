"""SuperAdmin / Admin management endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import require_admin, require_superadmin
from app.core.exceptions import AppError
from app.database.session import get_db
from app.models.contact import Contact
from app.models.user import User, UserRole
from app.schemas.auth import RegisterRequest, UserRead
from app.services.auth_service import AuthService
from app.utils.responses import success_response

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── User Management (SuperAdmin only) ────────────────────────────────────────

@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    """List all users with their contact count and last activity."""
    stmt = select(User).where(User.is_deleted == False)
    if search:
        pattern = f"%{search}%"
        from sqlalchemy import or_
        stmt = stmt.where(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    users = db.scalars(stmt.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()

    # Get contact count per user
    user_ids = [u.id for u in users]
    contact_counts: dict[str, int] = {}
    if user_ids:
        rows = db.execute(
            select(Contact.owner_id, func.count(Contact.id).label("cnt"))
            .where(Contact.owner_id.in_(user_ids), Contact.is_deleted == False)
            .group_by(Contact.owner_id)
        ).all()
        contact_counts = {r.owner_id: r.cnt for r in rows}

    items = []
    for u in users:
        d = UserRead.model_validate(u).model_dump()
        d["contact_count"] = contact_counts.get(u.id, 0)
        d["created_at"] = u.created_at.isoformat() if u.created_at else None
        items.append(d)

    return success_response("Users fetched", {"items": items, "total": total, "page": page, "page_size": page_size})


@router.post("/users", status_code=201)
def create_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    """SuperAdmin creates a new user (any role)."""
    user = AuthService(db).register(payload)
    return success_response("User created", UserRead.model_validate(user).model_dump(), 201)


@router.patch("/users/{user_id}/role")
def change_user_role(
    user_id: str,
    role: UserRole,
    db: Session = Depends(get_db),
    current: User = Depends(require_superadmin),
):
    """SuperAdmin changes a user's role."""
    if user_id == current.id:
        raise AppError("Cannot change your own role", 400)
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise AppError("User not found", 404)
    user.role = role
    db.commit()
    db.refresh(user)
    return success_response("Role updated", UserRead.model_validate(user).model_dump())


@router.patch("/users/{user_id}/status")
def toggle_user_status(
    user_id: str,
    is_active: bool,
    db: Session = Depends(get_db),
    current: User = Depends(require_superadmin),
):
    """SuperAdmin activates or deactivates a user."""
    if user_id == current.id:
        raise AppError("Cannot deactivate your own account", 400)
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise AppError("User not found", 404)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return success_response("User status updated", UserRead.model_validate(user).model_dump())


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(require_superadmin),
):
    """SuperAdmin soft-deletes a user."""
    if user_id == current.id:
        raise AppError("Cannot delete your own account", 400)
    user = db.get(User, user_id)
    if not user or user.is_deleted:
        raise AppError("User not found", 404)
    user.is_deleted = True
    user.is_active = False
    db.commit()
