from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UnlockTier, UserRole
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.payment import Unlock
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if token is None:
        raise UnauthorizedError()

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise UnauthorizedError("User not found")
    if not user.is_active:
        raise ForbiddenError("Account is deactivated")

    return user


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if token is None:
        return None
    try:
        return await get_current_user(token=token, db=db)
    except Exception:
        return None


def require_role(*roles: UserRole):
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in [r.value for r in roles]:
            raise ForbiddenError(f"Requires role: {', '.join(r.value for r in roles)}")
        return current_user

    return _check


def require_verified_identity():
    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.is_identity_verified:
            raise ForbiddenError("Identity verification required")
        return current_user

    return _check


async def get_review_unlock_tier(
    review_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> str | None:
    """Returns the highest unlock tier the user has for a review, or None."""
    result = await db.execute(
        select(Unlock).where(
            Unlock.user_id == user_id,
            Unlock.review_id == review_id,
        )
    )
    unlocks = list(result.scalars().all())
    if not unlocks:
        return None

    tiers = {u.tier for u in unlocks}
    if UnlockTier.FULL.value in tiers:
        return UnlockTier.FULL.value
    if UnlockTier.DETAILED.value in tiers:
        return UnlockTier.DETAILED.value
    if UnlockTier.SUMMARY.value in tiers:
        return UnlockTier.SUMMARY.value
    return None
