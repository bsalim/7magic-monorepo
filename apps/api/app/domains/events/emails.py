"""Event email rendering and delivery.

Templates are plain text with `{placeholder}` tokens rather than a template
engine: they are edited by non-developers in a CMS textarea, and an unknown token
must render literally instead of raising mid-send.
"""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.branches.models import Branch
from app.domains.events.models import Event, EventEmailTemplate, EventRegistration

logger = logging.getLogger(__name__)

PLACEHOLDERS = [
    "first_name",
    "event_name",
    "visit_date",
    "visit_slot",
    "venue",
    "branch_name",
    "party_size",
]

DEFAULT_TEMPLATES: dict[str, dict[str, str]] = {
    "thank_you": {
        "subject": "Terima kasih sudah berkunjung ke {branch_name}",
        "body": (
            "Halo {first_name},\n\n"
            "Terima kasih sudah meluangkan waktu untuk {event_name} di {branch_name}.\n"
            "Kalau ada pertanyaan soal tanggal, dekorasi, atau paket, balas email ini saja.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
    "no_show": {
        "subject": "Kami menunggu Anda di {branch_name}",
        "body": (
            "Halo {first_name},\n\n"
            "Kami tidak bertemu Anda pada {visit_date} pukul {visit_slot}.\n"
            "Mau kami jadwalkan ulang? Balas email ini dengan tanggal yang cocok.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
    "cancel": {
        "subject": "Kunjungan Anda ke {branch_name} dibatalkan",
        "body": (
            "Halo {first_name},\n\n"
            "Kunjungan Anda pada {visit_date} sudah kami batalkan.\n"
            "Kapan pun ingin menjadwalkan lagi, kami siap membantu.\n\n"
            "Salam,\nTim 7Magic"
        ),
    },
}


def default_template(kind: str) -> dict[str, str]:
    return dict(DEFAULT_TEMPLATES.get(kind, {"subject": "", "body": "{first_name}"}))


def build_replacements(
    *, event: Event, registration: EventRegistration | None, branch_name: str | None
) -> dict[str, str]:
    first_name = ""
    if registration and registration.guest_name:
        first_name = registration.guest_name.strip().split(" ")[0]
    return {
        "first_name": first_name,
        "event_name": event.name or "",
        "visit_date": registration.visit_date.isoformat()
        if registration and registration.visit_date
        else "",
        "visit_slot": (registration.visit_slot if registration else "") or "",
        "venue": event.venue or "",
        "branch_name": branch_name or "",
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


def registration_confirmation(
    *, event: Event, registration: EventRegistration, branch: Branch | None
) -> tuple[str, str]:
    """The always-on email a guest gets on submit. Distinct from the three admin
    templates, which are sent by hand after the visit."""
    replacements = build_replacements(
        event=event, registration=registration, branch_name=branch.name if branch else None
    )
    subject = render_template("Pendaftaran {event_name} diterima", replacements)
    body = render_template(
        "Halo {first_name},\n\n"
        "Pendaftaran Anda untuk {event_name} sudah kami terima.\n"
        "Tanggal: {visit_date}\nWaktu: {visit_slot}\nJumlah tamu: {party_size}\n"
        "Lokasi: {branch_name}\n\n"
        "Sampai jumpa!\nTim 7Magic",
        replacements,
    )
    return subject, body


def branch_alert(
    *, event: Event, registration: EventRegistration, branch: Branch | None
) -> tuple[str, str]:
    subject = f"Pendaftaran baru: {event.name}"
    lines = [
        f"Nama: {registration.guest_name}",
        f"Email: {registration.email}",
        f"HP: {registration.mobile or '-'}",
        f"Jumlah tamu: {registration.party_size}",
        f"Tanggal: {registration.visit_date.isoformat() if registration.visit_date else '-'}",
        f"Waktu: {registration.visit_slot or '-'}",
        f"Cabang: {branch.name if branch else '-'}",
        f"Sumber: {registration.source}",
    ]
    return subject, "\n".join(lines)
