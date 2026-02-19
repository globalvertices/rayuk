from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DisputeCreateRequest(BaseModel):
    property_review_id: UUID | None = None
    landlord_review_id: UUID | None = None
    reason: str = Field(min_length=20, max_length=5000)
    evidence_urls: list[str] | None = None


class DisputeResponse(BaseModel):
    id: UUID
    property_review_id: UUID | None
    landlord_review_id: UUID | None
    disputed_by: UUID
    reason: str
    evidence_urls: list[str] | None
    status: str
    admin_notes: str | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DisputeResolveRequest(BaseModel):
    status: str  # resolved_upheld, resolved_removed, dismissed
    admin_notes: str | None = None


class LandlordResponseCreateRequest(BaseModel):
    response_text: str = Field(min_length=10, max_length=3000)


class LandlordResponseResponse(BaseModel):
    id: UUID
    property_review_id: UUID | None
    landlord_review_id: UUID | None
    landlord_id: UUID
    response_text: str
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
