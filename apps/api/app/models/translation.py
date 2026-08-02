from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.venue import Venue


class VenueTranslation(TimestampMixin, Base):
    """Localized venue copy. The base `venues` row holds the canonical Indonesian
    content; a row here overrides it for one locale. Missing or null fields fall
    back to the base row."""

    __tablename__ = "venue_translations"
    __table_args__ = (
        UniqueConstraint("venue_id", "locale", name="uq_venue_translations_venue_locale"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venues.id", ondelete="CASCADE"), nullable=False, index=True
    )
    locale: Mapped[str] = mapped_column(String(5), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    packages: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    venue: Mapped["Venue"] = relationship(back_populates="translations")
