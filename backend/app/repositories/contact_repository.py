from datetime import date, datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.contact import Contact
from app.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Contact)

    def search_filters(
        self,
        query: str | None,
        owner_id: str | None = None,
        tag: str | None = None,
        company_id: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list:
        filters = []
        if owner_id:
            filters.append(Contact.owner_id == owner_id)
        if tag:
            filters.append(Contact.tags.ilike(f"%{tag}%"))
        if company_id:
            filters.append(Contact.company_id == company_id)
        if date_from:
            filters.append(Contact.created_at >= datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0))
        if date_to:
            filters.append(Contact.created_at <= datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59))
        if not query:
            return filters
        pattern = f"%{query}%"
        filters.append(or_(Contact.name.ilike(pattern), Contact.email.ilike(pattern), Contact.company_name.ilike(pattern)))
        return filters


class CompanyRepository(BaseRepository[Company]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, Company)

    def find_by_name(self, name: str) -> Company | None:
        stmt = select(Company).where(
            func.lower(Company.name) == name.strip().lower(),
            Company.is_deleted == False,  # noqa: E712
        )
        return self.db.scalars(stmt).first()

