from pydantic import BaseModel

class InventoryResource(BaseModel):
    id: str
    name: str
    status: str = "active"
