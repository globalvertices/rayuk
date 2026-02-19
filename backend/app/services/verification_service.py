from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ReviewStatus, VerificationStatus
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.property import PropertyOwnershipClaim
from app.models.review import LandlordReview, PropertyReview
from app.models.verification import TenancyRecord, VerificationDocument


async def create_tenancy_record(
    tenant_id: UUID, property_id: UUID, move_in_date=None, move_out_date=None,
    is_current_tenant=False, db: AsyncSession = None,
) -> TenancyRecord:
    record = TenancyRecord(
        tenant_id=tenant_id,
        property_id=property_id,
        move_in_date=move_in_date,
        move_out_date=move_out_date,
        is_current_tenant=is_current_tenant,
    )
    db.add(record)
    await db.flush()
    return record


async def submit_verification_document(
    user_id: UUID,
    document_type: str,
    file_url: str,
    file_name: str,
    file_size_bytes: int,
    mime_type: str,
    tenancy_record_id: UUID | None = None,
    ownership_claim_id: UUID | None = None,
    db: AsyncSession = None,
) -> VerificationDocument:
    if not tenancy_record_id and not ownership_claim_id:
        raise BadRequestError("Must specify tenancy_record_id or ownership_claim_id")

    doc = VerificationDocument(
        user_id=user_id,
        tenancy_record_id=tenancy_record_id,
        ownership_claim_id=ownership_claim_id,
        document_type=document_type,
        file_url=file_url,
        file_name=file_name,
        file_size_bytes=file_size_bytes,
        mime_type=mime_type,
    )
    db.add(doc)
    await db.flush()
    return doc


async def admin_review_verification(
    doc_id: UUID, status: str, admin_id: UUID, admin_notes: str | None, db: AsyncSession
) -> VerificationDocument:
    result = await db.execute(select(VerificationDocument).where(VerificationDocument.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Verification document not found")

    doc.verification_status = status
    doc.reviewed_by = admin_id
    doc.reviewed_at = datetime.now(timezone.utc)
    doc.admin_notes = admin_notes

    # If verified, update the related record
    if status == VerificationStatus.VERIFIED.value:
        if doc.tenancy_record_id:
            tr_result = await db.execute(
                select(TenancyRecord).where(TenancyRecord.id == doc.tenancy_record_id)
            )
            tr = tr_result.scalar_one_or_none()
            if tr:
                tr.verification_status = VerificationStatus.VERIFIED.value
                tr.verified_at = datetime.now(timezone.utc)
                tr.verified_by = admin_id

                # Mark related reviews as verified and publish them
                prop_reviews = await db.execute(
                    select(PropertyReview).where(PropertyReview.tenancy_record_id == tr.id)
                )
                for review in prop_reviews.scalars():
                    review.verification_status = VerificationStatus.VERIFIED.value
                    if review.status == ReviewStatus.SUBMITTED.value:
                        review.status = ReviewStatus.PUBLISHED.value
                        review.published_at = datetime.now(timezone.utc)

                landlord_reviews = await db.execute(
                    select(LandlordReview).where(LandlordReview.tenancy_record_id == tr.id)
                )
                for review in landlord_reviews.scalars():
                    review.verification_status = VerificationStatus.VERIFIED.value
                    if review.status == ReviewStatus.SUBMITTED.value:
                        review.status = ReviewStatus.PUBLISHED.value
                        review.published_at = datetime.now(timezone.utc)

        elif doc.ownership_claim_id:
            claim_result = await db.execute(
                select(PropertyOwnershipClaim).where(PropertyOwnershipClaim.id == doc.ownership_claim_id)
            )
            claim = claim_result.scalar_one_or_none()
            if claim:
                claim.verification_status = VerificationStatus.VERIFIED.value
                claim.verified_at = datetime.now(timezone.utc)
                claim.verified_by = admin_id

    await db.flush()
    return doc


async def get_user_verifications(user_id: UUID, db: AsyncSession) -> list[VerificationDocument]:
    result = await db.execute(
        select(VerificationDocument)
        .where(VerificationDocument.user_id == user_id)
        .order_by(VerificationDocument.created_at.desc())
    )
    return list(result.scalars().all())


async def get_pending_verifications(db: AsyncSession) -> list[VerificationDocument]:
    result = await db.execute(
        select(VerificationDocument)
        .where(VerificationDocument.verification_status == VerificationStatus.PENDING.value)
        .order_by(VerificationDocument.created_at.asc())
    )
    return list(result.scalars().all())
