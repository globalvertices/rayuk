from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.constants import PropertyType


class PropertyCreateRequest(BaseModel):
    community_id: UUID
    building_id: UUID | None = None
    property_type: PropertyType
    unit_number: str | None = None
    utility_reference: str | None = None
    bedrooms: int | None = Field(None, ge=0, le=20)
    bathrooms: int | None = Field(None, ge=0, le=20)
    size_sqft: int | None = Field(None, ge=0)
    year_built: int | None = Field(None, ge=1900, le=2030)
    address_line: str = Field(min_length=5, max_length=500)


class PropertyUpdateRequest(BaseModel):
    unit_number: str | None = None
    utility_reference: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    size_sqft: int | None = None
    year_built: int | None = None
    address_line: str | None = None


class PropertyResponse(BaseModel):
    id: UUID
    community_id: UUID
    building_id: UUID | None
    property_type: str
    unit_number: str | None
    utility_reference: str | None
    bedrooms: int | None
    bathrooms: int | None
    size_sqft: int | None
    year_built: int | None
    address_line: str
    avg_property_rating: float
    avg_landlord_rating: float
    review_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PropertyListResponse(BaseModel):
    id: UUID
    property_type: str
    unit_number: str | None
    bedrooms: int | None
    bathrooms: int | None
    size_sqft: int | None
    address_line: str
    avg_property_rating: float
    avg_landlord_rating: float
    review_count: int
    community_name: str | None = None
    city_name: str | None = None

    model_config = {"from_attributes": True}


class PropertySearchParams(BaseModel):
    q: str | None = None
    community_id: UUID | None = None
    city_id: UUID | None = None
    property_type: PropertyType | None = None
    bedrooms_min: int | None = None
    bedrooms_max: int | None = None
    page: int = 1
    page_size: int = 20
