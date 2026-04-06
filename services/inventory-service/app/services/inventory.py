from app.models.inventory import InventoryItem
from app.repositories.inventory import InventoryRepository
from app.schemas.inventory import (
    InventoryItemCreateRequest,
    InventoryItemResponse,
    InventoryItemUpdateRequest,
    InventoryListResponse,
    InventoryReleaseRequest,
    InventoryReservationRequest,
)


class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    def seed_defaults(self) -> None:
        items, total = self.repository.list_items(limit=5)
        if total > 0:
            return
        defaults = [
            {
                "product_id": 1,
                "product_name": "ShopMesh Wireless Headphones",
                "sku": "SM-HEADPHONES-01",
                "warehouse_code": "MAIN",
                "available_quantity": 25,
                "reserved_quantity": 0,
                "reorder_threshold": 5,
                "is_active": True,
            },
            {
                "product_id": 2,
                "product_name": "ShopMesh Mechanical Keyboard",
                "sku": "SM-KEYBOARD-01",
                "warehouse_code": "MAIN",
                "available_quantity": 18,
                "reserved_quantity": 0,
                "reorder_threshold": 4,
                "is_active": True,
            },
            {
                "product_id": 3,
                "product_name": "ShopMesh USB-C Dock",
                "sku": "SM-DOCK-01",
                "warehouse_code": "MAIN",
                "available_quantity": 12,
                "reserved_quantity": 0,
                "reorder_threshold": 3,
                "is_active": True,
            },
        ]
        for payload in defaults:
            self.repository.create(payload)

    def list_items(
        self, *, sku: str | None = None, product_id: int | None = None, active_only: bool = False, limit: int = 50, offset: int = 0
    ) -> InventoryListResponse:
        items, total = self.repository.list_items(
            sku=sku, product_id=product_id, active_only=active_only, limit=limit, offset=offset
        )
        return InventoryListResponse(total=total, items=[self._to_response(item) for item in items])

    def get_item(self, inventory_id: int) -> InventoryItemResponse:
        item = self.repository.get_by_id(inventory_id)
        if not item:
            raise ValueError("Inventory item not found")
        return self._to_response(item)

    def get_item_by_sku(self, sku: str) -> InventoryItemResponse:
        item = self.repository.get_by_sku(sku)
        if not item:
            raise ValueError("Inventory item not found")
        return self._to_response(item)

    def create_item(self, payload: InventoryItemCreateRequest) -> InventoryItemResponse:
        if self.repository.get_by_sku(payload.sku):
            raise ValueError("SKU already exists in inventory")
        item = self.repository.create(payload.model_dump())
        return self._to_response(item)

    def update_item(self, inventory_id: int, payload: InventoryItemUpdateRequest) -> InventoryItemResponse:
        item = self.repository.get_by_id(inventory_id)
        if not item:
            raise ValueError("Inventory item not found")
        for key, value in payload.model_dump(exclude_none=True).items():
            setattr(item, key, value)
        item = self.repository.save(item)
        return self._to_response(item)

    def reserve(self, payload: InventoryReservationRequest) -> InventoryItemResponse:
        item = self.repository.get_by_sku(payload.sku)
        if not item or not item.is_active:
            raise ValueError("Inventory item not found")
        if item.available_quantity < payload.quantity:
            raise ValueError("Insufficient stock")
        item.available_quantity -= payload.quantity
        item.reserved_quantity += payload.quantity
        item = self.repository.save(item)
        return self._to_response(item)

    def release(self, payload: InventoryReleaseRequest) -> InventoryItemResponse:
        item = self.repository.get_by_sku(payload.sku)
        if not item or not item.is_active:
            raise ValueError("Inventory item not found")
        if item.reserved_quantity < payload.quantity:
            raise ValueError("Cannot release more than reserved quantity")
        item.reserved_quantity -= payload.quantity
        item.available_quantity += payload.quantity
        item = self.repository.save(item)
        return self._to_response(item)

    def _to_response(self, item: InventoryItem) -> InventoryItemResponse:
        stock_status = "out_of_stock"
        if item.available_quantity > 0:
            stock_status = "low_stock" if item.available_quantity <= item.reorder_threshold else "in_stock"
        return InventoryItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            sku=item.sku,
            warehouse_code=item.warehouse_code,
            available_quantity=item.available_quantity,
            reserved_quantity=item.reserved_quantity,
            reorder_threshold=item.reorder_threshold,
            is_active=item.is_active,
            stock_status=stock_status,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
