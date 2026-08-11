"""Per-event email templates: read, save, preview."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import Field

from app.api.v1.admin._shared import BranchScope, DbSession, conflict, forbidden_branch, not_found
from app.domains.branches.access import EVENT_READ, EVENT_WRITE, AccessSet
from app.domains.events.emails import (
    PLACEHOLDERS,
    build_replacements,
    default_template,
    render_template,
    template_for,
)
from app.domains.events.models import TEMPLATE_KINDS, EventEmailTemplate
from app.domains.events.schemas import EventSchema
from app.domains.events.service import EventNotFoundError, event_service

router = APIRouter()


class TemplateUpsert(EventSchema):
    subject: str = Field(default="", max_length=300)
    body: str = ""
    enabled: bool = False


def _template_payload(kind: str, row: EventEmailTemplate | None) -> dict:
    fallback = default_template(kind)
    return {
        "kind": kind,
        "subject": row.subject if row and row.subject else fallback["subject"],
        "body": row.body if row and row.body else fallback["body"],
        "enabled": bool(row.enabled) if row else False,
    }


@router.get("/events/{event_id}/email-templates")
async def list_email_templates(event_id: int, session: DbSession, scope: BranchScope):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    stored = {row.kind: row for row in event.email_templates}
    return {
        "data": {
            "placeholders": PLACEHOLDERS,
            "templates": [_template_payload(kind, stored.get(kind)) for kind in TEMPLATE_KINDS],
        }
    }


@router.put("/events/{event_id}/email-templates/{kind}")
async def upsert_email_template(
    event_id: int, kind: str, payload: TemplateUpsert, session: DbSession, scope: BranchScope
):
    if kind not in TEMPLATE_KINDS:
        return conflict("invalid_template_kind", f"Unknown template kind '{kind}'.")
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_WRITE, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    row = await template_for(session, event_id, kind)
    if row is None:
        row = EventEmailTemplate(event_id=event_id, kind=kind)
        session.add(row)
    row.subject = payload.subject
    row.body = payload.body
    row.enabled = payload.enabled
    await session.commit()
    await session.refresh(row)
    return {"data": _template_payload(kind, row)}


@router.post("/events/{event_id}/email-templates/{kind}/preview")
async def preview_email_template(
    event_id: int, kind: str, payload: TemplateUpsert, session: DbSession, scope: BranchScope
):
    try:
        event = await event_service.get(session, event_id)
    except EventNotFoundError:
        return not_found("event_not_found", "Event not found.")
    try:
        scope.assert_branch(EVENT_READ, event.branch_id)
    except AccessSet.BranchForbidden:
        return forbidden_branch()

    # Preview against a real registration when one exists, so the team sees the
    # actual shape of a name and date rather than lorem ipsum.
    rows = await event_service.list_registrations(session, event_id=event_id)
    replacements = build_replacements(
        event=event,
        registration=rows[0] if rows else None,
        branch_name=event.branch.name if event.branch else None,
    )
    return {
        "data": {
            "subject": render_template(payload.subject, replacements),
            "body": render_template(payload.body, replacements),
        }
    }
