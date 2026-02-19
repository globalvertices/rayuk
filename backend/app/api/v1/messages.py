from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.message import (
    ContactRequestResponse,
    ContactRequestUpdateRequest,
    MessageCreateRequest,
    MessageResponse,
    ReportCreateRequest,
    ReportResponse,
)
from app.services import message_service

router = APIRouter()


@router.get("/contact-requests/my", response_model=list[ContactRequestResponse])
async def get_my_contact_requests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.get_user_contact_requests(current_user.id, db)


@router.patch("/contact-requests/{request_id}", response_model=ContactRequestResponse)
async def respond_to_contact_request(
    request_id: UUID,
    data: ContactRequestUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.respond_to_contact_request(request_id, current_user.id, data.status, db)


@router.get("/conversations", response_model=list[ContactRequestResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.get_conversations(current_user.id, db)


@router.get("/conversations/{contact_request_id}", response_model=list[MessageResponse])
async def get_messages(
    contact_request_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.get_messages(contact_request_id, current_user.id, db)


@router.post("/conversations/{contact_request_id}", response_model=MessageResponse, status_code=201)
async def send_message(
    contact_request_id: UUID,
    data: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.send_message(contact_request_id, current_user.id, data.body, db)


@router.post("/reports", response_model=ReportResponse, status_code=201)
async def create_report(
    data: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await message_service.create_report(
        reporter_user_id=current_user.id,
        target_type=data.target_type,
        target_id=data.target_id,
        reason=data.reason,
        db=db,
    )
