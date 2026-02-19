from datetime import datetime, timedelta, timezone
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import ContactRequestStatus, LedgerEntryType, UnlockTier
from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.models.message import ContactRequest
from app.models.payment import LedgerEntry, StripeTopup, Unlock, Wallet
from app.models.user import User

stripe.api_key = settings.STRIPE_SECRET_KEY

TOPUP_TIERS = {
    "small": (settings.CREDIT_TOPUP_SMALL_CENTS, settings.CREDIT_TOPUP_SMALL_CREDITS),
    "medium": (settings.CREDIT_TOPUP_MEDIUM_CENTS, settings.CREDIT_TOPUP_MEDIUM_CREDITS),
    "large": (settings.CREDIT_TOPUP_LARGE_CENTS, settings.CREDIT_TOPUP_LARGE_CREDITS),
}

UNLOCK_PRICES = {
    UnlockTier.SUMMARY: settings.CREDIT_PRICE_UNLOCK_SUMMARY,
    UnlockTier.DETAILED: settings.CREDIT_PRICE_UNLOCK_DETAILED,
    UnlockTier.FULL: settings.CREDIT_PRICE_UNLOCK_FULL,
}

TIER_HIERARCHY = [UnlockTier.SUMMARY, UnlockTier.DETAILED, UnlockTier.FULL]


async def get_or_create_wallet(user_id: UUID, db: AsyncSession) -> Wallet:
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance_credits=0)
        db.add(wallet)
        await db.flush()
    return wallet


async def get_wallet_balance(user_id: UUID, db: AsyncSession) -> Wallet:
    return await get_or_create_wallet(user_id, db)


async def create_topup_checkout(user: User, tier: str, db: AsyncSession) -> tuple[str, UUID]:
    if tier not in TOPUP_TIERS:
        raise BadRequestError(f"Invalid top-up tier: {tier}. Must be small, medium, or large")

    amount_cents, credits_amount = TOPUP_TIERS[tier]

    topup = StripeTopup(
        user_id=user.id,
        credits_amount=credits_amount,
        amount_cents=amount_cents,
        currency="USD",
        status="pending",
    )
    db.add(topup)
    await db.flush()

    session = stripe.checkout.Session.create(
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"TenantTruth Credits ({credits_amount} credits)"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"{settings.FRONTEND_URL}/wallet?topup=success",
        cancel_url=f"{settings.FRONTEND_URL}/wallet?topup=cancelled",
        metadata={
            "topup_id": str(topup.id),
            "user_id": str(user.id),
            "credits_amount": str(credits_amount),
        },
        client_reference_id=str(topup.id),
    )

    topup.stripe_checkout_session_id = session.id
    await db.flush()

    return session.url, topup.id


async def handle_topup_completed(session_data: dict, db: AsyncSession) -> None:
    topup_id = session_data["metadata"].get("topup_id")
    if not topup_id:
        return

    result = await db.execute(select(StripeTopup).where(StripeTopup.id == topup_id))
    topup = result.scalar_one_or_none()
    if not topup or topup.status == "completed":
        return  # Idempotent

    topup.status = "completed"
    topup.stripe_payment_intent_id = session_data.get("payment_intent")
    topup.completed_at = datetime.now(timezone.utc)

    # Credit the wallet
    wallet = await get_or_create_wallet(topup.user_id, db)
    wallet.balance_credits += topup.credits_amount

    # Ledger entry
    entry = LedgerEntry(
        user_id=topup.user_id,
        amount=topup.credits_amount,
        entry_type=LedgerEntryType.TOPUP.value,
        ref_type="stripe_topup",
        ref_id=topup.id,
        description=f"Top-up: {topup.credits_amount} credits via Stripe",
    )
    db.add(entry)
    await db.flush()


async def purchase_unlock(
    user: User, review_id: UUID, tier: UnlockTier, db: AsyncSession
) -> tuple[UUID, int, int]:
    """Spend credits to unlock a review at a given tier. Returns (unlock_id, credits_charged, new_balance)."""
    # Check if already unlocked at this tier or higher
    result = await db.execute(
        select(Unlock).where(Unlock.user_id == user.id, Unlock.review_id == review_id)
    )
    existing_unlocks = list(result.scalars().all())
    existing_tiers = {u.tier for u in existing_unlocks}

    # If they already have this tier or higher, reject
    tier_idx = TIER_HIERARCHY.index(tier)
    for existing_tier in existing_tiers:
        if existing_tier in [t.value for t in TIER_HIERARCHY]:
            existing_idx = TIER_HIERARCHY.index(UnlockTier(existing_tier))
            if existing_idx >= tier_idx:
                raise ConflictError(f"You already have {existing_tier} access or higher for this review")

    # Calculate price (only charge the difference if upgrading)
    full_price = UNLOCK_PRICES[tier]
    already_paid = sum(
        UNLOCK_PRICES[UnlockTier(t)]
        for t in existing_tiers
        if t in [tt.value for tt in TIER_HIERARCHY]
    )
    charge = max(0, full_price - already_paid)

    # Check balance
    wallet = await get_or_create_wallet(user.id, db)
    if wallet.balance_credits < charge:
        raise BadRequestError(f"Insufficient credits. Need {charge}, have {wallet.balance_credits}")

    # Debit wallet
    wallet.balance_credits -= charge

    # Create unlock
    unlock = Unlock(user_id=user.id, review_id=review_id, tier=tier.value)
    db.add(unlock)
    await db.flush()

    # Ledger entry
    if charge > 0:
        entry = LedgerEntry(
            user_id=user.id,
            amount=-charge,
            entry_type=LedgerEntryType.CHARGE.value,
            ref_type="unlock",
            ref_id=unlock.id,
            description=f"Unlock review ({tier.value}): {charge} credits",
        )
        db.add(entry)
        await db.flush()

    return unlock.id, charge, wallet.balance_credits


async def purchase_contact_request(
    user: User,
    tenant_id: UUID,
    property_id: UUID,
    review_id: UUID | None,
    message: str | None,
    db: AsyncSession,
) -> tuple[UUID, int, int]:
    """Spend credits to create a contact request. Charged upfront, refunded on decline."""
    charge = settings.CREDIT_PRICE_CONTACT_REQUEST

    wallet = await get_or_create_wallet(user.id, db)
    if wallet.balance_credits < charge:
        raise BadRequestError(f"Insufficient credits. Need {charge}, have {wallet.balance_credits}")

    # Debit wallet
    wallet.balance_credits -= charge

    # Create contact request
    cr = ContactRequest(
        requester_id=user.id,
        tenant_id=tenant_id,
        property_id=property_id,
        review_id=review_id,
        status=ContactRequestStatus.PENDING.value,
        message=message,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(cr)
    await db.flush()

    # Ledger entry
    entry = LedgerEntry(
        user_id=user.id,
        amount=-charge,
        entry_type=LedgerEntryType.CHARGE.value,
        ref_type="contact_request",
        ref_id=cr.id,
        description=f"Contact request: {charge} credits",
    )
    db.add(entry)
    await db.flush()

    return cr.id, charge, wallet.balance_credits


async def refund_contact_request(contact_request_id: UUID, user_id: UUID, db: AsyncSession) -> None:
    """Refund credits when a contact request is declined."""
    charge = settings.CREDIT_PRICE_CONTACT_REQUEST
    wallet = await get_or_create_wallet(user_id, db)
    wallet.balance_credits += charge

    entry = LedgerEntry(
        user_id=user_id,
        amount=charge,
        entry_type=LedgerEntryType.REFUND.value,
        ref_type="contact_request",
        ref_id=contact_request_id,
        description=f"Refund for declined contact request: {charge} credits",
    )
    db.add(entry)
    await db.flush()


async def get_user_ledger(user_id: UUID, db: AsyncSession) -> list[LedgerEntry]:
    result = await db.execute(
        select(LedgerEntry).where(LedgerEntry.user_id == user_id).order_by(LedgerEntry.created_at.desc())
    )
    return list(result.scalars().all())


async def check_review_unlock(user_id: UUID, review_id: UUID, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Unlock).where(Unlock.user_id == user_id, Unlock.review_id == review_id)
    )
    unlocks = list(result.scalars().all())
    tiers = {u.tier for u in unlocks}

    has_full = UnlockTier.FULL.value in tiers
    has_detailed = has_full or UnlockTier.DETAILED.value in tiers
    has_summary = has_detailed or UnlockTier.SUMMARY.value in tiers

    highest = None
    if has_full:
        highest = UnlockTier.FULL.value
    elif has_detailed:
        highest = UnlockTier.DETAILED.value
    elif has_summary:
        highest = UnlockTier.SUMMARY.value

    return {
        "has_summary": has_summary,
        "has_detailed": has_detailed,
        "has_full": has_full,
        "highest_tier": highest,
    }
