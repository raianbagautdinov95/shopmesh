from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationChannel(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"
    webhook = "webhook"


class NotificationStatus(str, Enum):
    queued = "queued"
    sent = "sent"
    failed = "failed"
    cancelled = "cancelled"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    recipient: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, default=NotificationChannel.email.value)
    template_key: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    related_order_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    related_payment_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=NotificationStatus.queued.value, index=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
