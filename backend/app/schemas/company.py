from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    website: str | None = None
    phone: str | None = None
    address: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    website: str | None = None
    phone: str | None = None
    address: str | None = None


class CompanyRead(CompanyCreate, ORMModel):
    id: str

