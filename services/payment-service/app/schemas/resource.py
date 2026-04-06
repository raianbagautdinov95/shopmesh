from pydantic import BaseModel

class PaymentResource(BaseModel):
    id: str
    name: str
    status: str = "active"
