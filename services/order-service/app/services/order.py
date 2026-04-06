from decimal import Decimal

from app.events.publisher import publisher
from app.models.order import Order, OrderItem
from app.repositories.order import OrderRepository
from app.schemas.order import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdateRequest,
)


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def create_order(self, email: str, payload: OrderCreateRequest) -> OrderResponse:
        total_amount = Decimal("0.00")
        items_payload: list[dict] = []
        for item in payload.items:
            line_total = Decimal(str(item.unit_price)) * item.quantity
            total_amount += line_total
            items_payload.append(
                {
                    "product_id": item.product_id,
                    "product_name": item.product_name,
                    "product_slug": item.product_slug,
                    "sku": item.sku,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "currency": item.currency,
                }
            )

        order = self.repository.create_order(
            {
                "user_email": email,
                "status": "pending",
                "total_amount": total_amount.quantize(Decimal("0.01")),
                "currency": payload.currency,
                "notes": payload.notes,
                "items": items_payload,
            }
        )
        publisher.publish("order.created", {"order_id": order.id, "user_email": order.user_email})
        return self._to_response(order)

    def get_order(self, email: str, role: str, order_id: int) -> OrderResponse:
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if role != "admin" and order.user_email != email:
            raise PermissionError("Not enough permissions")
        return self._to_response(order)

    def list_orders(self, email: str, role: str) -> list[OrderResponse]:
        orders = self.repository.list_orders(None if role == "admin" else email)
        return [self._to_response(order) for order in orders]

    def update_status(self, role: str, order_id: int, payload: OrderStatusUpdateRequest) -> OrderResponse:
        if role != "admin":
            raise PermissionError("Not enough permissions")
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        order.status = payload.status
        order = self.repository.save(order)
        publisher.publish("order.status_updated", {"order_id": order.id, "status": order.status})
        return self._to_response(order)

    def cancel_order(self, email: str, role: str, order_id: int) -> OrderResponse:
        order = self.repository.get_order_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        if role != "admin" and order.user_email != email:
            raise PermissionError("Not enough permissions")
        if order.status in {"paid", "cancelled"}:
            raise ValueError("Order cannot be cancelled")
        order.status = "cancelled"
        order = self.repository.save(order)
        publisher.publish("order.cancelled", {"order_id": order.id, "user_email": order.user_email})
        return self._to_response(order)

    def _to_response(self, order: Order) -> OrderResponse:
        items = [self._to_item_response(item) for item in order.items]
        return OrderResponse(
            id=order.id,
            user_email=order.user_email,
            status=order.status,
            total_amount=Decimal(str(order.total_amount)),
            currency=order.currency,
            notes=order.notes,
            items_count=sum(item.quantity for item in items),
            items=items,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    def _to_item_response(self, item: OrderItem) -> OrderItemResponse:
        unit_price = Decimal(str(item.unit_price))
        return OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_slug=item.product_slug,
            sku=item.sku,
            quantity=item.quantity,
            unit_price=unit_price,
            currency=item.currency,
            line_total=(unit_price * item.quantity).quantize(Decimal("0.01")),
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
