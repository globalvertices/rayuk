from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import ReviewStatus, VerificationStatus
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.property import Property
from app.models.review import LandlordReview, PropertyReview
from app.models.user import User
from app.models.verification import TenancyRecord
from app.schemas.review import LandlordReviewCreateRequest, PropertyReviewCreateRequest

PROPERTY_RATING_FIELDS = [
    "rating_plumbing", "rating_electricity", "rating_water", "rating_it_cabling",
    "rating_hvac", "rating_amenity_stove", "rating_amenity_washer", "rating_amenity_fridge",
    "rating_infra_water_tank", "rating_infra_irrigation", "rating_health_dust",
    "rating_health_breathing", "rating_health_sewage",
]

LANDLORD_RATING_FIELDS = [
    "rating_responsiveness", "rating_demeanor", "rating_repair_payments",
    "rating_availability", "rating_payment_flexibility",
]


def _compute_overall(data: dict, fields: list[str]) -> float:
    values = [data[f] for f in fields if data.get(f) is not None]
    if not values:
        raise BadRequestError("At least one category rating is required")
    return round(sum(values) / len(values), 2)


def _check_min_tenancy(tenancy: TenancyRecord) -> None:
    """Enforce MIN_TENANCY_DAYS — tenant must have lived there long enough."""
    start = tenancy.move_in_date
    end = tenancy.move_out_date or date.today()
    if start and (end - start).days < settings.MIN_TENANCY_DAYS:
        raise BadRequestError(
            f"You must have lived at this property for at least {settings.MIN_TENANCY_DAYS} days to review it"
        )


async def _validate_tenancy(tenant_id: UUID, tenancy_record_id: UUID, property_id: UUID, db: AsyncSession) -> TenancyRecord:
    result = await db.execute(
        select(TenancyRecord).where(
            TenancyRecord.id == tenancy_record_id,
            TenancyRecord.tenant_id == tenant_id,
            TenancyRecord.property_id == property_id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise BadRequestError("Tenancy record not found or does not match")
    _check_min_tenancy(record)
    return record


async def create_property_review(
    data: PropertyReviewCreateRequest, user: User, db: AsyncSession
) -> PropertyReview:
    # Check for duplicate
    existing = await db.execute(
        select(PropertyReview).where(
            PropertyReview.property_id == data.property_id,
            PropertyReview.tenant_id == user.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("You have already reviewed this property")

    # Validate tenancy
    tenancy = await _validate_tenancy(user.id, data.tenancy_record_id, data.property_id, db)

    review_data = data.model_dump()
    overall = _compute_overall(review_data, PROPERTY_RATING_FIELDS)

    is_verified = tenancy.verification_status == VerificationStatus.VERIFIED.value
    excerpt = data.public_excerpt or data.review_text[:200]

    review = PropertyReview(
        property_id=data.property_id,
        tenant_id=user.id,
        tenancy_record_id=data.tenancy_record_id,
        overall_rating=overall,
        review_text=data.review_text,
        public_excerpt=excerpt,
        status=ReviewStatus.SUBMITTED.value,
        verification_status=VerificationStatus.VERIFIED.value if is_verified else VerificationStatus.UNVERIFIED.value,
        published_at=datetime.now(timezone.utc) if is_verified else None,
        **{f: review_data[f] for f in PROPERTY_RATING_FIELDS},
    )
    # Auto-publish if verified, otherwise stays as submitted pending moderation
    if is_verified:
        review.status = ReviewStatus.PUBLISHED.value

    db.add(review)
    await db.flush()

    # Update property aggregate ratings if published
    if review.status == ReviewStatus.PUBLISHED.value:
        await _update_property_ratings(data.property_id, db)

    return review


async def submit_review(review_id: UUID, user_id: UUID, db: AsyncSession) -> PropertyReview:
    """Move a draft review to submitted."""
    result = await db.execute(select(PropertyReview).where(PropertyReview.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundError("Review not found")
    if review.tenant_id != user_id:
        raise BadRequestError("Not your review")
    if review.status != ReviewStatus.DRAFT.value:
        raise BadRequestError("Review is not in draft state")
    review.status = ReviewStatus.SUBMITTED.value
    await db.flush()
    return review


async def publish_review(review_id: UUID, db: AsyncSession) -> PropertyReview:
    """Admin publishes a submitted review."""
    result = await db.execute(select(PropertyReview).where(PropertyReview.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundError("Review not found")
    if review.status != ReviewStatus.SUBMITTED.value:
        raise BadRequestError("Review must be in submitted state to publish")
    review.status = ReviewStatus.PUBLISHED.value
    review.published_at = datetime.now(timezone.utc)
    await db.flush()
    await _update_property_ratings(review.property_id, db)
    return review


async def create_landlord_review(
    data: LandlordReviewCreateRequest, user: User, db: AsyncSession
) -> LandlordReview:
    existing = await db.execute(
        select(LandlordReview).where(
            LandlordReview.landlord_id == data.landlord_id,
            LandlordReview.tenant_id == user.id,
            LandlordReview.property_id == data.property_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("You have already reviewed this landlord for this property")

    tenancy = await _validate_tenancy(user.id, data.tenancy_record_id, data.property_id, db)

    review_data = data.model_dump()
    overall = _compute_overall(review_data, LANDLORD_RATING_FIELDS)

    is_verified = tenancy.verification_status == VerificationStatus.VERIFIED.value

    review = LandlordReview(
        landlord_id=data.landlord_id,
        tenant_id=user.id,
        property_id=data.property_id,
        tenancy_record_id=data.tenancy_record_id,
        overall_rating=overall,
        review_text=data.review_text,
        status=ReviewStatus.SUBMITTED.value,
        verification_status=VerificationStatus.VERIFIED.value if is_verified else VerificationStatus.UNVERIFIED.value,
        published_at=datetime.now(timezone.utc) if is_verified else None,
        **{f: review_data[f] for f in LANDLORD_RATING_FIELDS},
    )
    if is_verified:
        review.status = ReviewStatus.PUBLISHED.value

    db.add(review)
    await db.flush()

    if review.status == ReviewStatus.PUBLISHED.value:
        await _update_landlord_ratings(data.property_id, db)

    return review


async def get_property_review_summary(property_id: UUID, db: AsyncSession) -> dict:
    """Free tier: aggregate ratings only."""
    base = select(
        func.count().label("review_count"),
        func.avg(PropertyReview.overall_rating).label("avg_overall"),
        *[func.avg(getattr(PropertyReview, f)).label(f"avg_{f.replace('rating_', '')}") for f in PROPERTY_RATING_FIELDS],
    ).where(
        PropertyReview.property_id == property_id,
        PropertyReview.status == ReviewStatus.PUBLISHED.value,
    )

    result = await db.execute(base)
    row = result.one()

    return {
        "property_id": property_id,
        "review_count": row.review_count or 0,
        "avg_overall": float(row.avg_overall or 0),
        **{f"avg_{f.replace('rating_', '')}": float(getattr(row, f"avg_{f.replace('rating_', '')}") or 0) for f in PROPERTY_RATING_FIELDS},
    }


async def get_property_reviews(
    property_id: UUID, db: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[PropertyReview], int]:
    count_result = await db.execute(
        select(func.count()).select_from(PropertyReview).where(
            PropertyReview.property_id == property_id,
            PropertyReview.status == ReviewStatus.PUBLISHED.value,
        )
    )
    total = count_result.scalar()

    offset = (page - 1) * page_size
    result = await db.execute(
        select(PropertyReview)
        .where(PropertyReview.property_id == property_id, PropertyReview.status == ReviewStatus.PUBLISHED.value)
        .order_by(PropertyReview.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    reviews = list(result.scalars().all())

    return reviews, total


async def get_user_reviews(user_id: UUID, db: AsyncSession) -> tuple[list[PropertyReview], list[LandlordReview]]:
    prop_result = await db.execute(
        select(PropertyReview).where(PropertyReview.tenant_id == user_id).order_by(PropertyReview.created_at.desc())
    )
    landlord_result = await db.execute(
        select(LandlordReview).where(LandlordReview.tenant_id == user_id).order_by(LandlordReview.created_at.desc())
    )
    return list(prop_result.scalars().all()), list(landlord_result.scalars().all())


async def _update_property_ratings(property_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(
            func.avg(PropertyReview.overall_rating),
            func.count(),
        ).where(
            PropertyReview.property_id == property_id,
            PropertyReview.status == ReviewStatus.PUBLISHED.value,
        )
    )
    avg_rating, count = result.one()

    prop_result = await db.execute(select(Property).where(Property.id == property_id))
    prop = prop_result.scalar_one_or_none()
    if prop:
        prop.avg_property_rating = float(avg_rating or 0)
        prop.review_count = count or 0


async def _update_landlord_ratings(property_id: UUID, db: AsyncSession) -> None:
    result = await db.execute(
        select(func.avg(LandlordReview.overall_rating)).where(
            LandlordReview.property_id == property_id,
            LandlordReview.status == ReviewStatus.PUBLISHED.value,
        )
    )
    avg_rating = result.scalar()

    prop_result = await db.execute(select(Property).where(Property.id == property_id))
    prop = prop_result.scalar_one_or_none()
    if prop:
        prop.avg_landlord_rating = float(avg_rating or 0)
