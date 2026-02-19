from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import DocumentType


class TenancyRecordCreateRequest(BaseModel):
    property_id: UUID
    move_in_date: date | None = None
    move_out_date: date | None = None
    is_current_tenant: bool = False


class TenancyRecordResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    property_id: UUID
    move_in_date: date | None
    move_out_date: date | None
    is_current_tenant: bool
    verification_status: str
    verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VerificationDocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    tenancy_record_id: UUID | None
    ownership_claim_id: UUID | None
    document_type: str
    file_url: str
    file_name: str
    file_size_bytes: int
    mime_type: str
    verification_status: str
    admin_notes: str | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class VerificationSubmitRequest(BaseModel):
    tenancy_record_id: UUID | None = None
    ownership_claim_id: UUID | None = None
    document_type: DocumentType


class AdminVerificationUpdateRequest(BaseModel):
    verification_status: str  # approved, rejected
    admin_notes: str | None = None
