from pydantic import BaseModel

class CartResource(BaseModel):
    id: str
    name: str
    status: str = "active"
