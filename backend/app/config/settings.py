import logging
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET = "change-this-in-production"  # noqa: S105

# Always resolve .env relative to this file's directory (backend/), regardless of cwd
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", case_sensitive=False)

    app_name: str = "CardAI CRM"
    app_env: Literal["local", "dev", "staging", "prod", "test"] = "local"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api/v1"
    frontend_origin: str = "http://localhost:5173"
    # Comma-separated list of additional allowed CORS origins (besides frontend_origin)
    extra_cors_origins: str = ""

    database_url: str = Field(
        default="mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/CardAICRM"
        "?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = _DEFAULT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    max_upload_size_mb: int = 10
    upload_dir: Path = _ENV_FILE.parent / "uploads"
    dataset_dir: Path = _ENV_FILE.parent / "datasets"
    trained_model_dir: Path = _ENV_FILE.parent / "trained_models"
    allowed_image_types: str = "image/jpeg,image/png,image/webp"
    allowed_dataset_types: str = "text/csv,application/json"

    ocr_languages: str = "en"
    rate_limit_per_minute: int = 120

    @model_validator(mode="after")
    def _validate_production(self) -> "Settings":
        if self.app_env == "prod" and self.secret_key == _DEFAULT_SECRET:
            raise ValueError(
                "SECRET_KEY must be changed from the default value in production. "
                "Set a long random string in your .env file."
            )
        if self.app_env == "prod" and self.debug:
            logging.getLogger(__name__).warning("APP_DEBUG=true in production — disabling debug mode.")
            object.__setattr__(self, "debug", False)
        return self

    @computed_field
    @property
    def docs_enabled(self) -> bool:
        """OpenAPI docs are only available outside production."""
        return self.app_env not in ("prod", "staging")

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        origins = {self.frontend_origin}
        if self.app_env not in ("prod", "staging"):
            origins.update(["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"])
        for origin in self.extra_cors_origins.split(","):
            origin = origin.strip()
            if origin:
                origins.add(origin)
        return list(origins)

    @computed_field
    @property
    def allowed_image_type_set(self) -> set[str]:
        return {item.strip() for item in self.allowed_image_types.split(",") if item.strip()}

    @computed_field
    @property
    def allowed_dataset_type_set(self) -> set[str]:
        return {item.strip() for item in self.allowed_dataset_types.split(",") if item.strip()}

    @computed_field
    @property
    def ocr_language_list(self) -> list[str]:
        return [item.strip() for item in self.ocr_languages.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
