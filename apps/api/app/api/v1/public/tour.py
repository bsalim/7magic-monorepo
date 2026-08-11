"""Public Book a Tour endpoints. No auth: these are the website's forms."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.errors import error_response
from app.domains.branches.models import Branch
from app.domains.branches.service import BranchNotFoundError, branch_service
from app.domains.events.emails import (
    branch_alert,
    notification_recipients,
    registration_confirmation,
)
from app.domains.events.models import Event, EventRegistration
from app.domains.events.schemas import PublicRegistration
from app.domains.events.service import (
    RegistrationBlocked,
    event_service,
    registration_block,
)
from app.services.email import send_email

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
        "addressLine1": branch.address_line1,
        "addressLine2": branch.address_line2,
        "timezone": branch.timezone,
        "publicPhone": branch.public_phone,
        "publicEmail": branch.public_email,
        "whatsappNumber": branch.whatsapp_number,
        "websiteUrl": branch.website_url,
    }


def _event_payload(event: Event, now: datetime) -> dict:
    block = registration_block(event, now)
    return {
        "id": event.id,
        "publicId": str(event.public_id),
        "name": event.name,
        "descriptionHtml": event.description_html,
        "coverImageUrl": event.cover_image_url,
        "venue": event.venue,
        "eventStartAt": event.event_start_at.isoformat() if event.event_start_at else None,
        "eventEndAt": event.event_end_at.isoformat() if event.event_end_at else None,
        "registrationOpen": block is None,
        "registrationClosedReason": block[1] if block else None,
    }


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


@router.get("/tour/branches")
async def list_tour_branches(session: DbSession):
    branches = await branch_service.list(session, active_only=True)
    return {"items": [_branch_payload(branch) for branch in branches if branch.bookable]}


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
                "tourIntroHtml": branch.settings.tour_intro_html if branch.settings else None,
                "arrivalInstructions": branch.settings.arrival_instructions
                if branch.settings
                else None,
                "parkingNotes": branch.settings.parking_notes if branch.settings else None,
            },
            "event": _event_payload(event, now) if event else None,
            "openingHours": [
                {
                    "dayOfWeek": row.day_of_week,
                    "opensAtLocal": row.opens_at_local.isoformat(),
                    "closesAtLocal": row.closes_at_local.isoformat(),
                }
                for row in branch.opening_hours
                if row.active
            ],
            "closedDates": _closed_dates(branch, now.date()),
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
            "publicId": str(registration.public_id),
            "partySize": registration.party_size,
            "visitDate": registration.visit_date.isoformat() if registration.visit_date else None,
            "visitSlot": registration.visit_slot,
            "branchName": branch.name,
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
