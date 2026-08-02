from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.translation import VenueTranslation


class Venue(TimestampMixin, Base):
    __tablename__ = "venues"
    __table_args__ = (
        UniqueConstraint("city", "slug", name="uq_venues_city_slug"),
        CheckConstraint("stars >= 1 AND stars <= 5", name="venue_stars_between_1_and_5"),
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name="venue_status_allowed",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="jakarta", index=True)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    description: Mapped[str | None] = mapped_column(Text)
    amenities: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    price_start_from: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    price_for_total_pax: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ballrooms: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    packages: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)

    photos: Mapped[list[VenuePhoto]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
        order_by=lambda: (VenuePhoto.sort_order, VenuePhoto.id),
    )

    translations: Mapped[list["VenueTranslation"]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @staticmethod
    def path_for(*, city: str, slug: str) -> str:
        normalized_city = city.strip().lower().replace(" ", "-")
        return f"/wedding-venue/{normalized_city}/{slug}"

    @property
    def path_url(self) -> str:
        return self.path_for(city=self.city, slug=self.slug)


class VenuePhoto(Base):
    __tablename__ = "venue_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id", ondelete="SET NULL"))
    temp_venue_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    alt_text: Mapped[str | None] = mapped_column(String(255))
    original_filename: Mapped[str | None] = mapped_column(String(255))
    filename: Mapped[str | None] = mapped_column(String(255))
    content_type: Mapped[str | None] = mapped_column(String(100))
    storage_key: Mapped[str | None] = mapped_column(String(512), unique=True)
    cdn_url: Mapped[str | None] = mapped_column(String(512))
    thumbnail_url: Mapped[str | None] = mapped_column(String(512))
    original_width: Mapped[int | None] = mapped_column(Integer)
    original_height: Mapped[int | None] = mapped_column(Integer)
    original_file_size: Mapped[int | None] = mapped_column(Integer)
    orientation: Mapped[str | None] = mapped_column(String(20))
    webp_srcset: Mapped[str | None] = mapped_column(Text)
    jpeg_srcset: Mapped[str | None] = mapped_column(Text)
    sizes_attribute: Mapped[str | None] = mapped_column(Text)
    breakpoints_used: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    formats_generated: Mapped[list[str] | None] = mapped_column(JSON)
    webp_variants: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)
    jpeg_variants: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON)

    venue: Mapped[Venue | None] = relationship(back_populates="photos")
