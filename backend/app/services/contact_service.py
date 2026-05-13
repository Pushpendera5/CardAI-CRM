from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.contact import Contact
from app.repositories.contact_repository import CompanyRepository, ContactRepository
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.contact import ContactCreate, ContactUpdate
from app.utils.sanitization import sanitize_payload


def _link_company(db, contact: Contact, company_name: str | None) -> None:
    """Find or create a company by name and link it to the contact."""
    if not company_name or not company_name.strip():
        return
    repo = CompanyRepository(db)
    company = repo.find_by_name(company_name)
    if not company:
        company = repo.create({"name": company_name.strip()})
    contact.company_id = company.id
    db.commit()
    db.refresh(contact)


class ContactService:
    def __init__(self, db: Session) -> None:
        self.repo = ContactRepository(db)

    def list_contacts(
        self,
        page: int,
        page_size: int,
        search: str | None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        owner_id: str | None = None,
        tag: str | None = None,
        company_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[Contact], int]:
        return self.repo.list(
            page=page,
            page_size=page_size,
            filters=self.repo.search_filters(search, owner_id=owner_id, tag=tag, company_id=company_id, date_from=date_from, date_to=date_to),
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def get_contact(self, contact_id: str, owner_id: str | None = None) -> Contact:
        contact = self.repo.get(contact_id)
        if not contact or contact.is_deleted:
            raise AppError("Contact not found", 404)
        if owner_id and contact.owner_id != owner_id:
            raise AppError("Contact not found", 404)
        return contact

    def create_contact(self, payload: ContactCreate, owner_id: str | None = None) -> Contact:
        data = sanitize_payload(payload.model_dump())
        data["owner_id"] = owner_id
        contact = self.repo.create(data)
        _link_company(self.repo.db, contact, payload.company_name)
        return contact

    def update_contact(self, contact_id: str, payload: ContactUpdate, owner_id: str | None = None) -> Contact:
        contact = self.repo.update(
            self.get_contact(contact_id, owner_id=owner_id),
            sanitize_payload(payload.model_dump(exclude_unset=True)),
        )
        if payload.company_name is not None:
            _link_company(self.repo.db, contact, payload.company_name)
        return contact

    def delete_contact(self, contact_id: str, owner_id: str | None = None) -> None:
        self.repo.soft_delete(self.get_contact(contact_id, owner_id=owner_id))


class CompanyService:
    def __init__(self, db: Session) -> None:
        self.repo = CompanyRepository(db)

    def list_companies(self, page: int, page_size: int, sort_by: str = "created_at", sort_order: str = "desc") -> tuple[list, int]:
        return self.repo.list(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)

    def get_company(self, company_id: str):
        company = self.repo.get(company_id)
        if not company or company.is_deleted:
            raise AppError("Company not found", 404)
        return company

    def create_company(self, payload: CompanyCreate):
        return self.repo.create(sanitize_payload(payload.model_dump()))

    def update_company(self, company_id: str, payload: CompanyUpdate):
        company = self.get_company(company_id)
        return self.repo.update(company, sanitize_payload(payload.model_dump(exclude_unset=True)))

    def delete_company(self, company_id: str) -> None:
        self.repo.soft_delete(self.get_company(company_id))
