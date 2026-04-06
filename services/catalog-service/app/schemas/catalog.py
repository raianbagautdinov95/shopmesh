from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    currency: str
    is_active: bool
    stock_status: str
    image_url: str | None = None
    category: CategoryResponse
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ProductResponse]


class CategoryListResponse(BaseModel):
    total: int
    items: list[CategoryResponse]


class ProductCreateRequest(BaseModel):
    sku: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    category_slug: str = Field(min_length=2, max_length=120)
    stock_status: str = Field(default="in_stock", min_length=2, max_length=50)
    image_url: str | None = None
    is_active: bool = True


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=8)
    category_slug: str | None = Field(default=None, min_length=2, max_length=120)
    stock_status: str | None = Field(default=None, min_length=2, max_length=50)
    image_url: str | None = None
    is_active: bool | None = None


class CategoryCreateRequest(BaseModel):
    slug: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
