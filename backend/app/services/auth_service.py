from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import UserRole
from app.core.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_verification_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.user import EmailVerificationToken, PasswordResetToken, RefreshToken, User
from app.schemas.auth import RegisterRequest, TokenResponse


async def register_user(data: RegisterRequest, db: AsyncSession) -> User:
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")

    # Don't allow self-registration as admin
    if data.role == UserRole.ADMIN:
        raise BadRequestError("Cannot register as admin")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        role=data.role.value,
        auth_provider="email",
    )
    db.add(user)
    await db.flush()

    # Create email verification token
    token = generate_verification_token()
    email_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )
    db.add(email_token)

    # TODO: send verification email
    if settings.ENVIRONMENT == "development":
        print(f"[DEV] Email verification token for {user.email}: {token}")

    return user


async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise UnauthorizedError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)

    # Create tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "is_identity_verified": user.is_identity_verified,
        }
    )

    refresh_plain, refresh_hash = create_refresh_token()
    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_plain,
    )


async def refresh_tokens(refresh_token: str, db: AsyncSession) -> TokenResponse:
    token_hash = hash_token(refresh_token)

    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash, RefreshToken.revoked_at.is_(None))
    )
    record = result.scalar_one_or_none()

    if not record:
        raise UnauthorizedError("Invalid refresh token")

    if record.expires_at < datetime.now(timezone.utc):
        raise UnauthorizedError("Refresh token expired")

    # Get user
    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or deactivated")

    # Revoke old refresh token
    record.revoked_at = datetime.now(timezone.utc)

    # Create new tokens
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "is_identity_verified": user.is_identity_verified,
        }
    )

    new_refresh_plain, new_refresh_hash = create_refresh_token()
    new_refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_refresh_record)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_plain,
    )


async def logout_user(refresh_token: str, db: AsyncSession) -> None:
    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()
    if record:
        record.revoked_at = datetime.now(timezone.utc)


async def verify_email(token: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token == token,
            EmailVerificationToken.used_at.is_(None),
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise BadRequestError("Invalid verification token")

    if record.expires_at < datetime.now(timezone.utc):
        raise BadRequestError("Verification token expired")

    record.used_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_email_verified = True


async def request_password_reset(email: str, db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if email exists
        return

    token = generate_verification_token()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db.add(reset_token)

    # TODO: send password reset email
    if settings.ENVIRONMENT == "development":
        print(f"[DEV] Password reset token for {user.email}: {token}")


async def reset_password(token: str, new_password: str, db: AsyncSession) -> None:
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used_at.is_(None),
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        raise BadRequestError("Invalid reset token")

    if record.expires_at < datetime.now(timezone.utc):
        raise BadRequestError("Reset token expired")

    record.used_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(User).where(User.id == record.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.password_hash = hash_password(new_password)
