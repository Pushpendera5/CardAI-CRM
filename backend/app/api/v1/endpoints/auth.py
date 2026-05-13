from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.dependencies.auth import get_current_user, require_superadmin
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, UpdateProfileRequest, UserRead
from app.services.auth_service import AuthService
from app.utils.responses import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    """Only SuperAdmin can create new users."""
    user = AuthService(db).register(payload)
    return success_response("User registered successfully", UserRead.model_validate(user).model_dump(), 201)


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    tokens = AuthService(db).login(
        payload.email,
        payload.password,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return success_response("Login successful", tokens)


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    return success_response("Token refreshed", AuthService(db).refresh(payload.refresh_token))


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return success_response("Current user", UserRead.model_validate(user).model_dump())


@router.patch("/me")
def update_profile(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    updated = AuthService(db).update_profile(user, payload)
    return success_response("Profile updated", UserRead.model_validate(updated).model_dump())


@router.post("/logout")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    AuthService(db).logout(payload.refresh_token)
    return success_response("Logout successful", {})

