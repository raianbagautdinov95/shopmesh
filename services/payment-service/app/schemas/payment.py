from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class PaymentCreateRequest(BaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PaymentStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=3, max_length=32)
    failure_reason: str | None = Field(default=None, max_length=1000)

    @field_validator("status")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        return value.lower()


class PaymentResponse(BaseModel):
    id: int
    user_email: str
    order_id: int
    amount: Decimal
    currency: str
    provider: str
    provider_payment_id: str
    status: str
    description: str | None
    failure_reason: str | None
    is_refundable: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentIntentResponse(PaymentResponse):
    client_secret: str


class PaymentListResponse(BaseModel):
    total: int
    items: list[PaymentResponse]
