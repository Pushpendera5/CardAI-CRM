from typing import Any, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]) -> None:
        self.db = db
        self.model = model

    def get(self, record_id: str) -> ModelT | None:
        return self.db.get(self.model, record_id)

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: list[Any] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[ModelT], int]:
        stmt: Select = select(self.model).where(self.model.is_deleted == False)
        if filters:
            stmt = stmt.where(*filters)
        sort_column = getattr(self.model, sort_by, getattr(self.model, "created_at"))
        stmt = stmt.order_by(sort_column.asc() if sort_order == "asc" else sort_column.desc())
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = self.db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
        return list(rows), total

    def create(self, data: dict[str, Any]) -> ModelT:
        item = self.model(**data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update(self, item: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def soft_delete(self, item: ModelT) -> None:
        item.is_deleted = True
        self.db.commit()

