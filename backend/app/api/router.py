from fastapi import APIRouter

from app.api.v1 import admin, auth, disputes, messages, payments, properties, reviews, users, verifications

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(verifications.router, prefix="/verifications", tags=["Verifications"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
