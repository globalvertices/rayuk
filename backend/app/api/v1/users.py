from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.schemas.user import UpdateContactableRequest, UpdateProfileRequest, UserPublicResponse, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return current_user


@router.patch("/me/contactable", response_model=UserResponse)
async def update_contactable(
    data: UpdateContactableRequest,
    current_user: User = Depends(require_role(UserRole.TENANT)),
    db: AsyncSession = Depends(get_db),
):
    current_user.is_contactable = data.is_contactable
    await db.flush()
    return current_user


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")
    return user
