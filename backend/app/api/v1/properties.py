from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import PropertyType, UserRole
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models.location import City, Community
from app.models.property import Property, PropertyOwnershipClaim
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.property import (
    PropertyCreateRequest,
    PropertyListResponse,
    PropertyResponse,
    PropertySearchParams,
    PropertyUpdateRequest,
)
from app.services import property_service

router = APIRouter()


@router.get("", response_model=dict)
async def search_properties(
    q: str | None = None,
    community_id: UUID | None = None,
    city_id: UUID | None = None,
    property_type: PropertyType | None = None,
    bedrooms_min: int | None = None,
    bedrooms_max: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    params = PropertySearchParams(
        q=q, community_id=community_id, city_id=city_id,
        property_type=property_type, bedrooms_min=bedrooms_min,
        bedrooms_max=bedrooms_max, page=page, page_size=page_size,
    )
    properties, total = await property_service.search_properties(params, db)

    items = []
    for p in properties:
        item = PropertyListResponse.model_validate(p)
        # Enrich with community/city names
        if p.community_id:
            comm_result = await db.execute(select(Community).where(Community.id == p.community_id))
            comm = comm_result.scalar_one_or_none()
            if comm:
                item.community_name = comm.name
                city_result = await db.execute(select(City).where(City.id == comm.city_id))
                city = city_result.scalar_one_or_none()
                if city:
                    item.city_name = city.name
        items.append(item)

    return {
        "items": [i.model_dump() for i in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(property_id: UUID, db: AsyncSession = Depends(get_db)):
    return await property_service.get_property(property_id, db)


@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(
    data: PropertyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await property_service.create_property(data, current_user, db)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    data: PropertyUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await property_service.update_property(property_id, data, db)


@router.post("/{property_id}/claim", response_model=MessageResponse, status_code=201)
async def claim_property(
    property_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.LANDLORD.value:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Only landlords can claim properties")

    # Check existing claim
    existing = await db.execute(
        select(PropertyOwnershipClaim).where(
            PropertyOwnershipClaim.property_id == property_id,
            PropertyOwnershipClaim.landlord_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none():
        from app.core.exceptions import ConflictError
        raise ConflictError("You have already claimed this property")

    claim = PropertyOwnershipClaim(
        property_id=property_id,
        landlord_id=current_user.id,
    )
    db.add(claim)
    return MessageResponse(message="Ownership claim submitted. Please upload verification documents.")


# Location endpoints (convenience)
@router.get("/locations/communities/search")
async def search_communities(
    q: str = Query(min_length=2),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Community)
        .where(Community.name.ilike(f"%{q}%"), Community.is_active.is_(True))
        .limit(20)
    )
    communities = result.scalars().all()
    return [{"id": str(c.id), "name": c.name, "slug": c.slug} for c in communities]
