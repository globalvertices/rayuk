from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.verification import (
    TenancyRecordCreateRequest,
    TenancyRecordResponse,
    VerificationDocumentResponse,
    VerificationSubmitRequest,
)
from app.services import storage_service, verification_service

router = APIRouter()


@router.post("/tenancy", response_model=TenancyRecordResponse, status_code=201)
async def create_tenancy_record(
    data: TenancyRecordCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await verification_service.create_tenancy_record(
        tenant_id=current_user.id,
        property_id=data.property_id,
        move_in_date=data.move_in_date,
        move_out_date=data.move_out_date,
        is_current_tenant=data.is_current_tenant,
        db=db,
    )


@router.post("/upload", response_model=VerificationDocumentResponse, status_code=201)
async def upload_verification_document(
    file: UploadFile,
    document_type: str,
    tenancy_record_id: str | None = None,
    ownership_claim_id: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Upload file
    file_info = await storage_service.upload_file(file)

    return await verification_service.submit_verification_document(
        user_id=current_user.id,
        document_type=document_type,
        file_url=file_info["file_url"],
        file_name=file_info["file_name"],
        file_size_bytes=file_info["file_size_bytes"],
        mime_type=file_info["mime_type"],
        tenancy_record_id=tenancy_record_id,
        ownership_claim_id=ownership_claim_id,
        db=db,
    )


@router.get("/my", response_model=list[VerificationDocumentResponse])
async def get_my_verifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await verification_service.get_user_verifications(current_user.id, db)
