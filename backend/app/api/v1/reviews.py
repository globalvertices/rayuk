from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, get_review_unlock_tier, require_role
from app.models.user import User
from app.schemas.review import (
    LandlordReviewCreateRequest,
    LandlordReviewResponse,
    PropertyReviewCreateRequest,
    PropertyReviewResponse,
    PropertyReviewSnippetResponse,
    PropertyReviewSummaryResponse,
)
from app.services import review_service

router = APIRouter()


@router.post("/property", response_model=PropertyReviewResponse, status_code=201)
async def create_property_review(
    data: PropertyReviewCreateRequest,
    current_user: User = Depends(require_role(UserRole.TENANT)),
    db: AsyncSession = Depends(get_db),
):
    return await review_service.create_property_review(data, current_user, db)


@router.post("/landlord", response_model=LandlordReviewResponse, status_code=201)
async def create_landlord_review(
    data: LandlordReviewCreateRequest,
    current_user: User = Depends(require_role(UserRole.TENANT)),
    db: AsyncSession = Depends(get_db),
):
    return await review_service.create_landlord_review(data, current_user, db)


@router.get("/property/{property_id}/summary", response_model=PropertyReviewSummaryResponse)
async def get_property_review_summary(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Free tier: aggregated ratings only."""
    return await review_service.get_property_review_summary(property_id, db)


@router.get("/property/{property_id}", response_model=dict)
async def get_property_reviews(
    property_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """Access-tier gated review listing.

    - Not logged in / no unlock: excerpt + overall rating only (snippets)
    - Summary unlock: truncated review text + overall rating
    - Detailed unlock: full review text + all category ratings
    - Full unlock: everything including photos and evidence metadata
    """
    reviews, total = await review_service.get_property_reviews(property_id, db, page, page_size)

    items = []
    for r in reviews:
        # Determine unlock tier for this specific review
        unlock_tier = None
        if current_user:
            unlock_tier = await get_review_unlock_tier(r.id, current_user.id, db)

        if unlock_tier == "full":
            # Full: everything
            items.append(PropertyReviewResponse.model_validate(r).model_dump())
        elif unlock_tier == "detailed":
            # Detailed: full text + ratings, no photos
            data = PropertyReviewResponse.model_validate(r).model_dump()
            data["photos"] = []
            items.append(data)
        elif unlock_tier == "summary":
            # Summary: truncated text + overall rating, no category ratings
            data = PropertyReviewResponse.model_validate(r).model_dump()
            data["review_text"] = data["review_text"][:200] + "..." if len(data["review_text"]) > 200 else data["review_text"]
            data["photos"] = []
            for key in list(data.keys()):
                if key.startswith("rating_") and key != "overall_rating":
                    data[key] = None
            items.append(data)
        else:
            # No unlock: snippet only
            items.append(PropertyReviewSnippetResponse.model_validate(r).model_dump())

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
    }


@router.get("/my", response_model=dict)
async def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prop_reviews, landlord_reviews = await review_service.get_user_reviews(current_user.id, db)
    return {
        "property_reviews": [PropertyReviewResponse.model_validate(r).model_dump() for r in prop_reviews],
        "landlord_reviews": [LandlordReviewResponse.model_validate(r).model_dump() for r in landlord_reviews],
    }
