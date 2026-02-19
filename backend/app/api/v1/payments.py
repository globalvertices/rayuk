from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BadRequestError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.payment import (
    ContactRequestPaymentResponse,
    CreateContactRequestPayment,
    CreditPricingResponse,
    LedgerEntryResponse,
    PurchaseUnlockRequest,
    PurchaseUnlockResponse,
    TopupCheckoutResponse,
    TopupRequest,
    UnlockCheckResponse,
    WalletResponse,
)
from app.services import payment_service

router = APIRouter()


@router.get("/wallet", response_model=WalletResponse)
async def get_wallet(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = await payment_service.get_wallet_balance(current_user.id, db)
    return wallet


@router.post("/topup", response_model=TopupCheckoutResponse)
async def topup_credits(
    data: TopupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    checkout_url, topup_id = await payment_service.create_topup_checkout(current_user, data.tier, db)
    return TopupCheckoutResponse(checkout_url=checkout_url, topup_id=topup_id)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise BadRequestError("Invalid webhook signature")

    if event["type"] == "checkout.session.completed":
        await payment_service.handle_topup_completed(event["data"]["object"], db)

    return {"status": "ok"}


@router.post("/unlock", response_model=PurchaseUnlockResponse)
async def purchase_unlock(
    data: PurchaseUnlockRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    unlock_id, credits_charged, new_balance = await payment_service.purchase_unlock(
        current_user, data.review_id, data.tier, db
    )
    return PurchaseUnlockResponse(
        unlock_id=unlock_id, credits_charged=credits_charged, new_balance=new_balance
    )


@router.post("/contact-request", response_model=ContactRequestPaymentResponse)
async def purchase_contact_request(
    data: CreateContactRequestPayment,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cr_id, credits_charged, new_balance = await payment_service.purchase_contact_request(
        user=current_user,
        tenant_id=data.tenant_id,
        property_id=data.property_id,
        review_id=data.review_id,
        message=data.message,
        db=db,
    )
    return ContactRequestPaymentResponse(
        contact_request_id=cr_id, credits_charged=credits_charged, new_balance=new_balance
    )


@router.get("/unlocks/check", response_model=UnlockCheckResponse)
async def check_unlock(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await payment_service.check_review_unlock(current_user.id, review_id, db)
    return UnlockCheckResponse(**result)


@router.get("/ledger", response_model=list[LedgerEntryResponse])
async def get_ledger(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await payment_service.get_user_ledger(current_user.id, db)


@router.get("/pricing", response_model=CreditPricingResponse)
async def get_pricing():
    return CreditPricingResponse(
        unlock_summary=settings.CREDIT_PRICE_UNLOCK_SUMMARY,
        unlock_detailed=settings.CREDIT_PRICE_UNLOCK_DETAILED,
        unlock_full=settings.CREDIT_PRICE_UNLOCK_FULL,
        contact_request=settings.CREDIT_PRICE_CONTACT_REQUEST,
        topup_small_cents=settings.CREDIT_TOPUP_SMALL_CENTS,
        topup_small_credits=settings.CREDIT_TOPUP_SMALL_CREDITS,
        topup_medium_cents=settings.CREDIT_TOPUP_MEDIUM_CENTS,
        topup_medium_credits=settings.CREDIT_TOPUP_MEDIUM_CREDITS,
        topup_large_cents=settings.CREDIT_TOPUP_LARGE_CENTS,
        topup_large_credits=settings.CREDIT_TOPUP_LARGE_CREDITS,
    )
