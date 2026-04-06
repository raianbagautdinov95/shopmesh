from pydantic import BaseModel

class UserResource(BaseModel):
    id: str
    name: str
    status: str = "active"
