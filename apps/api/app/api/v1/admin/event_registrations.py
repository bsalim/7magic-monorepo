"""Registration admin routes: list, create at the front desk, update, export."""

from __future__ import annotations

import csv
import io
from datetime import UTC, datetime

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse
from pydantic import Field

from app.api.v1.admin._shared import (
    BranchScope,
    CurrentUser,
    DbSession,
    conflict,
    forbidden_branch,
    not_found,
)
from app.domains.branches.access import REGISTRATION_READ, REGISTRATION_WRITE, AccessSet
from app.domains.events.models import EventRegistration
from app.domains.events.schemas import (
    EventSchema,
    GuestInput,
    PublicRegistration,
    RegistrationResponse,
    RegistrationUpdate,
)
from app.domains.events.service import (
    EventNotFoundError,
    RegistrationBlocked,
    RegistrationNotFoundError,
    event_service,
)

router = APIRouter()

CSV_HEADER = [
    "Branch",
    "Event",
    "Name",
    "Email",
    "Mobile",
    "Party size",
    "Visit date",
    "Visit slot",
    "Status",
    "Follow up",
    "Source",
    "Registered at",
]


class CmsRegistrationCreate(EventSchema):
    event_id: int
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(min_length=3, max_length=320)
    mobile: str | None = Field(default=None, max_length=40)
    visit_date: str | None = None
    visit_slot: str | None = Field(default=None, max_length=40)
    notes: str | None = None
    guests: list[GuestInput] = Field(default_factory=list)


def _payload(registration: EventRegistration) -> dict:
    response = RegistrationResponse.model_validate(registration).model_dump(mode="json")
    event = registration.event
    response["event_name"] = event.name if event else None
    response["branch_id"] = event.branch_id if event else None
    response["branch_name"] = event.branch.name if event and event.branch else None
    return response


async def _scoped_rows(session, scope, **filters) -> list[EventRegistration]:
    return await event_service.list_registrations(
        session, branch_ids=scope.branches_with(REGISTRATION_READ), **filters
    )


@router.get("/event-registrations")
async def list_registrations(
    session: DbSession,
    scope: BranchScope,
    event_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None),
):
    if not scope.has(REGISTRATION_READ):
        return forbidden_branch()
    rows = await _scoped_rows(session, scope, event_id=event_id, status=status_filter, query=q)
    return {"items": [_payload(row) for row in rows]}


# Declared before the /{registration_id} routes so "export" is never captured as
# an id.
@router.get("/event-registrations/export")
async def export_registrations(
    session: DbSession,
    scope: BranchScope,
    event_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
):
    if not scope.has(REGISTRATION_READ):
        return forbidden_branch()
    rows = await _scoped_rows(session, scope, event_id=event_id, status=status_filter)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for row in rows:
        event = row.event
        writer.writerow(
            [
                event.branch.name if event and event.branch else "",
                event.name if event else "",
                row.guest_name,
                row.email,
                row.mobile or "",
                row.party_size,
                row.visit_date.isoformat() if row.visit_date else "",
                row.visit_slot or "",
                row.status,
                "yes" if row.follow_up else "no",
                row.source,
                row.created_at.isoformat() if row.created_at else "",
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="event-registrations.csv"'},
    )


@router.post("/event-registrations", status_code=status.HTTP_201_CREATED)
async def create_registration(
    payload: CmsRegistrationCreate, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, payload.event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(REGISTRATION_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    public_payload = PublicRegistration.model_validate(
        {
            "name": payload.name,
            "email": payload.email,
            "mobile": payload.mobile,
            "visit_date": payload.visit_date,
            "visit_slot": payload.visit_slot,
            "guests": [guest.model_dump() for guest in payload.guests],
        }
    )
    try:
        registration = await event_service.register(
            session,
            event=event,
            branch=event.branch,
            payload=public_payload,
            now=datetime.now(UTC),
            source="cms",
        )
    except RegistrationBlocked as blocked:
        return conflict(blocked.code, blocked.message)

    if payload.notes:
        registration.notes = payload.notes
        await session.commit()
        await session.refresh(registration)
    return {"data": _payload(registration)}


@router.patch("/event-registrations/{registration_id}")
async def update_registration(
    registration_id: int,
    payload: RegistrationUpdate,
    session: DbSession,
    scope: BranchScope,
    user: CurrentUser,
):
    try:
        registration = await event_service.get_registration(session, registration_id)
    except RegistrationNotFoundError:
        return not_found("registration_not_found", "Registration not found.")
    try:
        scope.assert_branch(REGISTRATION_WRITE, registration.event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    try:
        registration = await event_service.update_registration(
            session, registration_id, payload, acting_user_id=user.id
        )
    except RegistrationBlocked as blocked:
        return conflict(blocked.code, blocked.message)
    return {"data": _payload(registration)}
