from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cart import Cart, CartItem


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cart_by_email(self, email: str) -> Cart | None:
        stmt = select(Cart).options(selectinload(Cart.items)).where(Cart.user_email == email.lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def create_cart(self, email: str) -> Cart:
        cart = Cart(user_email=email.lower())
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return self.get_cart_by_email(email) or cart

    def get_or_create_cart(self, email: str) -> Cart:
        cart = self.get_cart_by_email(email)
        if cart:
            return cart
        return self.create_cart(email)

    def get_item(self, cart: Cart, item_id: int) -> CartItem | None:
        for item in cart.items:
            if item.id == item_id:
                return item
        return None

    def get_item_by_product_id(self, cart: Cart, product_id: int) -> CartItem | None:
        for item in cart.items:
            if item.product_id == product_id:
                return item
        return None

    def add_item(self, cart: Cart, payload: dict) -> CartItem:
        item = CartItem(cart_id=cart.id, **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def save(self, instance: Cart | CartItem) -> Cart | CartItem:
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete_item(self, item: CartItem) -> None:
        self.db.delete(item)
        self.db.commit()

    def clear_cart(self, cart: Cart) -> Cart:
        for item in list(cart.items):
            self.db.delete(item)
        self.db.commit()
        return self.get_cart_by_email(cart.user_email) or cart
