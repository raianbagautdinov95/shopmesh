"""create inventory_items table

Revision ID: 0001_create_inventory_items
Revises:
Create Date: 2026-04-06 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_inventory_items"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("warehouse_code", sa.String(length=64), nullable=False),
        sa.Column("available_quantity", sa.Integer(), nullable=False),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False),
        sa.Column("reorder_threshold", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_items_id"), "inventory_items", ["id"], unique=False)
    op.create_index(op.f("ix_inventory_items_product_id"), "inventory_items", ["product_id"], unique=False)
    op.create_index(op.f("ix_inventory_items_sku"), "inventory_items", ["sku"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_items_sku"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_product_id"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_id"), table_name="inventory_items")
    op.drop_table("inventory_items")