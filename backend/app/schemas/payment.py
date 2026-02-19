from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import UnlockTier


class WalletResponse(BaseModel):
    user_id: UUID
    balance_credits: int

    model_config = {"from_attributes": True}


class TopupRequest(BaseModel):
    tier: str = Field(description="small, medium, or large")


class TopupCheckoutResponse(BaseModel):
    checkout_url: str
    topup_id: UUID


class PurchaseUnlockRequest(BaseModel):
    review_id: UUID
    tier: UnlockTier


class PurchaseUnlockResponse(BaseModel):
    unlock_id: UUID
    credits_charged: int
    new_balance: int


class CreateContactRequestPayment(BaseModel):
    tenant_id: UUID
    property_id: UUID
    review_id: UUID | None = None
    message: str | None = Field(None, max_length=1000)


class ContactRequestPaymentResponse(BaseModel):
    contact_request_id: UUID
    credits_charged: int
    new_balance: int


class LedgerEntryResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: int
    entry_type: str
    ref_type: str | None
    ref_id: UUID | None
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnlockResponse(BaseModel):
    id: UUID
    user_id: UUID
    review_id: UUID
    tier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UnlockCheckResponse(BaseModel):
    has_summary: bool
    has_detailed: bool
    has_full: bool
    highest_tier: str | None


class CreditPricingResponse(BaseModel):
    unlock_summary: int
    unlock_detailed: int
    unlock_full: int
    contact_request: int
    topup_small_cents: int
    topup_small_credits: int
    topup_medium_cents: int
    topup_medium_credits: int
    topup_large_cents: int
    topup_large_credits: int
