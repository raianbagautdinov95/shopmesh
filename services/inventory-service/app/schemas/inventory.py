from datetime import datetime

from pydantic import BaseModel, Field


class InventoryItemBase(BaseModel):
    product_id: int
    product_name: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    warehouse_code: str = Field(default="MAIN", min_length=1, max_length=64)
    reorder_threshold: int = Field(default=0, ge=0)
    is_active: bool = True


class InventoryItemCreateRequest(InventoryItemBase):
    available_quantity: int = Field(default=0, ge=0)
    reserved_quantity: int = Field(default=0, ge=0)


class InventoryItemUpdateRequest(BaseModel):
    product_name: str | None = Field(default=None, min_length=1, max_length=255)
    warehouse_code: str | None = Field(default=None, min_length=1, max_length=64)
    available_quantity: int | None = Field(default=None, ge=0)
    reserved_quantity: int | None = Field(default=None, ge=0)
    reorder_threshold: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class InventoryReservationRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1)
    order_id: int | None = None


class InventoryReleaseRequest(BaseModel):
    sku: str = Field(min_length=1, max_length=100)
    quantity: int = Field(ge=1)
    order_id: int | None = None


class InventoryItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    sku: str
    warehouse_code: str
    available_quantity: int
    reserved_quantity: int
    reorder_threshold: int
    is_active: bool
    stock_status: str
    created_at: datetime
    updated_at: datetime


class InventoryListResponse(BaseModel):
    total: int
    items: list[InventoryItemResponse]
