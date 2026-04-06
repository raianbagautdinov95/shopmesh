from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class OrderItemCreateRequest(BaseModel):
    product_id: int = Field(gt=0)
    product_name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1, le=100)
    unit_price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    product_slug: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, max_length=100)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class OrderCreateRequest(BaseModel):
    items: list[OrderItemCreateRequest] = Field(min_length=1)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class OrderStatusUpdateRequest(BaseModel):
    status: str = Field(min_length=3, max_length=32)

    @field_validator("status")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        return value.lower()


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_slug: str | None
    sku: str | None
    quantity: int
    unit_price: Decimal
    currency: str
    line_total: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int
    user_email: str
    status: str
    total_amount: Decimal
    currency: str
    notes: str | None
    items_count: int
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
