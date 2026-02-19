from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


def _rating_field():
    return Field(None, ge=1, le=5)


class PropertyReviewCreateRequest(BaseModel):
    property_id: UUID
    tenancy_record_id: UUID
    rating_plumbing: int | None = _rating_field()
    rating_electricity: int | None = _rating_field()
    rating_water: int | None = _rating_field()
    rating_it_cabling: int | None = _rating_field()
    rating_hvac: int | None = _rating_field()
    rating_amenity_stove: int | None = _rating_field()
    rating_amenity_washer: int | None = _rating_field()
    rating_amenity_fridge: int | None = _rating_field()
    rating_infra_water_tank: int | None = _rating_field()
    rating_infra_irrigation: int | None = _rating_field()
    rating_health_dust: int | None = _rating_field()
    rating_health_breathing: int | None = _rating_field()
    rating_health_sewage: int | None = _rating_field()
    review_text: str = Field(min_length=20, max_length=5000)
    public_excerpt: str | None = Field(None, max_length=300)


class PropertyReviewResponse(BaseModel):
    id: UUID
    property_id: UUID
    tenant_id: UUID
    rating_plumbing: int | None
    rating_electricity: int | None
    rating_water: int | None
    rating_it_cabling: int | None
    rating_hvac: int | None
    rating_amenity_stove: int | None
    rating_amenity_washer: int | None
    rating_amenity_fridge: int | None
    rating_infra_water_tank: int | None
    rating_infra_irrigation: int | None
    rating_health_dust: int | None
    rating_health_breathing: int | None
    rating_health_sewage: int | None
    overall_rating: float
    review_text: str
    public_excerpt: str | None
    status: str
    verification_status: str
    is_flagged: bool
    published_at: datetime | None
    created_at: datetime
    photos: list["PhotoResponse"] = []

    model_config = {"from_attributes": True}


class PropertyReviewSnippetResponse(BaseModel):
    """Free tier: excerpt + aggregated scores only, no detailed text."""
    id: UUID
    property_id: UUID
    overall_rating: float
    public_excerpt: str | None
    status: str
    verification_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PropertyReviewSummaryResponse(BaseModel):
    """Free tier: just averages and count."""
    property_id: UUID
    review_count: int
    avg_overall: float
    avg_plumbing: float | None
    avg_electricity: float | None
    avg_water: float | None
    avg_it_cabling: float | None
    avg_hvac: float | None
    avg_amenity_stove: float | None
    avg_amenity_washer: float | None
    avg_amenity_fridge: float | None
    avg_infra_water_tank: float | None
    avg_infra_irrigation: float | None
    avg_health_dust: float | None
    avg_health_breathing: float | None
    avg_health_sewage: float | None


class LandlordReviewCreateRequest(BaseModel):
    landlord_id: UUID
    property_id: UUID
    tenancy_record_id: UUID
    rating_responsiveness: int | None = _rating_field()
    rating_demeanor: int | None = _rating_field()
    rating_repair_payments: int | None = _rating_field()
    rating_availability: int | None = _rating_field()
    rating_payment_flexibility: int | None = _rating_field()
    review_text: str = Field(min_length=20, max_length=5000)


class LandlordReviewResponse(BaseModel):
    id: UUID
    landlord_id: UUID
    tenant_id: UUID
    property_id: UUID
    rating_responsiveness: int | None
    rating_demeanor: int | None
    rating_repair_payments: int | None
    rating_availability: int | None
    rating_payment_flexibility: int | None
    overall_rating: float
    review_text: str
    status: str
    verification_status: str
    is_flagged: bool
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PhotoResponse(BaseModel):
    id: UUID
    file_url: str
    file_name: str
    sort_order: int

    model_config = {"from_attributes": True}
