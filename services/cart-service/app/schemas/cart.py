from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CartItemCreateRequest(BaseModel):
    product_id: int = Field(gt=0)
    product_name: str = Field(min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1, le=100)
    unit_price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=12)
    product_slug: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    image_url: str | None = None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class CartItemUpdateRequest(BaseModel):
    quantity: int = Field(ge=1, le=100)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_slug: str | None
    sku: str | None
    quantity: int
    unit_price: Decimal
    currency: str
    line_total: Decimal
    is_available: bool
    image_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    id: int
    user_email: str
    status: str
    items_count: int
    total_amount: Decimal
    currency: str | None
    items: list[CartItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
