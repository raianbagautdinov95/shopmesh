from pydantic import BaseModel

class AuthResource(BaseModel):
    id: str
    name: str
    status: str = "active"
