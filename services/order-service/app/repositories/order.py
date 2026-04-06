from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, payload: dict) -> Order:
        order = Order(
            user_email=payload["user_email"],
            status=payload["status"],
            total_amount=payload["total_amount"],
            currency=payload["currency"],
            notes=payload.get("notes"),
        )
        self.db.add(order)
        self.db.flush()

        for item in payload["items"]:
            self.db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    product_slug=item.get("product_slug"),
                    sku=item.get("sku"),
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    currency=item["currency"],
                )
            )
        self.db.commit()
        return self.get_order_by_id(order.id)

    def get_order_by_id(self, order_id: int) -> Order | None:
        stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        return self.db.scalar(stmt)

    def list_orders(self, user_email: str | None = None) -> list[Order]:
        stmt = select(Order).options(selectinload(Order.items)).order_by(Order.id.desc())
        if user_email:
            stmt = stmt.where(Order.user_email == user_email)
        return list(self.db.scalars(stmt).all())

    def save(self, order: Order) -> Order:
        self.db.add(order)
        self.db.commit()
        return self.get_order_by_id(order.id)
