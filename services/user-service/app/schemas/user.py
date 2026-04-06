from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    phone: str | None = None
    city: str | None = None
    bio: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    city: str | None = Field(default=None, max_length=120)
    bio: str | None = Field(default=None, max_length=500)


class UserRoleUpdateRequest(BaseModel):
    role: str = Field(min_length=4, max_length=20)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool
