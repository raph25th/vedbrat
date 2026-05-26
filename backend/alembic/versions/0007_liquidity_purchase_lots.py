"""add liquidity purchase lots

Revision ID: 0007_liquidity_purchase_lots
Revises: 0006_document_request_manager
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_liquidity_purchase_lots"
down_revision = "0006_document_request_manager"
branch_labels = None
depends_on = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    existing = table_names()
    if "liquidity_purchase_lots" not in existing:
        op.create_table(
            "liquidity_purchase_lots",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("asset", sa.String(length=32), nullable=False, server_default="USDT"),
            sa.Column("purchase_amount_rub", sa.Numeric(18, 2), nullable=False, server_default="0"),
            sa.Column("purchase_rate", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("purchased_asset_volume", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("used_asset_volume", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("remaining_asset_volume", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
            sa.Column("source", sa.String(length=128), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_liquidity_purchase_lots_asset", "liquidity_purchase_lots", ["asset"])
        op.create_index("ix_liquidity_purchase_lots_status", "liquidity_purchase_lots", ["status"])

    existing = table_names()
    if "liquidity_lot_allocations" not in existing:
        op.create_table(
            "liquidity_lot_allocations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("lot_id", sa.Integer(), sa.ForeignKey("liquidity_purchase_lots.id"), nullable=False),
            sa.Column("deal_id", sa.Integer(), sa.ForeignKey("cfa_deals.id"), nullable=False),
            sa.Column("asset", sa.String(length=32), nullable=False, server_default="USDT"),
            sa.Column("asset_volume", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("allocation_rate", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("cost_basis_rub", sa.Numeric(18, 2), nullable=False, server_default="0"),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        )
        op.create_index("ix_liquidity_lot_allocations_lot_id", "liquidity_lot_allocations", ["lot_id"])
        op.create_index("ix_liquidity_lot_allocations_deal_id", "liquidity_lot_allocations", ["deal_id"])
        op.create_index("ix_liquidity_lot_allocations_asset", "liquidity_lot_allocations", ["asset"])


def downgrade() -> None:
    pass
