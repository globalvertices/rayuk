from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: str | None
    role: str
    auth_provider: str
    avatar_url: str | None
    is_email_verified: bool
    is_identity_verified: bool
    is_contactable: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    role: str
    avatar_url: str | None
    is_identity_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    avatar_url: str | None = None


class UpdateContactableRequest(BaseModel):
    is_contactable: bool
