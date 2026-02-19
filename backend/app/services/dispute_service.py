from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DisputeStatus, ReviewStatus
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.dispute import LandlordResponse, ReviewDispute
from app.models.review import LandlordReview, PropertyReview
from app.utils.profanity import check_profanity


async def create_dispute(
    disputed_by: UUID,
    reason: str,
    property_review_id: UUID | None = None,
    landlord_review_id: UUID | None = None,
    evidence_urls: list[str] | None = None,
    db: AsyncSession = None,
) -> ReviewDispute:
    if not property_review_id and not landlord_review_id:
        raise BadRequestError("Must specify a review to dispute")

    query = select(ReviewDispute).where(ReviewDispute.disputed_by == disputed_by)
    if property_review_id:
        query = query.where(ReviewDispute.property_review_id == property_review_id)
    if landlord_review_id:
        query = query.where(ReviewDispute.landlord_review_id == landlord_review_id)

    existing = await db.execute(query)
    if existing.scalar_one_or_none():
        raise ConflictError("You have already disputed this review")

    # Move the review into disputed state
    if property_review_id:
        rev_result = await db.execute(select(PropertyReview).where(PropertyReview.id == property_review_id))
        review = rev_result.scalar_one_or_none()
        if review and review.status == ReviewStatus.PUBLISHED.value:
            review.status = ReviewStatus.DISPUTED.value
    elif landlord_review_id:
        rev_result = await db.execute(select(LandlordReview).where(LandlordReview.id == landlord_review_id))
        review = rev_result.scalar_one_or_none()
        if review and review.status == ReviewStatus.PUBLISHED.value:
            review.status = ReviewStatus.DISPUTED.value

    dispute = ReviewDispute(
        property_review_id=property_review_id,
        landlord_review_id=landlord_review_id,
        disputed_by=disputed_by,
        reason=reason,
        evidence_urls=evidence_urls,
    )
    db.add(dispute)
    await db.flush()
    return dispute


async def resolve_dispute(
    dispute_id: UUID, status: str, admin_id: UUID, admin_notes: str | None, db: AsyncSession
) -> ReviewDispute:
    result = await db.execute(select(ReviewDispute).where(ReviewDispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise NotFoundError("Dispute not found")

    dispute.status = status
    dispute.resolved_by = admin_id
    dispute.resolved_at = datetime.now(timezone.utc)
    dispute.admin_notes = admin_notes

    # upheld -> remove the review
    if status == DisputeStatus.UPHELD.value:
        if dispute.property_review_id:
            rev_result = await db.execute(
                select(PropertyReview).where(PropertyReview.id == dispute.property_review_id)
            )
            review = rev_result.scalar_one_or_none()
            if review:
                review.status = ReviewStatus.REMOVED.value
                review.is_flagged = True
        elif dispute.landlord_review_id:
            rev_result = await db.execute(
                select(LandlordReview).where(LandlordReview.id == dispute.landlord_review_id)
            )
            review = rev_result.scalar_one_or_none()
            if review:
                review.status = ReviewStatus.REMOVED.value
                review.is_flagged = True

    # rejected -> restore the review to published
    elif status == DisputeStatus.REJECTED.value:
        if dispute.property_review_id:
            rev_result = await db.execute(
                select(PropertyReview).where(PropertyReview.id == dispute.property_review_id)
            )
            review = rev_result.scalar_one_or_none()
            if review:
                review.status = ReviewStatus.PUBLISHED.value
        elif dispute.landlord_review_id:
            rev_result = await db.execute(
                select(LandlordReview).where(LandlordReview.id == dispute.landlord_review_id)
            )
            review = rev_result.scalar_one_or_none()
            if review:
                review.status = ReviewStatus.PUBLISHED.value

    # partially_upheld -> some fields hidden (keep as disputed with notes)
    elif status == DisputeStatus.PARTIALLY_UPHELD.value:
        pass  # Admin notes describe what was hidden

    await db.flush()
    return dispute


async def create_landlord_response(
    landlord_id: UUID,
    response_text: str,
    property_review_id: UUID | None = None,
    landlord_review_id: UUID | None = None,
    db: AsyncSession = None,
) -> LandlordResponse:
    if not property_review_id and not landlord_review_id:
        raise BadRequestError("Must specify a review to respond to")

    # Profanity filter
    if check_profanity(response_text):
        raise BadRequestError("Response contains inappropriate language. Please revise.")

    # Check for existing response
    query = select(LandlordResponse).where(LandlordResponse.landlord_id == landlord_id)
    if property_review_id:
        query = query.where(LandlordResponse.property_review_id == property_review_id)
    if landlord_review_id:
        query = query.where(LandlordResponse.landlord_review_id == landlord_review_id)

    existing = await db.execute(query)
    if existing.scalar_one_or_none():
        raise ConflictError("You have already responded to this review")

    response = LandlordResponse(
        property_review_id=property_review_id,
        landlord_review_id=landlord_review_id,
        landlord_id=landlord_id,
        response_text=response_text,
    )
    db.add(response)
    await db.flush()
    return response


async def get_user_disputes(user_id: UUID, db: AsyncSession) -> list[ReviewDispute]:
    result = await db.execute(
        select(ReviewDispute)
        .where(ReviewDispute.disputed_by == user_id)
        .order_by(ReviewDispute.created_at.desc())
    )
    return list(result.scalars().all())


async def get_open_disputes(db: AsyncSession) -> list[ReviewDispute]:
    result = await db.execute(
        select(ReviewDispute)
        .where(ReviewDispute.status.in_([DisputeStatus.OPEN.value, DisputeStatus.UNDER_REVIEW.value]))
        .order_by(ReviewDispute.created_at.asc())
    )
    return list(result.scalars().all())
