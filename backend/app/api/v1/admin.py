from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.database import get_db
from app.dependencies import require_role
from app.models.payment import LedgerEntry, StripeTopup
from app.models.review import LandlordReview, PropertyReview
from app.models.user import User
from app.schemas.dispute import DisputeResolveRequest, DisputeResponse
from app.schemas.message import ReportResponse
from app.schemas.verification import AdminVerificationUpdateRequest, VerificationDocumentResponse
from app.services import dispute_service, message_service, review_service, verification_service

router = APIRouter()


@router.get("/verifications", response_model=list[VerificationDocumentResponse])
async def get_pending_verifications(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await verification_service.get_pending_verifications(db)


@router.patch("/verifications/{doc_id}", response_model=VerificationDocumentResponse)
async def review_verification(
    doc_id: UUID,
    data: AdminVerificationUpdateRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await verification_service.admin_review_verification(
        doc_id=doc_id,
        status=data.verification_status,
        admin_id=current_user.id,
        admin_notes=data.admin_notes,
        db=db,
    )


@router.get("/disputes", response_model=list[DisputeResponse])
async def get_open_disputes(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await dispute_service.get_open_disputes(db)


@router.patch("/disputes/{dispute_id}", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: UUID,
    data: DisputeResolveRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await dispute_service.resolve_dispute(
        dispute_id=dispute_id,
        status=data.status,
        admin_id=current_user.id,
        admin_notes=data.admin_notes,
        db=db,
    )


@router.post("/reviews/{review_id}/publish")
async def admin_publish_review(
    review_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    review = await review_service.publish_review(review_id, db)
    return {"status": "published", "review_id": str(review.id)}


@router.get("/reports", response_model=list[ReportResponse])
async def get_reports(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.get_reports(db)


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    users_count = (await db.execute(select(func.count()).select_from(User))).scalar()
    prop_reviews_count = (await db.execute(select(func.count()).select_from(PropertyReview))).scalar()
    landlord_reviews_count = (await db.execute(select(func.count()).select_from(LandlordReview))).scalar()
    total_topups = (
        await db.execute(
            select(func.sum(StripeTopup.amount_cents)).where(StripeTopup.status == "completed")
        )
    ).scalar()

    return {
        "total_users": users_count,
        "total_property_reviews": prop_reviews_count,
        "total_landlord_reviews": landlord_reviews_count,
        "total_revenue_cents": total_topups or 0,
    }
