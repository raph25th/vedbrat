"""add manager assignment to document requests

Revision ID: 0006_document_request_manager
Revises: 0005_document_request_intake
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_document_request_manager"
down_revision = "0005_document_request_intake"
branch_labels = None
depends_on = None


def columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def upgrade() -> None:
    if "manager_id" not in columns("document_issue_requests"):
        op.add_column("document_issue_requests", sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))


def downgrade() -> None:
    pass
