from decimal import Decimal

from app.models.cart import Cart, CartItem
from app.repositories.cart import CartRepository
from app.schemas.cart import CartItemCreateRequest, CartItemResponse, CartItemUpdateRequest, CartResponse


class CartService:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    def get_cart(self, email: str) -> CartResponse:
        cart = self.repository.get_or_create_cart(email)
        return self._to_response(cart)

    def add_item(self, email: str, payload: CartItemCreateRequest) -> CartResponse:
        cart = self.repository.get_or_create_cart(email)
        existing = self.repository.get_item_by_product_id(cart, payload.product_id)
        if existing:
            existing.quantity += payload.quantity
            existing.product_name = payload.product_name
            existing.product_slug = payload.product_slug
            existing.sku = payload.sku
            existing.unit_price = payload.unit_price
            existing.currency = payload.currency
            existing.image_url = payload.image_url
            self.repository.save(existing)
        else:
            self.repository.add_item(
                cart,
                {
                    "product_id": payload.product_id,
                    "product_name": payload.product_name,
                    "product_slug": payload.product_slug,
                    "sku": payload.sku,
                    "quantity": payload.quantity,
                    "unit_price": payload.unit_price,
                    "currency": payload.currency,
                    "image_url": payload.image_url,
                },
            )
        return self.get_cart(email)

    def update_item(self, email: str, item_id: int, payload: CartItemUpdateRequest) -> CartResponse:
        cart = self.repository.get_or_create_cart(email)
        item = self.repository.get_item(cart, item_id)
        if not item:
            raise ValueError("Cart item not found")
        item.quantity = payload.quantity
        self.repository.save(item)
        return self.get_cart(email)

    def remove_item(self, email: str, item_id: int) -> CartResponse:
        cart = self.repository.get_or_create_cart(email)
        item = self.repository.get_item(cart, item_id)
        if not item:
            raise ValueError("Cart item not found")
        self.repository.delete_item(item)
        return self.get_cart(email)

    def clear_cart(self, email: str) -> CartResponse:
        cart = self.repository.get_or_create_cart(email)
        cart = self.repository.clear_cart(cart)
        return self._to_response(cart)

    def _to_response(self, cart: Cart) -> CartResponse:
        items = [self._to_item_response(item) for item in cart.items]
        total_amount = sum((item.line_total for item in items), Decimal("0.00"))
        currency = items[0].currency if items else None
        return CartResponse(
            id=cart.id,
            user_email=cart.user_email,
            status=cart.status,
            items_count=sum(item.quantity for item in items),
            total_amount=total_amount,
            currency=currency,
            items=items,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )

    def _to_item_response(self, item: CartItem) -> CartItemResponse:
        unit_price = Decimal(str(item.unit_price))
        return CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=item.product_name,
            product_slug=item.product_slug,
            sku=item.sku,
            quantity=item.quantity,
            unit_price=unit_price,
            currency=item.currency,
            line_total=(unit_price * item.quantity).quantize(Decimal("0.01")),
            is_available=item.is_available,
            image_url=item.image_url,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
