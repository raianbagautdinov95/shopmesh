from pydantic import BaseModel

class NotificationResource(BaseModel):
    id: str
    name: str
    status: str = "active"
