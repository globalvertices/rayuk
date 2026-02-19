from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundError
from app.models.location import Community
from app.models.property import Property
from app.models.user import User
from app.schemas.property import PropertyCreateRequest, PropertySearchParams, PropertyUpdateRequest


async def create_property(data: PropertyCreateRequest, user: User, db: AsyncSession) -> Property:
    prop = Property(
        community_id=data.community_id,
        building_id=data.building_id,
        property_type=data.property_type.value,
        unit_number=data.unit_number,
        utility_reference=data.utility_reference,
        bedrooms=data.bedrooms,
        bathrooms=data.bathrooms,
        size_sqft=data.size_sqft,
        year_built=data.year_built,
        address_line=data.address_line,
        created_by=user.id,
    )
    db.add(prop)
    await db.flush()
    return prop


async def get_property(property_id: UUID, db: AsyncSession) -> Property:
    result = await db.execute(
        select(Property)
        .options(joinedload(Property.community))
        .where(Property.id == property_id, Property.is_active.is_(True))
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise NotFoundError("Property not found")
    return prop


async def search_properties(params: PropertySearchParams, db: AsyncSession) -> tuple[list[Property], int]:
    query = select(Property).where(Property.is_active.is_(True))
    count_query = select(func.count()).select_from(Property).where(Property.is_active.is_(True))

    if params.community_id:
        query = query.where(Property.community_id == params.community_id)
        count_query = count_query.where(Property.community_id == params.community_id)

    if params.property_type:
        query = query.where(Property.property_type == params.property_type.value)
        count_query = count_query.where(Property.property_type == params.property_type.value)

    if params.bedrooms_min is not None:
        query = query.where(Property.bedrooms >= params.bedrooms_min)
        count_query = count_query.where(Property.bedrooms >= params.bedrooms_min)

    if params.bedrooms_max is not None:
        query = query.where(Property.bedrooms <= params.bedrooms_max)
        count_query = count_query.where(Property.bedrooms <= params.bedrooms_max)

    if params.q:
        search_term = f"%{params.q}%"
        query = query.where(Property.address_line.ilike(search_term))
        count_query = count_query.where(Property.address_line.ilike(search_term))

    if params.city_id:
        query = query.join(Community).where(Community.city_id == params.city_id)
        count_query = count_query.join(Community).where(Community.city_id == params.city_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (params.page - 1) * params.page_size
    query = query.order_by(Property.created_at.desc()).offset(offset).limit(params.page_size)

    result = await db.execute(query)
    properties = list(result.scalars().all())

    return properties, total


async def update_property(property_id: UUID, data: PropertyUpdateRequest, db: AsyncSession) -> Property:
    prop = await get_property(property_id, db)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prop, field, value)

    await db.flush()
    return prop
