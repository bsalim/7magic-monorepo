"""Event email rendering and delivery.

Templates are plain text with `{placeholder}` tokens rather than a template
engine: they are edited by non-developers in a CMS textarea, and an unknown token
must render literally instead of raising mid-send.
"""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch
from app.domains.events.models import Event, EventEmailTemplate, EventRegistration

logger = logging.getLogger(__name__)

# Indonesian is canonical, English secondary -- the same rule the site follows.
# Anything else, including an absent value, renders Indonesian: a guest must get
# a readable confirmation even when the caller says nothing about language.
BASE_LOCALE = "id"
SUPPORTED_LOCALES = ("id", "en")

# Month names are a table rather than a call into Python's `locale` module,
# which is process-global, not thread-safe, and depends on the OS having the
# locale data installed -- three bad properties for an async server. Twenty-four
# strings buy correctness with no runtime dependency.
MONTH_NAMES: dict[str, tuple[str, ...]] = {
    "id": (
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ),
    "en": (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ),
}

VENUE_LABELS: dict[str, dict[str, str]] = {
    "id": {"venue": "Venue", "address": "Alamat"},
    "en": {"venue": "Venue", "address": "Address"},
}

PLACEHOLDERS = [
    "first_name",
    "event_name",
    "visit_date",
    "visit_slot",
    "venue",
    # The venue with its address, as a multi-line block. `venue` remains the
    # name alone, so an existing template that uses it is unaffected.
    "venue_details",
    "branch_name",
    # The branch signing off, falling back to the company when a booking was
    # never routed to one.
    "team_name",
    "party_size",
]


def normalise_locale(locale: str | None) -> str:
    """Reduce whatever the caller sent to a locale we can render.

    Accepts a region tag (`en-GB`) by taking the language half, since that is
    what a browser or an `Accept-Language` header tends to carry.
    """
    candidate = (locale or "").strip().lower().replace("_", "-").split("-")[0]
    return candidate if candidate in SUPPORTED_LOCALES else BASE_LOCALE


def format_visit_date(value: date | None, locale: str = BASE_LOCALE) -> str:
    """`17 Mei 2026` rather than `2026-05-17`.

    A numeric format is not an option: 05/17 and 17/05 mean different things in
    different places, and a guest reading the wrong date misses their tour.
    """
    if value is None:
        return ""
    return f"{value.day} {MONTH_NAMES[normalise_locale(locale)][value.month - 1]} {value.year}"

DEFAULT_TEMPLATES: dict[str, dict[str, str]] = {
    "thank_you": {
        "subject": "Thank you for visiting {branch_name}",
        "body": (
            "Hi {first_name},\n\n"
            "Thank you for taking the time to join us for {event_name} at {branch_name}.\n"
            "If you have any questions about dates, styling or packages, just reply to this "
            "email.\n\n"
            "Warm regards,\nThe 7Magic team"
        ),
    },
    "no_show": {
        "subject": "We missed you at {branch_name}",
        "body": (
            "Hi {first_name},\n\n"
            "We did not get to meet you on {visit_date} at {visit_slot}.\n"
            "Would you like us to rebook? Reply to this email with a date that suits you.\n\n"
            "Warm regards,\nThe 7Magic team"
        ),
    },
    "cancel": {
        "subject": "Your visit to {branch_name} has been cancelled",
        "body": (
            "Hi {first_name},\n\n"
            "Your visit on {visit_date} has been cancelled.\n"
            "Whenever you would like to book again, we are happy to help.\n\n"
            "Warm regards,\nThe 7Magic team"
        ),
    },
}


def default_template(kind: str) -> dict[str, str]:
    return dict(DEFAULT_TEMPLATES.get(kind, {"subject": "", "body": "{first_name}"}))


def venue_label(registration: EventRegistration | None) -> str:
    """The venue, named. The catalogue row wins when there is one; otherwise the
    guest's own words, because the tour network is wider than what we publish."""
    if registration is None:
        return ""
    if registration.venue is not None:
        return registration.venue.name
    return registration.venue_name or ""


def venue_details(
    registration: EventRegistration | None, *, fallback: str = "", locale: str = BASE_LOCALE
) -> str:
    """The venue as an address block: where the guest is actually going.

    A tour confirmation whose venue line is a bare name leaves the guest to go
    and look the address up, so the street and area are included whenever we
    have the venue on file. When the guest typed a venue we do not publish there
    is only a name -- `venue_name` with no `venue_id` -- and the block correctly
    degrades to that single line.
    """
    labels = VENUE_LABELS[normalise_locale(locale)]
    name = venue_label(registration) or fallback
    lines = []
    if name:
        lines.append(f"{labels['venue']}: {name}")

    venue = registration.venue if registration else None
    if venue is not None:
        if street := (venue.address or "").strip():
            lines.append(f"{labels['address']}: {street}")
        # City is stored lowercased ("jakarta"), so it needs casing back for prose.
        area = ", ".join(
            part
            for part in ((venue.district or "").strip(), (venue.city or "").strip().title())
            if part
        )
        if area:
            lines.append(area)
    return "\n".join(lines)


def build_replacements(
    *,
    event: Event,
    registration: EventRegistration | None,
    branch_name: str | None,
    locale: str = BASE_LOCALE,
) -> dict[str, str]:
    first_name = ""
    if registration and registration.guest_name:
        first_name = registration.guest_name.strip().split(" ")[0]
    # The registration's venue, not the event's: a venue tour visits the venue
    # the guest chose. event.venue is only a label on the event itself, and
    # stands in when the registration names nothing.
    venue = venue_label(registration) or event.venue or ""
    return {
        "first_name": first_name,
        "event_name": event.name or "",
        "visit_date": format_visit_date(
            registration.visit_date if registration else None, locale
        ),
        "visit_slot": (registration.visit_slot if registration else "") or "",
        "venue": venue,
        "venue_details": venue_details(registration, fallback=venue, locale=locale),
        "branch_name": branch_name or "",
        # Who is signing off. The branch when there is one, so a guest hears from
        # "7Magic Jakarta" rather than from the company in the abstract, and it
        # matches the branch that actually follows up. Falls back to the company
        # name so an unrouted booking never signs off as "Tim " with a gap.
        "team_name": branch_name or "7Magic",
        "party_size": str(registration.party_size) if registration else "",
    }


def render_template(text: str, replacements: dict[str, str]) -> str:
    """`str.format` would raise KeyError on an unknown token; replace only the
    tokens we know and leave anything else exactly as typed."""
    rendered = text or ""
    for key, value in replacements.items():
        rendered = rendered.replace("{" + key + "}", value)
    return rendered


def notification_recipients(branch: Branch | None) -> list[str]:
    """Deduplicated, lowercased addresses to alert about a new registration.

    Expects `branch.settings` to be loaded -- every branch that reaches here came
    from branch_service, which loads it via selectin. Reading an unloaded relation
    under asyncio raises MissingGreenlet rather than emitting a SELECT.
    """
    if branch is None or branch.settings is None:
        return []
    seen: list[str] = []
    for raw in branch.settings.tour_notification_recipients or []:
        address = str(raw).strip().lower()
        if address and address not in seen:
            seen.append(address)
    return seen


async def template_for(
    session: AsyncSession, event_id: int, kind: str
) -> EventEmailTemplate | None:
    return await session.scalar(
        select(EventEmailTemplate).where(
            EventEmailTemplate.event_id == event_id, EventEmailTemplate.kind == kind
        )
    )


# The one email every guest gets, so it is the one that has to be in their
# language. Not CMS-editable, unlike the three follow-up templates: it is the
# receipt for a booking and must not be able to lose its own details.
#
# No time line in either: the public form offers a date and no slot, so this
# rendered an empty "Time:" on every booking. The follow-up promise covers it.
CONFIRMATION_TEMPLATES: dict[str, dict[str, str]] = {
    "id": {
        "subject": "Booking {event_name} Anda sudah dikonfirmasi",
        "body": (
            "Halo {first_name},\n\n"
            "Kami sudah menerima booking Anda untuk {event_name}.\n\n"
            "{venue_details}\n"
            "Tanggal: {visit_date}\n"
            "Jumlah tamu: {party_size}\n\n"
            "{branch_name} akan menghubungi Anda untuk memastikan waktu kunjungan.\n\n"
            "Sampai jumpa!\nTim {team_name}"
        ),
    },
    "en": {
        "subject": "Your {event_name} booking is confirmed",
        "body": (
            "Hi {first_name},\n\n"
            "We have received your booking for {event_name}.\n\n"
            "{venue_details}\n"
            "Date: {visit_date}\n"
            "Guests: {party_size}\n\n"
            "{branch_name} will be in touch to confirm the time.\n\n"
            "See you soon!\nThe {team_name} team"
        ),
    },
}


def registration_confirmation(
    *,
    event: Event,
    registration: EventRegistration,
    branch: Branch | None,
    locale: str | None = None,
) -> tuple[str, str]:
    """The always-on email a guest gets on submit, in the language they booked
    in. Distinct from the three admin templates, which are sent by hand after
    the visit."""
    resolved = normalise_locale(locale)
    replacements = build_replacements(
        event=event,
        registration=registration,
        branch_name=branch.name if branch else None,
        locale=resolved,
    )
    template = CONFIRMATION_TEMPLATES[resolved]
    return (
        render_template(template["subject"], replacements),
        render_template(template["body"], replacements),
    )


def branch_alert(
    *, event: Event, registration: EventRegistration, branch: Branch | None
) -> tuple[str, str]:
    subject = f"New booking: {event.name}"
    lines = [
        f"Name: {registration.guest_name}",
        f"Email: {registration.email}",
        f"Mobile: {registration.mobile or '-'}",
        f"Venue: {venue_label(registration) or '-'}",
        f"City: {registration.city or '-'}",
        f"Guests: {registration.party_size}",
        f"Date: {registration.visit_date.isoformat() if registration.visit_date else '-'}",
        f"Time: {registration.visit_slot or '-'}",
        f"Branch: {branch.name if branch else '-'}",
        f"Source: {registration.source}",
    ]
    return subject, "\n".join(lines)
