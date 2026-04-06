from app.events.publisher import publisher
from app.integrations.provider import PaymentProvider
from app.models.payment import Payment
from app.repositories.payment import PaymentRepository
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentIntentResponse,
    PaymentListResponse,
    PaymentResponse,
    PaymentStatusUpdateRequest,
)


class PaymentService:
    def __init__(self, repository: PaymentRepository, provider: PaymentProvider | None = None):
        self.repository = repository
        self.provider = provider or PaymentProvider()

    def list_payments(self, user_email: str, role: str, *, order_id: int | None = None, limit: int = 50, offset: int = 0) -> PaymentListResponse:
        scoped_email = None if role == "admin" else user_email.lower()
        items, total = self.repository.list_payments(user_email=scoped_email, order_id=order_id, limit=limit, offset=offset)
        return PaymentListResponse(total=total, items=[self._to_response(item) for item in items])

    def create_payment_intent(self, user_email: str, payload: PaymentCreateRequest) -> PaymentIntentResponse:
        intent = self.provider.create_intent(amount=str(payload.amount), currency=payload.currency)
        payment = self.repository.create(
            {
                "user_email": user_email.lower(),
                "order_id": payload.order_id,
                "amount": payload.amount,
                "currency": payload.currency,
                "provider": intent["provider"],
                "provider_payment_id": intent["provider_payment_id"],
                "status": intent["status"],
                "description": payload.description,
                "failure_reason": None,
                "is_refundable": True,
            }
        )
        publisher.publish(
            "payment.intent_created",
            {
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "user_email": payment.user_email,
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
        )
        response = self._to_response(payment)
        return PaymentIntentResponse(**response.model_dump(), client_secret=intent["client_secret"])

    def get_payment(self, user_email: str, role: str, payment_id: int) -> PaymentResponse:
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        if role != "admin" and payment.user_email.lower() != user_email.lower():
            raise PermissionError("Not enough permissions to access this payment")
        return self._to_response(payment)

    def update_status(self, role: str, payment_id: int, payload: PaymentStatusUpdateRequest) -> PaymentResponse:
        if role != "admin":
            raise PermissionError("Not enough permissions to update payment status")
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise ValueError("Payment not found")
        payment.status = payload.status
        payment.failure_reason = payload.failure_reason
        payment.is_refundable = payload.status == "succeeded"
        payment = self.repository.save(payment)
        publisher.publish(
            "payment.status_updated",
            {
                "payment_id": payment.id,
                "order_id": payment.order_id,
                "status": payment.status,
                "failure_reason": payment.failure_reason,
            },
        )
        return self._to_response(payment)

    def _to_response(self, payment: Payment) -> PaymentResponse:
        return PaymentResponse(
            id=payment.id,
            user_email=payment.user_email,
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            provider=payment.provider,
            provider_payment_id=payment.provider_payment_id,
            status=payment.status,
            description=payment.description,
            failure_reason=payment.failure_reason,
            is_refundable=payment.is_refundable,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

