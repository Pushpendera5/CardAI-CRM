from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import User, UserSession
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        if self.repo.get_by_email(payload.email.lower()):
            raise AppError("Email already registered", 409)
        return self.repo.create(
            {
                "email": payload.email.lower(),
                "full_name": payload.full_name,
                "hashed_password": hash_password(payload.password),
                "role": payload.role,
            }
        )

    def login(self, email: str, password: str, user_agent: str | None = None, ip_address: str | None = None) -> dict:
        user = self.repo.get_by_email(email.lower())
        if not user or not verify_password(password, user.hashed_password):
            raise AppError("Invalid email or password", 401)
        if not user.is_active:
            raise AppError("User account is inactive", 403)
        access = create_access_token(user.id, {"role": user.role.value})
        refresh, expires = create_refresh_token(user.id)
        self.repo.create_session(
            UserSession(
                user_id=user.id,
                refresh_token_hash=hash_token(refresh),
                expires_at=expires,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

    def refresh(self, refresh_token: str) -> dict:
        from app.core.security import decode_token

        payload = decode_token(refresh_token, "refresh")
        session = self.repo.get_session_by_hash(hash_token(refresh_token))
        if not session or session.revoked_at or session.expires_at < datetime.now(UTC):
            raise AppError("Refresh token is no longer valid", 401)
        user = self.repo.get(payload["sub"])
        if not user:
            raise AppError("User not found", 401)
        access = create_access_token(user.id, {"role": user.role.value})
        new_refresh, expires = create_refresh_token(user.id)
        session.revoked_at = datetime.now(UTC)
        self.repo.db.add(session)
        self.repo.create_session(UserSession(user_id=user.id, refresh_token_hash=hash_token(new_refresh), expires_at=expires))
        return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}

    def logout(self, refresh_token: str) -> None:
        session = self.repo.get_session_by_hash(hash_token(refresh_token))
        if session:
            session.revoked_at = datetime.now(UTC)
            self.repo.db.commit()

    def update_profile(self, user: User, payload) -> User:
        from app.schemas.auth import UpdateProfileRequest

        if not isinstance(payload, UpdateProfileRequest):
            raise AppError("Invalid payload", 400)
        updates: dict = {}
        if payload.full_name is not None:
            updates["full_name"] = payload.full_name
        if payload.new_password is not None:
            if not payload.current_password:
                raise AppError("Current password is required to set a new password", 400)
            if not verify_password(payload.current_password, user.hashed_password):
                raise AppError("Current password is incorrect", 401)
            updates["hashed_password"] = hash_password(payload.new_password)
        if not updates:
            return user
        return self.repo.update(user, updates)

