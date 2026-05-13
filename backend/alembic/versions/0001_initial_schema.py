"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def audit_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.String(36), primary_key=True, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        *audit_columns(),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("Admin", "User", name="userrole"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "companies",
        *audit_columns(),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("website", sa.String(255)),
        sa.Column("phone", sa.String(64)),
        sa.Column("address", sa.Text()),
    )
    op.create_table(
        "contacts",
        *audit_columns(),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), index=True),
        sa.Column("company_id", sa.String(36), sa.ForeignKey("companies.id"), index=True),
        sa.Column("name", sa.String(255), nullable=False, index=True),
        sa.Column("designation", sa.String(255)),
        sa.Column("company_name", sa.String(255), index=True),
        sa.Column("mobile", sa.String(64), index=True),
        sa.Column("alternate_mobile", sa.String(64)),
        sa.Column("email", sa.String(255), index=True),
        sa.Column("website", sa.String(255)),
        sa.Column("address", sa.Text()),
        sa.Column("social_links", sa.Text()),
        sa.Column("tags", sa.String(500)),
        sa.Column("notes", sa.Text()),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_table(
        "scanned_cards",
        *audit_columns(),
        sa.Column("contact_id", sa.String(36), sa.ForeignKey("contacts.id"), index=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), index=True),
        sa.Column("original_file_path", sa.String(500), nullable=False),
        sa.Column("processed_file_path", sa.String(500)),
        sa.Column("raw_text", sa.Text()),
        sa.Column("status", sa.String(40), nullable=False, index=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
    )
    op.create_table(
        "ocr_logs",
        *audit_columns(),
        sa.Column("scan_id", sa.String(36), sa.ForeignKey("scanned_cards.id"), nullable=False, index=True),
        sa.Column("engine", sa.String(80), nullable=False),
        sa.Column("language", sa.String(80), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("bounding_boxes_json", sa.Text()),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "ml_models",
        *audit_columns(),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("version", sa.String(60), nullable=False, index=True),
        sa.Column("model_type", sa.String(80), nullable=False),
        sa.Column("file_path", sa.String(500)),
        sa.Column("accuracy", sa.Float()),
        sa.Column("precision", sa.Float()),
        sa.Column("recall", sa.Float()),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("metrics_json", sa.Text()),
    )
    op.create_table(
        "training_datasets",
        *audit_columns(),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("format", sa.String(20), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("metrics_json", sa.Text()),
    )
    op.create_table(
        "user_sessions",
        *audit_columns(),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("user_agent", sa.String(500)),
        sa.Column("ip_address", sa.String(64)),
    )
    op.create_table(
        "activity_logs",
        *audit_columns(),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), index=True),
        sa.Column("action", sa.String(120), nullable=False, index=True),
        sa.Column("entity_type", sa.String(80)),
        sa.Column("entity_id", sa.String(80)),
        sa.Column("metadata_json", sa.Text()),
        sa.Column("ip_address", sa.String(64)),
    )


def downgrade() -> None:
    for table in (
        "activity_logs",
        "user_sessions",
        "training_datasets",
        "ml_models",
        "ocr_logs",
        "scanned_cards",
        "contacts",
        "companies",
        "users",
    ):
        op.drop_table(table)

