from datetime import datetime

from pydantic import BaseModel, Field


class NotificationCreateRequest(BaseModel):
    recipient: str
    channel: str = Field(default="email")
    template_key: str | None = None
    subject: str | None = None
    message: str
    related_order_id: int | None = Field(default=None, gt=0)
    related_payment_id: int | None = Field(default=None, gt=0)


class NotificationStatusUpdateRequest(BaseModel):
    status: str
    failure_reason: str | None = None


class NotificationResponse(BaseModel):
    id: int
    user_email: str | None
    recipient: str
    channel: str
    template_key: str | None
    subject: str | None
    message: str
    related_order_id: int | None
    related_payment_id: int | None
    status: str
    provider_message_id: str | None
    failure_reason: str | None
    is_read: bool
    created_at: datetime
    sent_at: datetime | None


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    count: int
    limit: int
    offset: int
