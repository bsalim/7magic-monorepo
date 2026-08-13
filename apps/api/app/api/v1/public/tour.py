"""Public Book a Tour endpoints. No auth: these are the website's forms."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.errors import error_response
from app.domains.branches.models import Branch
from app.domains.branches.service import BranchNotFoundError, branch_service
from app.domains.events.emails import (
    branch_alert,
    notification_recipients,
    registration_confirmation,
    venue_label,
)
from app.domains.events.models import Event, EventRegistration
from app.domains.events.schemas import PublicRegistration
from app.domains.events.service import (
    RegistrationBlocked,
    event_service,
    registration_block,
)
from app.models.venue import Venue
from app.services.email import send_email
from app.services.whatsapp import WhatsAppNotifier, join_contact

logger = logging.getLogger(__name__)
router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db_session)]

# How far ahead the page advertises closures. Longer than any sane tour window and
# short enough to keep the payload small.
CLOSURE_HORIZON_DAYS = 120


def _branch_payload(branch: Branch) -> dict:
    return {
        "id": branch.id,
        "slug": branch.slug,
        "name": branch.name,
        "city": branch.city,
        "address_line1": branch.address_line1,
        "address_line2": branch.address_line2,
        "timezone": branch.timezone,
        "public_phone": branch.public_phone,
        "public_email": branch.public_email,
        "whatsapp_number": branch.whatsapp_number,
        "website_url": branch.website_url,
    }


def _event_payload(event: Event, now: datetime) -> dict:
    block = registration_block(event, now)
    return {
        "id": event.id,
        "public_id": str(event.public_id),
        "name": event.name,
        "description_html": event.description_html,
        "cover_image_url": event.cover_image_url,
        "venue": event.venue,
        "event_start_at": event.event_start_at.isoformat() if event.event_start_at else None,
        "event_end_at": event.event_end_at.isoformat() if event.event_end_at else None,
        "registration_open": block is None,
        "registration_closed_reason": block[1] if block else None,
    }


async def _tourable_venues(session: AsyncSession) -> list[dict]:
    """Every active venue, for the form's venue dropdown.

    All cities, not just this branch's: a couple enquiring through the Jakarta
    branch may well want to tour a venue in Bali, and the branch is who handles the
    booking rather than where it happens. Ordered by city then name so the page can
    group them without sorting again.
    """
    rows = await session.scalars(
        select(Venue)
        .where(Venue.status == "active")
        .order_by(Venue.city, Venue.name)
    )
    return [{"id": row.id, "name": row.name, "city": row.city} for row in rows]


def _closed_dates(branch: Branch, today: date) -> list[str]:
    horizon = today + timedelta(days=CLOSURE_HORIZON_DAYS)
    closed: list[str] = []
    for closure in branch.closures:
        if not closure.active:
            continue
        cursor = max(closure.starts_at_local.date(), today)
        last = min(closure.ends_at_local.date(), horizon)
        while cursor <= last:
            closed.append(cursor.isoformat())
            cursor += timedelta(days=1)
    return sorted(set(closed))


@router.get("/tour")
async def tour_form_payload(session: DbSession):
    """Everything the branch-less form needs: what to suggest, what to route by,
    and whether anyone is taking bookings at all."""
    venues = await _tourable_venues(session)
    any_branch, branch_ids = await event_service.open_tour_scope(session, datetime.now(UTC))
    return {
        "data": {
            "venues": venues,
            # Distinct, in the order the venue query already sorted them.
            # dict.fromkeys rather than a set: the dropdown order has to be stable
            # across requests.
            "cities": list(dict.fromkeys(row["city"] for row in venues)),
            "open": any_branch or bool(branch_ids),
        }
    }


@router.post("/tour/register", status_code=status.HTTP_201_CREATED)
async def register_without_a_branch(payload: PublicRegistration, session: DbSession):
    """The nav entry point: the guest named a venue and a city, and the city is what
    decides whose event and whose inbox this lead belongs to."""
    now = datetime.now(UTC)
    branch, event = await event_service.resolve_tour_target(session, payload.city, now)
    if event is None:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="no_open_event",
            message="We are not taking tour bookings right now.",
        )

    try:
        registration = await event_service.register(
            session, event=event, branch=branch, payload=payload, now=now, source="public"
        )
    except RegistrationBlocked as blocked:
        code = 422 if blocked.code == "validation_error" else status.HTTP_409_CONFLICT
        return error_response(status_code=code, code=blocked.code, message=blocked.message)

    await _notify(event=event, registration=registration, branch=branch)

    return {
        "data": {
            "id": registration.id,
            "public_id": str(registration.public_id),
            "party_size": registration.party_size,
            "visit_date": registration.visit_date.isoformat() if registration.visit_date else None,
            "visit_slot": registration.visit_slot,
            "branch_name": branch.name if branch else None,
        }
    }


@router.get("/tour/branches")
async def list_tour_branches(session: DbSession):
    branches = await branch_service.list(session, active_only=True)
    # Active and bookable is not sufficient: a registration hangs off an event, so a
    # branch with none open cannot accept one. Listing it would send a guest to a
    # page whose only message is "not taking bookings right now".
    any_branch, branch_ids = await event_service.open_tour_scope(session, datetime.now(UTC))
    return {
        "items": [
            _branch_payload(branch)
            for branch in branches
            if branch.bookable and (any_branch or branch.id in branch_ids)
        ]
    }


@router.get("/tour/branches/{slug}")
async def get_tour_branch(slug: str, session: DbSession):
    try:
        branch = await branch_service.get_by_slug(session, slug)
    except BranchNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )
    if not branch.active or not branch.bookable:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )

    now = datetime.now(UTC)
    event = await event_service.open_tour_event(session, branch, now)
    return {
        "data": {
            "branch": _branch_payload(branch),
            "settings": {
                "tour_intro_html": branch.settings.tour_intro_html if branch.settings else None,
                "arrival_instructions": branch.settings.arrival_instructions
                if branch.settings
                else None,
                "parking_notes": branch.settings.parking_notes if branch.settings else None,
            },
            "event": _event_payload(event, now) if event else None,
            "opening_hours": [
                {
                    "day_of_week": row.day_of_week,
                    "opens_at_local": row.opens_at_local.isoformat(),
                    "closes_at_local": row.closes_at_local.isoformat(),
                }
                for row in branch.opening_hours
                if row.active
            ],
            "closed_dates": _closed_dates(branch, now.date()),
            "venues": await _tourable_venues(session),
        }
    }


@router.post("/tour/branches/{slug}/register", status_code=status.HTTP_201_CREATED)
async def register_for_tour(slug: str, payload: PublicRegistration, session: DbSession):
    try:
        branch = await branch_service.get_by_slug(session, slug)
    except BranchNotFoundError:
        return error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="branch_not_found",
            message="Branch not found.",
        )

    now = datetime.now(UTC)
    event = await event_service.open_tour_event(session, branch, now)
    if event is None:
        return error_response(
            status_code=status.HTTP_409_CONFLICT,
            code="no_open_event",
            message="This branch is not taking tour bookings right now.",
        )

    try:
        registration = await event_service.register(
            session, event=event, branch=branch, payload=payload, now=now, source="public"
        )
    except RegistrationBlocked as blocked:
        code = 422 if blocked.code == "validation_error" else status.HTTP_409_CONFLICT
        return error_response(status_code=code, code=blocked.code, message=blocked.message)

    await _notify(event=event, registration=registration, branch=branch)

    return {
        "data": {
            "id": registration.id,
            "public_id": str(registration.public_id),
            "party_size": registration.party_size,
            "visit_date": registration.visit_date.isoformat() if registration.visit_date else None,
            "visit_slot": registration.visit_slot,
            "branch_name": branch.name,
        }
    }


async def _notify(*, event: Event, registration: EventRegistration, branch: Branch) -> None:
    """Sent after the row is committed, and never allowed to fail the request: a
    mail-provider outage must not cost a lead."""
    reply_to = branch.settings.reply_to_email if branch.settings else branch.public_email
    subject, body = registration_confirmation(
        event=event, registration=registration, branch=branch
    )
    try:
        await send_email(to=[registration.email], subject=subject, text=body, reply_to=reply_to)
    except Exception:  # noqa: BLE001 -- logged, never re-raised
        logger.exception("tour confirmation email failed for registration %s", registration.id)

    await _whatsapp_alert(registration=registration, branch=branch)

    recipients = notification_recipients(branch)
    if not recipients:
        return
    alert_subject, alert_body = branch_alert(
        event=event, registration=registration, branch=branch
    )
    try:
        await send_email(to=recipients, subject=alert_subject, text=alert_body)
    except Exception:  # noqa: BLE001
        logger.exception("branch alert email failed for registration %s", registration.id)


async def _whatsapp_alert(*, registration: EventRegistration, branch: Branch | None) -> None:
    """The team works out of WhatsApp, so an emailed lead is one nobody reads for
    hours. Sent to the same team number the contact forms already alert.

    Best-effort like the emails above, and for the same reason: the registration is
    committed before this runs, so a Bird outage must cost a notification rather
    than the lead.
    """
    facts = [
        f"tour {registration.city or '-'}",
        registration.visit_date.isoformat() if registration.visit_date else "no date",
        f"{registration.party_size} guests",
        branch.name if branch else "-",
    ]
    try:
        await WhatsAppNotifier(get_settings()).send_lead_alert(
            name=registration.guest_name,
            contact=join_contact(registration.mobile, registration.email),
            # The venue, not the page path: a venue tour visits the venue, and that
            # is the first thing the team needs to read.
            page=venue_label(registration) or "venue not named",
            message=join_contact(*facts),
        )
    except Exception:  # noqa: BLE001 -- logged, never re-raised
        logger.exception("whatsapp alert failed for registration %s", registration.id)
