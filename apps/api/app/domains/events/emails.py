"""Event email rendering and delivery.

Templates are plain text with `{placeholder}` tokens rather than a template
engine: they are edited by non-developers in a CMS textarea, and an unknown token
must render literally instead of raising mid-send.
"""

from __future__ import annotations

import logging
import re
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.locale import BASE_LOCALE, SUPPORTED_LOCALES, normalise_locale
from app.domains.branches.models import Branch
from app.domains.events.models import Event, EventEmailTemplate, EventRegistration

__all__ = ["BASE_LOCALE", "SUPPORTED_LOCALES", "normalise_locale"]

logger = logging.getLogger(__name__)

# Re-exported: the locale rule moved to core once the email layout needed the
# same one. Two implementations meant an `en-GB` guest got an English body in an
# Indonesian shell.

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
    "id": {
        "venue": "Venue",
        "address": "Alamat",
        "date": "Tanggal",
        "party_size": "Jumlah tamu",
    },
    "en": {
        "venue": "Venue",
        "address": "Address",
        "date": "Date",
        "party_size": "Guests",
    },
}

_WHITESPACE = re.compile(r"\s+")


def one_line(value: Any) -> str:
    """Collapse a user-supplied value onto a single line.

    Every detail in these emails renders as one `Label: value` line, and the
    HTML layout turns each such line into a styled row. A newline inside a value
    therefore does not just wrap -- it forges an extra row that looks exactly
    like a real field. A guest booking as "John\\nEmail: attacker@example.com"
    put a convincing second Email row into the branch's alert.

    The WhatsApp notifier collapses for the same class of reason; see `_slot` in
    app/services/whatsapp.py.
    """
    return _WHITESPACE.sub(" ", str(value or "")).strip()

PLACEHOLDERS = [
    "first_name",
    "event_name",
    "visit_date",
    "visit_slot",
    "venue",
    # The venue with its address, as a multi-line block. `venue` remains the
    # name alone, so an existing template that uses it is unaffected.
    "venue_details",
    # Venue, address, date and head count as one block, with any line whose
    # value is unknown left out entirely.
    "booking_details",
    "branch_name",
    # The branch signing off, falling back to the company when a booking was
    # never routed to one.
    "team_name",
    "party_size",
]


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
    return detail_lines(venue_detail_pairs(registration, fallback=fallback, locale=locale))


def venue_detail_pairs(
    registration: EventRegistration | None, *, fallback: str = "", locale: str = BASE_LOCALE
) -> list[tuple[str, str]]:
    """The venue rows as pairs, so a caller can extend the block rather than
    re-parse the rendered lines."""
    labels = VENUE_LABELS[normalise_locale(locale)]
    pairs = [(labels["venue"], one_line(venue_label(registration) or fallback))]

    venue = registration.venue if registration else None
    if venue is not None:
        # Street and area on one line, so every line in the block is a single
        # `Label: value` pair. The renderer emphasises the value after the
        # colon, and a bare continuation line has no label to anchor that to.
        # City is stored lowercased ("jakarta"), so it needs casing back for prose.
        pairs.append(
            (
                labels["address"],
                one_line(
                    ", ".join(
                        part
                        for part in (
                            (venue.address or "").strip(),
                            (venue.district or "").strip(),
                            (venue.city or "").strip().title(),
                        )
                        if part
                    )
                ),
            )
        )
    return pairs


def detail_lines(pairs: list[tuple[str, str]]) -> str:
    """Render `Label: value` lines, dropping any whose value is empty.

    A label with nothing after it is not a neutral blank -- it reads as missing
    information in a confirmation the guest is checking. The empty `Time:` line
    removed in 1b0089e was exactly this, and building the block from pairs makes
    the whole class of it impossible rather than fixing one field at a time.
    """
    return "\n".join(f"{label}: {value}" for label, value in pairs if value)


def build_replacements(
    *,
    event: Event,
    registration: EventRegistration | None,
    branch_name: str | None,
    locale: str = BASE_LOCALE,
) -> dict[str, str]:
    first_name = ""
    if registration and registration.guest_name:
        # Collapsed first: a newline anywhere in a value forges an extra row in
        # the rendered email, and the name is the one field a guest types freely.
        first_name = one_line(registration.guest_name).split(" ")[0]
    # The registration's venue, not the event's: a venue tour visits the venue
    # the guest chose. event.venue is only a label on the event itself, and
    # stands in when the registration names nothing.
    venue = one_line(venue_label(registration) or event.venue or "")
    labels = VENUE_LABELS[normalise_locale(locale)]
    visit_date = format_visit_date(registration.visit_date if registration else None, locale)
    party_size = str(registration.party_size) if registration else ""
    return {
        "first_name": first_name,
        "event_name": one_line(event.name or ""),
        "visit_date": visit_date,
        "visit_slot": one_line(registration.visit_slot if registration else ""),
        "venue": venue,
        "venue_details": venue_details(registration, fallback=venue, locale=locale),
        # The whole block the guest checks, assembled from what is actually
        # known. A date the guest never gave renders no line at all rather than
        # a bare "Tanggal:".
        "booking_details": detail_lines(
            [
                *venue_detail_pairs(registration, fallback=venue, locale=locale),
                (labels["date"], visit_date),
                (labels["party_size"], party_size),
            ]
        ),
        "branch_name": one_line(branch_name or ""),
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
            "{booking_details}\n\n"
            "{branch_name} akan menghubungi Anda untuk memastikan waktu kunjungan.\n\n"
            "Sampai jumpa!\nTim {team_name}"
        ),
    },
    "en": {
        "subject": "Your {event_name} booking is confirmed",
        "body": (
            "Hi {first_name},\n\n"
            "We have received your booking for {event_name}.\n\n"
            "{booking_details}\n\n"
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
    """The internal alert. English throughout -- see BRANCH_ALERT_LOCALE.

    Every value goes through `one_line`. These render as `Label: value` rows, so
    a newline inside one forges an extra row indistinguishable from a real
    field: a guest named "John\\nEmail: attacker@example.com" put a convincing
    second Email row above the genuine one.
    """
    subject = f"New booking: {one_line(event.name)}"
    lines = [
        f"Name: {one_line(registration.guest_name)}",
        f"Email: {one_line(registration.email)}",
        f"Mobile: {one_line(registration.mobile) or '-'}",
        f"Venue: {one_line(venue_label(registration)) or '-'}",
        f"City: {one_line(registration.city) or '-'}",
        f"Guests: {registration.party_size}",
        f"Date: {registration.visit_date.isoformat() if registration.visit_date else '-'}",
        f"Time: {one_line(registration.visit_slot) or '-'}",
        f"Branch: {one_line(branch.name) if branch else '-'}",
        f"Source: {one_line(registration.source)}",
    ]
    return subject, "\n".join(lines)


# The alert body is written in English, so its shell has to be too, or the team
# gets an English message under an Indonesian heading -- the same
# half-translation core/locale.py exists to prevent, just pointed inward.
BRANCH_ALERT_LOCALE = "en"
