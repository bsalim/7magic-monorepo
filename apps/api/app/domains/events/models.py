from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domains.branches.models import Branch
from app.models.mixins import TimestampMixin

REGISTRATION_STATUSES = ("registered", "attended", "no_show", "cancelled")
TEMPLATE_KINDS = ("thank_you", "no_show", "cancel")


class Event(TimestampMixin, Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    # NULL means the event belongs to every branch (a company-wide open house).
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    venue: Mapped[str | None] = mapped_column(String(300))
    event_start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    event_end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registration_opens_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    registration_closes_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    capacity: Mapped[int | None] = mapped_column(Integer)
    cover_image_url: Mapped[str | None] = mapped_column(Text)
    color: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # selectin, not lazy: the routers read `event.branch.name` for the Branch column
    # after the query has returned, and a lazy load there raises MissingGreenlet
    # under asyncio.
    branch: Mapped[Branch | None] = relationship(back_populates="events", lazy="selectin")
    registrations: Mapped[list[EventRegistration]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    email_templates: Mapped[list[EventEmailTemplate]] = relationship(
        back_populates="event", cascade="all, delete-orphan", lazy="selectin"
    )


class EventRegistration(TimestampMixin, Base):
    __tablename__ = "event_registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    public_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, unique=True, nullable=False)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    guest_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    mobile: Mapped[str | None] = mapped_column(String(40))
    party_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    visit_date: Mapped[date | None] = mapped_column(Date)
    visit_slot: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="registered", index=True
    )
    follow_up: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)
    # "public" (the website form) or "cms" (typed in by the team).
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="public")
    attended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attended_by_user_id: Mapped[int | None] = mapped_column(Integer)

    # Also selectin: the registrations router reads `registration.event.branch.name`
    # for its Branch column and its CSV export.
    event: Mapped[Event] = relationship(back_populates="registrations", lazy="selectin")
    guests: Mapped[list[EventRegistrationGuest]] = relationship(
        back_populates="registration", cascade="all, delete-orphan", lazy="selectin"
    )


class EventRegistrationGuest(Base):
    __tablename__ = "event_registration_guests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    registration_id: Mapped[int] = mapped_column(
        ForeignKey("event_registrations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320))
    mobile: Mapped[str | None] = mapped_column(String(40))

    registration: Mapped[EventRegistration] = relationship(back_populates="guests")


class EventEmailTemplate(TimestampMixin, Base):
    __tablename__ = "event_email_templates"
    __table_args__ = (
        UniqueConstraint("event_id", "kind", name="uq_event_email_templates_event_id_kind"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # see TEMPLATE_KINDS
    subject: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    event: Mapped[Event] = relationship(back_populates="email_templates")
