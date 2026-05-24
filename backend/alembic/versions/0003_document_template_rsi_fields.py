"""add rsi document template fields

Revision ID: 0003_document_template_rsi_fields
Revises: 0002_document_templates
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_document_template_rsi_fields"
down_revision = "0002_document_templates"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    existing = _columns("document_templates")
    if "document_type" not in existing:
        op.add_column("document_templates", sa.Column("document_type", sa.String(length=64), nullable=True))
        op.create_index(op.f("ix_document_templates_document_type"), "document_templates", ["document_type"], unique=False)
    if "composition_type" not in existing:
        op.add_column("document_templates", sa.Column("composition_type", sa.String(length=32), nullable=False, server_default="single_document"))
        op.create_index(op.f("ix_document_templates_composition_type"), "document_templates", ["composition_type"], unique=False)
    if "original_file_name" not in existing:
        op.add_column("document_templates", sa.Column("original_file_name", sa.String(length=255), nullable=True))
    if "missing_fields_json" not in existing:
        op.add_column("document_templates", sa.Column("missing_fields_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    existing = _columns("document_templates")
    if "missing_fields_json" in existing:
        op.drop_column("document_templates", "missing_fields_json")
    if "original_file_name" in existing:
        op.drop_column("document_templates", "original_file_name")
    if "composition_type" in existing:
        op.drop_index(op.f("ix_document_templates_composition_type"), table_name="document_templates")
        op.drop_column("document_templates", "composition_type")
    if "document_type" in existing:
        op.drop_index(op.f("ix_document_templates_document_type"), table_name="document_templates")
        op.drop_column("document_templates", "document_type")
