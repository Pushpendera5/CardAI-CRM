from __future__ import annotations

from io import BytesIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact import Contact


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def contacts_dataframe(self, owner_id: str | None = None, search: str | None = None, tag: str | None = None, date_from=None, date_to=None):
        import pandas as pd
        from datetime import datetime
        from sqlalchemy import or_, func

        stmt = select(Contact).where(Contact.is_deleted == False)
        if owner_id:
            stmt = stmt.where(Contact.owner_id == owner_id)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Contact.name.ilike(pattern), Contact.email.ilike(pattern), Contact.company_name.ilike(pattern))
            )
        if tag:
            stmt = stmt.where(Contact.tags.ilike(f"%{tag}%"))
        if date_from:
            stmt = stmt.where(Contact.created_at >= datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0))
        if date_to:
            stmt = stmt.where(Contact.created_at <= datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59))
        rows = self.db.scalars(stmt).all()
        return pd.DataFrame(
            [
                {
                    "Name": row.name,
                    "Designation": row.designation,
                    "Company": row.company_name,
                    "Mobile": row.mobile,
                    "Email": row.email,
                    "Website": row.website,
                    "Address": row.address,
                    "Tags": row.tags,
                }
                for row in rows
            ]
        )

    def csv_bytes(self, owner_id: str | None = None, search: str | None = None, tag: str | None = None, date_from=None, date_to=None) -> bytes:
        return self.contacts_dataframe(owner_id=owner_id, search=search, tag=tag, date_from=date_from, date_to=date_to).to_csv(index=False).encode("utf-8")

    def excel_bytes(self, owner_id: str | None = None, search: str | None = None, tag: str | None = None, date_from=None, date_to=None) -> bytes:
        import pandas as pd

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            self.contacts_dataframe(owner_id=owner_id, search=search, tag=tag, date_from=date_from, date_to=date_to).to_excel(writer, index=False, sheet_name="Contacts")
        return output.getvalue()

    def pdf_bytes(self, owner_id: str | None = None) -> bytes:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        output = BytesIO()
        pdf = canvas.Canvas(output, pagesize=letter)
        y = 760
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, y, "CardAI CRM Contacts")
        y -= 30
        pdf.setFont("Helvetica", 9)
        for row in self.contacts_dataframe(owner_id=owner_id).fillna("").to_dict("records"):
            line = f"{row['Name']} | {row['Company']} | {row['Mobile']} | {row['Email']}"
            pdf.drawString(40, y, line[:110])
            y -= 16
            if y < 50:
                pdf.showPage()
                y = 760
        pdf.save()
        return output.getvalue()

