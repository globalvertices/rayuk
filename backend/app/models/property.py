import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Property(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "properties"

    building_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=True, index=True
    )
    community_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("communities.id"), nullable=False, index=True
    )
    property_type: Mapped[str] = mapped_column(String(20), nullable=False)  # villa, apartment, townhouse, studio
    unit_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    utility_reference: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    bedrooms: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    bathrooms: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    size_sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    address_line: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    avg_property_rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    avg_landlord_rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    community: Mapped["Community"] = relationship()
    building: Mapped["Building | None"] = relationship()
    creator: Mapped["User"] = relationship()
    ownership_claims: Mapped[list["PropertyOwnershipClaim"]] = relationship(back_populates="property")

    # Import these for type hints
    from app.models.location import Building, Community
    from app.models.user import User


class PropertyOwnershipClaim(Base, UUIDMixin):
    __tablename__ = "property_ownership_claims"

    property_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    landlord_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    verification_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    property: Mapped["Property"] = relationship(back_populates="ownership_claims")
    landlord: Mapped["User"] = relationship(foreign_keys=[landlord_id])

    from app.models.user import User
