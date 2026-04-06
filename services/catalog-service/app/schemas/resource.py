from pydantic import BaseModel

class CatalogResource(BaseModel):
    id: str
    name: str
    status: str = "active"
