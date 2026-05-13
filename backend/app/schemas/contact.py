from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class ContactBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    designation: str | None = None
    company_name: str | None = None
    mobile: str | None = None
    alternate_mobile: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    address: str | None = None
    social_links: str | None = None
    tags: str | None = None
    notes: str | None = None
    confidence_score: float = 0


class ContactCreate(ContactBase):
    company_id: str | None = None


class ContactUpdate(BaseModel):
    name: str | None = None
    designation: str | None = None
    company_name: str | None = None
    mobile: str | None = None
    alternate_mobile: str | None = None
    email: EmailStr | None = None
    website: str | None = None
    address: str | None = None
    social_links: str | None = None
    tags: str | None = None
    notes: str | None = None


class ContactRead(ContactBase, ORMModel):
    id: str
    owner_id: str | None = None
    company_id: str | None = None
    card_image_url: str | None = None
    owner_name: str | None = None  # populated for SuperAdmin views

