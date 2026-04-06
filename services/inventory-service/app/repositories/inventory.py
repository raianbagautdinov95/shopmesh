from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_items(
        self,
        *,
        sku: str | None = None,
        product_id: int | None = None,
        active_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[InventoryItem], int]:
        statement = select(InventoryItem)
        count_statement = select(InventoryItem)

        if sku:
            statement = statement.where(InventoryItem.sku == sku)
            count_statement = count_statement.where(InventoryItem.sku == sku)
        if product_id is not None:
            statement = statement.where(InventoryItem.product_id == product_id)
            count_statement = count_statement.where(InventoryItem.product_id == product_id)
        if active_only:
            statement = statement.where(InventoryItem.is_active.is_(True))
            count_statement = count_statement.where(InventoryItem.is_active.is_(True))

        items = self.db.execute(statement.order_by(InventoryItem.id.desc()).limit(limit).offset(offset)).scalars().all()
        total = len(self.db.execute(count_statement).scalars().all())
        return items, total

    def get_by_id(self, inventory_id: int) -> InventoryItem | None:
        return self.db.get(InventoryItem, inventory_id)

    def get_by_sku(self, sku: str) -> InventoryItem | None:
        return self.db.execute(select(InventoryItem).where(InventoryItem.sku == sku)).scalar_one_or_none()

    def create(self, payload: dict) -> InventoryItem:
        item = InventoryItem(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save(self, item: InventoryItem) -> InventoryItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
