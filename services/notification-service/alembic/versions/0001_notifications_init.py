"""create notifications table

Revision ID: 0001_notifications_init
Revises: None
Create Date: 2026-04-06 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_notifications_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_email", sa.String(length=255), nullable=True),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column("channel", sa.String(length=32), nullable=False),
        sa.Column("template_key", sa.String(length=100), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("related_order_id", sa.Integer(), nullable=True),
        sa.Column("related_payment_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_email"), "notifications", ["user_email"], unique=False)
    op.create_index(op.f("ix_notifications_recipient"), "notifications", ["recipient"], unique=False)
    op.create_index(op.f("ix_notifications_template_key"), "notifications", ["template_key"], unique=False)
    op.create_index(op.f("ix_notifications_related_order_id"), "notifications", ["related_order_id"], unique=False)
    op.create_index(op.f("ix_notifications_related_payment_id"), "notifications", ["related_payment_id"], unique=False)
    op.create_index(op.f("ix_notifications_status"), "notifications", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_notifications_status"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_related_payment_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_related_order_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_template_key"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_recipient"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_email"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")