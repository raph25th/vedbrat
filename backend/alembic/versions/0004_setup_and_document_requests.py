"""add setup and document request workflow

Revision ID: 0004_setup_document_requests
Revises: 0003_document_template_rsi_fields
Create Date: 2026-05-24
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_setup_document_requests"
down_revision = "0003_document_template_rsi_fields"
branch_labels = None
depends_on = None


def columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def add_column_if_missing(table: str, column: sa.Column) -> None:
    if column.name not in columns(table):
        op.add_column(table, column)


def upgrade() -> None:
    add_column_if_missing("telegram_chats", sa.Column("setup_status", sa.String(length=32), nullable=False, server_default="pending_setup"))
    add_column_if_missing("telegram_chats", sa.Column("client_type", sa.String(length=64), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("deal_direction", sa.String(length=32), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("document_flow_type", sa.String(length=96), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("default_manager_id", sa.Integer(), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("default_referral_mode", sa.String(length=32), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("default_referral_id", sa.Integer(), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("rate_mode", sa.String(length=32), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("notes", sa.Text(), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("active_draft_deal_id", sa.Integer(), nullable=True))
    add_column_if_missing("telegram_chats", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False))

    add_column_if_missing("clients", sa.Column("client_type", sa.String(length=64), nullable=False, server_default="physical_person"))
    add_column_if_missing("clients", sa.Column("default_referral_enabled", sa.Boolean(), nullable=False, server_default=sa.text("0")))
    add_column_if_missing("clients", sa.Column("default_referral_id", sa.Integer(), nullable=True))
    add_column_if_missing("clients", sa.Column("default_referral_fee_type", sa.String(length=32), nullable=True))
    add_column_if_missing("clients", sa.Column("default_referral_fee_value", sa.Numeric(18, 6), nullable=True))
    add_column_if_missing("clients", sa.Column("default_referral_base", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("default_referral_comment", sa.Text(), nullable=True))

    add_column_if_missing("cfa_deals", sa.Column("client_type", sa.String(length=64), nullable=False, server_default="physical_person"))
    add_column_if_missing("cfa_deals", sa.Column("deal_direction", sa.String(length=32), nullable=False, server_default="cfa"))
    add_column_if_missing("cfa_deals", sa.Column("document_flow_type", sa.String(length=96), nullable=False, server_default="offer_join_statement"))
    add_column_if_missing("cfa_deals", sa.Column("referral_mode", sa.String(length=32), nullable=False, server_default="inherit_from_client"))
    add_column_if_missing("cfa_deals", sa.Column("referral_base", sa.String(length=64), nullable=True))
    add_column_if_missing("cfa_deals", sa.Column("referral_disabled_reason", sa.Text(), nullable=True))
    add_column_if_missing("cfa_deals", sa.Column("referral_comment", sa.Text(), nullable=True))

    add_column_if_missing("document_templates", sa.Column("document_flow_type", sa.String(length=96), nullable=True))

    if "document_issue_requests" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table(
            "document_issue_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("cfa_deals.id"), nullable=False),
            sa.Column("requested_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("requested_by_role", sa.String(length=32), nullable=True),
            sa.Column("request_source", sa.String(length=32), nullable=False),
            sa.Column("request_type", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("correction_comment", sa.Text(), nullable=True),
            sa.Column("reviewed_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("issued_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("selected_template_id", sa.Integer(), sa.ForeignKey("document_templates.id"), nullable=True),
            sa.Column("generated_document_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )

    if "generated_documents" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table(
            "generated_documents",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("cfa_deals.id"), nullable=False),
            sa.Column("template_id", sa.Integer(), sa.ForeignKey("document_templates.id"), nullable=True),
            sa.Column("issue_request_id", sa.Integer(), sa.ForeignKey("document_issue_requests.id"), nullable=True),
            sa.Column("document_type", sa.String(length=64), nullable=False),
            sa.Column("file_name", sa.String(length=255), nullable=True),
            sa.Column("file_path", sa.String(length=512), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("generated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("issued_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("signed_uploaded_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("generated_documents")
    op.drop_table("document_issue_requests")
