import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class PropertyReview(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "property_reviews"
    __table_args__ = (
        UniqueConstraint("property_id", "tenant_id", name="uq_property_review_tenant"),
    )

    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    tenancy_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenancy_records.id"), nullable=False
    )

    # Category ratings (1-5, nullable = not applicable)
    rating_plumbing: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_electricity: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_water: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_it_cabling: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_hvac: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_amenity_stove: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_amenity_washer: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_amenity_fridge: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_infra_water_tank: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_infra_irrigation: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_health_dust: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_health_breathing: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_health_sewage: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    overall_rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)
    public_excerpt: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Status workflow: draft -> submitted -> published / disputed / removed
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)
    # Verification: unverified -> pending -> verified / rejected
    verification_status: Mapped[str] = mapped_column(String(20), default="unverified", nullable=False)

    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    property: Mapped["Property"] = relationship()
    tenant: Mapped["User"] = relationship()
    tenancy_record: Mapped["TenancyRecord"] = relationship()
    photos: Mapped[list["PropertyReviewPhoto"]] = relationship(back_populates="review", cascade="all, delete-orphan")

    from app.models.property import Property
    from app.models.user import User
    from app.models.verification import TenancyRecord


class PropertyReviewPhoto(Base, UUIDMixin):
    __tablename__ = "property_review_photos"

    review_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("property_reviews.id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review: Mapped["PropertyReview"] = relationship(back_populates="photos")


class LandlordReview(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "landlord_reviews"

    landlord_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False
    )
    tenancy_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenancy_records.id"), nullable=False
    )

    # Category ratings (1-5)
    rating_responsiveness: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_demeanor: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_repair_payments: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_availability: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    rating_payment_flexibility: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    overall_rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Status workflow: draft -> submitted -> published / disputed / removed
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False, index=True)
    # Verification: unverified -> pending -> verified / rejected
    verification_status: Mapped[str] = mapped_column(String(20), default="unverified", nullable=False)

    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    landlord: Mapped["User"] = relationship(foreign_keys=[landlord_id])
    tenant: Mapped["User"] = relationship(foreign_keys=[tenant_id])
    property: Mapped["Property"] = relationship()
    tenancy_record: Mapped["TenancyRecord"] = relationship()

    from app.models.property import Property
    from app.models.user import User
    from app.models.verification import TenancyRecord
