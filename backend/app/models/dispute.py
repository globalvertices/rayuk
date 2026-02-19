import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ReviewDispute(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "review_disputes"

    property_review_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property_reviews.id"), nullable=True
    )
    landlord_review_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("landlord_reviews.id"), nullable=True
    )
    disputed_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_urls: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open")
    # open, under_review, resolved_upheld, resolved_removed, dismissed
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    disputer: Mapped["User"] = relationship(foreign_keys=[disputed_by])
    property_review: Mapped["PropertyReview | None"] = relationship()
    landlord_review: Mapped["LandlordReview | None"] = relationship()

    from app.models.review import LandlordReview, PropertyReview
    from app.models.user import User


class LandlordResponse(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "landlord_responses"

    property_review_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property_reviews.id"), nullable=True
    )
    landlord_review_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("landlord_reviews.id"), nullable=True
    )
    landlord_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    landlord: Mapped["User"] = relationship()

    from app.models.user import User
