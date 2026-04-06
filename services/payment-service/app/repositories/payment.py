from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: dict) -> Payment:
        payment = Payment(**payload)
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def save(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self.db.get(Payment, payment_id)

    def get_by_provider_payment_id(self, provider_payment_id: str) -> Payment | None:
        stmt = select(Payment).where(Payment.provider_payment_id == provider_payment_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_payments(self, *, user_email: str | None = None, order_id: int | None = None, limit: int = 50, offset: int = 0) -> tuple[list[Payment], int]:
        stmt = select(Payment).order_by(Payment.id.desc())
        if user_email:
            stmt = stmt.where(Payment.user_email == user_email.lower())
        if order_id is not None:
            stmt = stmt.where(Payment.order_id == order_id)

        items = list(self.db.execute(stmt.offset(offset).limit(limit)).scalars().all())
        total = len(list(self.db.execute(stmt).scalars().all()))
        return items, total
