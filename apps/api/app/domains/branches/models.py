from __future__ import annotations

import uuid
from datetime import datetime, time
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.domains.events.models import Event


class Branch(TimestampMixin, Base):
    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address_line1: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    address_line2: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="jakarta", index=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="ID")
    postal_code: Mapped[str | None] = mapped_column(String(20))
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Jakarta")
    public_phone: Mapped[str | None] = mapped_column(String(40))
    public_email: Mapped[str | None] = mapped_column(String(255))
    whatsapp_number: Mapped[str | None] = mapped_column(String(40))
    instagram_url: Mapped[str | None] = mapped_column(String(255))
    facebook_url: Mapped[str | None] = mapped_column(String(255))
    # Overrides the site origin used when building links for this branch. Some
    # branches run their own landing page; NULL falls back to the global origin.
    website_url: Mapped[str | None] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # Where /tour lands with no branch in the URL. At most one row may be true --
    # enforced in branch_service, because SQLite has no partial unique index.
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    settings: Mapped[BranchSettings] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    opening_hours: Mapped[list[BranchOpeningHour]] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=lambda: (BranchOpeningHour.day_of_week, BranchOpeningHour.opens_at_local),
    )
    closures: Mapped[list[BranchClosure]] = relationship(
        back_populates="branch",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by=lambda: BranchClosure.starts_at_local,
    )
    # Paired with Event.branch. Both sides are declared in the events module's
    # commit because SQLAlchemy resolves `Event` when the mapper is configured,
    # not lazily -- a back_populates pointing at a class that does not exist yet
    # fails every query, not just the ones that touch it.
    events: Mapped[list[Event]] = relationship(back_populates="branch")


class BranchSettings(TimestampMixin, Base):
    __tablename__ = "branch_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sender_display_name: Mapped[str | None] = mapped_column(String(150))
    reply_to_email: Mapped[str | None] = mapped_column(String(255))
    # Who hears about a new tour registration at this branch. JSON, not ARRAY:
    # the dev database is SQLite.
    tour_notification_recipients: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    tour_intro_html: Mapped[str | None] = mapped_column(Text)
    arrival_instructions: Mapped[str | None] = mapped_column(Text)
    parking_notes: Mapped[str | None] = mapped_column(Text)

    branch: Mapped[Branch] = relationship(back_populates="settings")


class BranchOpeningHour(TimestampMixin, Base):
    __tablename__ = "branch_opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # ISO 8601 numbering: Monday = 1 ... Sunday = 7. Stated here because the
    # source platform carries two competing conventions and paid for it.
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    opens_at_local: Mapped[time] = mapped_column(Time, nullable=False)
    closes_at_local: Mapped[time] = mapped_column(Time, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    branch: Mapped[Branch] = relationship(back_populates="opening_hours")


class BranchClosure(TimestampMixin, Base):
    __tablename__ = "branch_closures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Local wall-clock only. The source platform stores a UTC copy alongside and
    # the two can drift; convert with the branch timezone at read time instead.
    starts_at_local: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    ends_at_local: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    full_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reason: Mapped[str | None] = mapped_column(Text)  # internal
    public_label: Mapped[str | None] = mapped_column(Text)  # shown to guests
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    branch: Mapped[Branch] = relationship(back_populates="closures")


def branch_metadata(branch: Branch) -> dict[str, Any]:
    """Contact block reused by the public tour payload and branch emails."""
    return {
        "phone": branch.public_phone,
        "email": branch.public_email,
        "whatsapp": branch.whatsapp_number,
    }
