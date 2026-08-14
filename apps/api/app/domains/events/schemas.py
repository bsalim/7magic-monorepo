from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventSchema(BaseModel):
    """snake_case on the wire -- see BranchSchema."""

    model_config = ConfigDict(from_attributes=True)


class EventCreate(EventSchema):
    branch_id: int | None = None
    name: str = Field(min_length=1, max_length=200)
    description_html: str = ""
    venue: str | None = Field(default=None, max_length=300)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    color: str | None = Field(default=None, max_length=20)
    is_active: bool = True


class EventUpdate(EventSchema):
    branch_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description_html: str | None = None
    venue: str | None = Field(default=None, max_length=300)
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = Field(default=None, ge=1)
    cover_image_url: str | None = None
    color: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None


class EventResponse(EventSchema):
    id: int
    public_id: UUID  # dumped with mode="json", so it reaches the wire as a string
    branch_id: int | None = None
    branch_name: str | None = None
    name: str
    description_html: str
    venue: str | None = None
    event_start_at: datetime | None = None
    event_end_at: datetime | None = None
    registration_opens_at: datetime | None = None
    registration_closes_at: datetime | None = None
    capacity: int | None = None
    cover_image_url: str | None = None
    color: str | None = None
    is_active: bool
    registration_count: int = 0
    head_count: int = 0


class GuestInput(EventSchema):
    name: str = Field(min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)


class PublicRegistration(EventSchema):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)
    # The venue the guest wants to tour. A venue tour visits a venue, not the
    # branch office, so this is the destination.
    venue_id: int | None = None
    # The venue as typed, for one we do not publish. Sent alongside venue_id, never
    # instead of it: the form fills venue_id in too when a suggestion was picked.
    venue_name: str | None = Field(default=None, max_length=300)
    # Routes the booking to a branch when the URL carries no slug.
    city: str | None = Field(default=None, max_length=80)
    visit_date: date | None = None
    visit_slot: str | None = Field(default=None, max_length=40)
    # Total head count including the person booking, which is what the team needs
    # to know. `guests` remains for the named-companion path the CMS still uses.
    party_size: int | None = Field(default=None, ge=1, le=20)
    guests: list[GuestInput] = Field(default_factory=list)
    # The language the guest booked in, so the confirmation arrives in it. Not
    # stored on the row: it is needed once, at send time. Anything unrecognised
    # falls back to Indonesian rather than being rejected -- a booking must
    # never fail over the language of its receipt.
    locale: str | None = Field(default=None, max_length=10)


class RegistrationUpdate(EventSchema):
    status: str | None = None
    venue_id: int | None = None
    follow_up: bool | None = None
    notes: str | None = None
    visit_date: date | None = None
    visit_slot: str | None = Field(default=None, max_length=40)


class RegistrationResponse(EventSchema):
    id: int
    public_id: UUID
    event_id: int
    event_name: str | None = None
    branch_id: int | None = None
    branch_name: str | None = None
    venue_id: int | None = None
    venue_name: str | None = None
    city: str | None = None
    guest_name: str
    email: str
    mobile: str | None = None
    party_size: int
    visit_date: date | None = None
    visit_slot: str | None = None
    status: str
    follow_up: bool
    notes: str | None = None
    source: str
    attended_at: datetime | None = None
    guests: list[GuestInput] = Field(default_factory=list)
    created_at: datetime | None = None
