from pydantic import BaseModel

class OrderResource(BaseModel):
    id: str
    name: str
    status: str = "active"
