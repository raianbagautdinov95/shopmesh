from uuid import uuid4


class PaymentProvider:
    def create_intent(self, amount: str, currency: str = "USD") -> dict:
        provider_payment_id = f"pi_{uuid4().hex[:24]}"
        client_secret = f"secret_{uuid4().hex}"
        return {
            "provider": "shopmesh-pay",
            "provider_payment_id": provider_payment_id,
            "client_secret": client_secret,
            "status": "pending",
            "amount": amount,
            "currency": currency,
        }
