from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.dispute import (
    DisputeCreateRequest,
    DisputeResponse,
    LandlordResponseCreateRequest,
    LandlordResponseResponse,
)
from app.services import dispute_service

router = APIRouter()


@router.post("", response_model=DisputeResponse, status_code=201)
async def create_dispute(
    data: DisputeCreateRequest,
    current_user: User = Depends(require_role(UserRole.LANDLORD)),
    db: AsyncSession = Depends(get_db),
):
    return await dispute_service.create_dispute(
        disputed_by=current_user.id,
        reason=data.reason,
        property_review_id=data.property_review_id,
        landlord_review_id=data.landlord_review_id,
        evidence_urls=data.evidence_urls,
        db=db,
    )


@router.get("/my", response_model=list[DisputeResponse])
async def get_my_disputes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dispute_service.get_user_disputes(current_user.id, db)


@router.post("/reviews/{review_type}/{review_id}/response", response_model=LandlordResponseResponse, status_code=201)
async def create_response(
    review_type: str,
    review_id: UUID,
    data: LandlordResponseCreateRequest,
    current_user: User = Depends(require_role(UserRole.LANDLORD)),
    db: AsyncSession = Depends(get_db),
):
    property_review_id = review_id if review_type == "property" else None
    landlord_review_id = review_id if review_type == "landlord" else None

    return await dispute_service.create_landlord_response(
        landlord_id=current_user.id,
        response_text=data.response_text,
        property_review_id=property_review_id,
        landlord_review_id=landlord_review_id,
        db=db,
    )
