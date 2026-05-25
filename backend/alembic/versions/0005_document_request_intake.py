"""add document request intake fields

Revision ID: 0005_document_request_intake
Revises: 0004_setup_document_requests
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_document_request_intake"
down_revision = "0004_setup_document_requests"
branch_labels = None
depends_on = None


def columns(table_name: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def add_column_if_missing(table: str, column: sa.Column) -> None:
    if column.name not in columns(table):
        op.add_column(table, column)


def upgrade() -> None:
    add_column_if_missing("clients", sa.Column("ru_name", sa.String(length=255), nullable=True))
    add_column_if_missing("clients", sa.Column("en_name", sa.String(length=255), nullable=True))
    add_column_if_missing("clients", sa.Column("telegram_id", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("telegram_username", sa.String(length=255), nullable=True))
    add_column_if_missing("clients", sa.Column("tax_residency_country", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("passport_type", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("passport_series_number", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("passport_expires_at", sa.Date(), nullable=True))
    add_column_if_missing("clients", sa.Column("residential_address", sa.Text(), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_name", sa.String(length=255), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_account", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_corr_account", sa.String(length=64), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_bik", sa.String(length=32), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_inn", sa.String(length=32), nullable=True))
    add_column_if_missing("clients", sa.Column("bank_kpp", sa.String(length=32), nullable=True))

    op.alter_column("document_issue_requests", "deal_id", existing_type=sa.Integer(), nullable=True)
    add_column_if_missing("document_issue_requests", sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("client_type", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("document_package_type", sa.String(length=96), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("deal_type", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_number", sa.String(length=128), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_date", sa.Date(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("offer_version", sa.String(length=32), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("offer_date", sa.Date(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("total_amount", sa.Numeric(18, 2), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("full_payment_amount", sa.Numeric(18, 2), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("currency", sa.String(length=16), nullable=False, server_default="RUB"))
    add_column_if_missing("document_issue_requests", sa.Column("agent_fee_percent", sa.Numeric(9, 6), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_amount", sa.Numeric(18, 2), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("supplier_payment_equal", sa.Numeric(18, 2), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("agent_fee_amount", sa.Numeric(18, 2), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("crypto_asset", sa.String(length=32), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("wallet_address", sa.String(length=255), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_name", sa.String(length=255), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_address", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_tax_number", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_registration_number", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_bank_name", sa.String(length=255), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_bank_account", sa.String(length=128), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_bank_swift", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_corr_bank", sa.String(length=255), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_corr_bank_bik", sa.String(length=32), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_corr_account", sa.String(length=128), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("counterparty_corr_account_extra", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_basis_type", sa.String(length=64), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_basis_number", sa.String(length=128), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_basis_date", sa.Date(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payment_basis_description", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("client_comment", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("manager_comment", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("admin_comment", sa.Text(), nullable=True))
    add_column_if_missing("document_issue_requests", sa.Column("payload_json", sa.JSON(), nullable=True))


def downgrade() -> None:
    pass
