from __future__ import annotations

from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BranchSchema(BaseModel):
    """snake_case on the wire, matching the field names -- the same convention the
    venue and article endpoints use, so the whole API reads one way."""

    model_config = ConfigDict(from_attributes=True)


class BranchCreate(BranchSchema):
    slug: str = Field(min_length=1, max_length=150)
    name: str = Field(min_length=1, max_length=150)
    address_line1: str = Field(default="", max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(default="jakarta", max_length=100)
    country_code: str = Field(default="ID", min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    timezone: str = Field(default="Asia/Jakarta", max_length=64)
    public_phone: str | None = Field(default=None, max_length=40)
    public_email: str | None = Field(default=None, max_length=255)
    whatsapp_number: str | None = Field(default=None, max_length=40)
    instagram_url: str | None = Field(default=None, max_length=255)
    facebook_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    active: bool = True
    bookable: bool = True
    is_default: bool = False


class BranchUpdate(BranchSchema):
    slug: str | None = Field(default=None, min_length=1, max_length=150)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    postal_code: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=64)
    public_phone: str | None = Field(default=None, max_length=40)
    public_email: str | None = Field(default=None, max_length=255)
    whatsapp_number: str | None = Field(default=None, max_length=40)
    instagram_url: str | None = Field(default=None, max_length=255)
    facebook_url: str | None = Field(default=None, max_length=255)
    website_url: str | None = Field(default=None, max_length=255)
    active: bool | None = None
    bookable: bool | None = None
    is_default: bool | None = None


class BranchSettingsUpdate(BranchSchema):
    sender_display_name: str | None = Field(default=None, max_length=150)
    reply_to_email: str | None = Field(default=None, max_length=255)
    tour_notification_recipients: list[str] | None = None
    tour_intro_html: str | None = None
    arrival_instructions: str | None = None
    parking_notes: str | None = None


class OpeningHourInput(BranchSchema):
    day_of_week: int = Field(ge=1, le=7)  # ISO: Monday = 1
    opens_at_local: time
    closes_at_local: time
    active: bool = True
    sort_order: int = 0


class ClosureCreate(BranchSchema):
    starts_at_local: datetime
    ends_at_local: datetime
    full_day: bool = False
    reason: str | None = None
    public_label: str | None = None
    active: bool = True


class BranchSettingsResponse(BranchSchema):
    sender_display_name: str | None = None
    reply_to_email: str | None = None
    tour_notification_recipients: list[str] = Field(default_factory=list)
    tour_intro_html: str | None = None
    arrival_instructions: str | None = None
    parking_notes: str | None = None


class OpeningHourResponse(OpeningHourInput):
    id: int


class ClosureResponse(ClosureCreate):
    id: int


class BranchResponse(BranchSchema):
    id: int
    # UUID, not str: the column hands back a uuid.UUID and pydantic rejects it as a
    # string. `model_dump(mode="json")` renders it as one at the boundary.
    public_id: UUID
    slug: str
    name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    country_code: str
    postal_code: str | None = None
    timezone: str
    public_phone: str | None = None
    public_email: str | None = None
    whatsapp_number: str | None = None
    instagram_url: str | None = None
    facebook_url: str | None = None
    website_url: str | None = None
    active: bool
    bookable: bool
    is_default: bool
    settings: BranchSettingsResponse | None = None
    opening_hours: list[OpeningHourResponse] = Field(default_factory=list)
    closures: list[ClosureResponse] = Field(default_factory=list)
