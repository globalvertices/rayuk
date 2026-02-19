from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContactRequestResponse(BaseModel):
    id: UUID
    requester_id: UUID
    tenant_id: UUID
    property_id: UUID
    review_id: UUID | None
    status: str
    message: str | None
    responded_at: datetime | None
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactRequestUpdateRequest(BaseModel):
    status: str  # accepted, declined


class MessageCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: UUID
    thread_id: UUID
    sender_id: UUID
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportCreateRequest(BaseModel):
    target_type: str  # review, landlord_response, message
    target_id: UUID
    reason: str = Field(min_length=10, max_length=2000)


class ReportResponse(BaseModel):
    id: UUID
    reporter_user_id: UUID
    target_type: str
    target_id: UUID
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}
