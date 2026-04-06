class PaymentEventPublisher:
    def publish(self, event_name: str, payload: dict) -> dict:
        return {"event": event_name, "payload": payload}


publisher = PaymentEventPublisher()
