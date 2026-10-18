"""Lead admin routes: a read-only list and a CSV export. HTTP only -- every query
lives in lead_service.

Contact-form, venue-pricing and wedding-tool leads all share `contact_leads`, so
this one resource covers them; `source` tells them apart.
"""

from __future__ import annotations

import csv
import io
import json
import re
from datetime import date

from fastapi import APIRouter, Query, status
from fastapi.responses import StreamingResponse

from app.api.v1.admin._shared import BranchScope, DbSession
from app.core.errors import error_response
from app.domains.branches.access import LEAD_READ, AccessSet
from app.services.leads import lead_service

router = APIRouter()

CSV_HEADER = ["Date", "Source", "Name", "Email", "Phone", "Page", "Message", "Details"]
PLAIN_PHONE = re.compile(r"\+?\d{6,20}")


def _cell(value: object) -> str:
    # Every text column here was typed by a member of the public, and the team
    # opens this file in Excel or Sheets, which run a cell starting with = + - @
    # as a formula. A leading apostrophe makes it plain text (OWASP's advice).
    text = "" if value is None else str(value)
    return f"'{text}" if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def _may_read_leads(scope: AccessSet) -> bool:
    # No branch means "a record of every branch", which assert_branch lets only an
    # org-wide grant touch. Leads are exactly that: not branch data, and personal.
    try:
        scope.assert_branch(LEAD_READ, None)
    except AccessSet.BranchForbidden:
        return False
    return True


def _forbidden():
    return error_response(
        status_code=status.HTTP_403_FORBIDDEN,
        code="lead_forbidden",
        message="Leads need an organisation-wide lead:read permission.",
    )


@router.get("/leads")
async def list_leads(
    session: DbSession,
    scope: BranchScope,
    source: str | None = Query(default=None, max_length=50),
    q: str | None = Query(default=None, max_length=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
):
    if not _may_read_leads(scope):
        return _forbidden()
    result = await lead_service.list_leads(
        session, source=source, query=q, date_from=date_from, date_to=date_to, page=page
    )
    return result.model_dump(mode="json")


@router.get("/leads.csv")
async def export_leads(
    session: DbSession,
    scope: BranchScope,
    source: str | None = Query(default=None, max_length=50),
    q: str | None = Query(default=None, max_length=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
):
    if not _may_read_leads(scope):
        return _forbidden()
    leads = await lead_service.export_leads(
        session, source=source, query=q, date_from=date_from, date_to=date_to
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(CSV_HEADER)
    for lead in leads:
        writer.writerow(
            [
                lead.created_at or "",
                lead.source,
                _cell(lead.full_name),
                _cell(lead.email),
                # Tool leads store +62..., which the guard would prefix with a
                # stray apostrophe; contact forms store free text, which needs it.
                lead.mobile if PLAIN_PHONE.fullmatch(lead.mobile or "") else _cell(lead.mobile),
                _cell(lead.source_path),
                _cell(lead.message),
                # Each source stores different extras (tool inputs, venue, wedding
                # date), so they travel as one JSON cell rather than ragged columns.
                json.dumps(lead.metadata, ensure_ascii=False) if lead.metadata else "",
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leads.csv"'},
    )
