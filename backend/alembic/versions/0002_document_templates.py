"""add document templates

Revision ID: 0002_document_templates
Revises: 0001_initial
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_document_templates"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "document_templates" in inspector.get_table_names():
        return

    op.create_table(
        "document_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("template_type", sa.String(length=64), nullable=False),
        sa.Column("direction", sa.String(length=32), nullable=False),
        sa.Column("client_type", sa.String(length=64), nullable=False),
        sa.Column("executor_id", sa.Integer(), nullable=True),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_path", sa.String(length=512), nullable=True),
        sa.Column("file_mime_type", sa.String(length=128), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("variables_json", sa.JSON(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["executor_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_templates_id"), "document_templates", ["id"], unique=False)
    op.create_index(op.f("ix_document_templates_name"), "document_templates", ["name"], unique=False)
    op.create_index(op.f("ix_document_templates_slug"), "document_templates", ["slug"], unique=True)
    op.create_index(op.f("ix_document_templates_template_type"), "document_templates", ["template_type"], unique=False)
    op.create_index(op.f("ix_document_templates_direction"), "document_templates", ["direction"], unique=False)
    op.create_index(op.f("ix_document_templates_client_type"), "document_templates", ["client_type"], unique=False)
    op.create_index(op.f("ix_document_templates_is_active"), "document_templates", ["is_active"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "document_templates" not in inspector.get_table_names():
        return

    op.drop_index(op.f("ix_document_templates_is_active"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_client_type"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_direction"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_template_type"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_slug"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_name"), table_name="document_templates")
    op.drop_index(op.f("ix_document_templates_id"), table_name="document_templates")
    op.drop_table("document_templates")
