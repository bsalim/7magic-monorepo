"""Event admin routes. Registrations live in event_registrations.py and email
templates in event_emails.py -- one resource family per module."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.api.v1.admin._shared import (
    BranchScope,
    CurrentUser,
    DbSession,
    forbidden_branch,
    not_found,
)
from app.domains.branches.access import EVENT_READ, EVENT_WRITE, AccessSet
from app.domains.events.models import Event
from app.domains.events.schemas import EventCreate, EventResponse, EventUpdate
from app.domains.events.service import EventNotFoundError, event_service

router = APIRouter()


def _payload(event: Event, registration_count: int = 0, head_count: int = 0) -> dict:
    response = EventResponse.model_validate(event).model_dump(by_alias=True, mode="json")
    response["branchName"] = event.branch.name if event.branch else None
    response["registrationCount"] = registration_count
    response["headCount"] = head_count
    return response


@router.get("/events")
async def list_events(
    session: DbSession,
    scope: BranchScope,
    branch_id: int | None = Query(default=None, alias="branchId"),
):
    if not scope.has(EVENT_READ):
        return forbidden_branch()

    permitted = scope.branches_with(EVENT_READ)
    if branch_id is not None:
        try:
            scope.assert_branch(EVENT_READ, branch_id)
        except AccessSet.BranchForbidden:
            return forbidden_branch()
        permitted = [branch_id]

    rows = await event_service.list(session, branch_ids=permitted)
    return {"items": [_payload(event, count, heads) for event, count, heads in rows]}


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(
    payload: EventCreate, session: DbSession, scope: BranchScope, user: CurrentUser
):
    # branch_id None is a company-wide event, so only an org-wide grant may create it.
    try:
        scope.assert_branch(EVENT_WRITE, payload.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    event = await event_service.create(session, payload, created_by_user_id=user.id)
    return {"data": _payload(event)}


@router.get("/events/{event_id}")
async def get_event(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    heads = await event_service.head_count(session, event.id)
    return {"data": _payload(event, head_count=heads)}


@router.patch("/events/{event_id}")
async def update_event(
    event_id: int, payload: EventUpdate, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
        if "branch_id" in payload.model_dump(exclude_unset=True):
            scope.assert_branch(EVENT_WRITE, payload.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    event = await event_service.update(session, event_id, payload)
    return {"data": _payload(event)}


@router.delete("/events/{event_id}")
async def delete_event(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()
    await event_service.delete(session, event_id)
    return {"data": {"deleted": True}}
