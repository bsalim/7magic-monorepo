"""Public Ba Zi calculator for the wedding tools, and the gate in front of its result.

The calculator computes and answers; nothing in that request is stored or
logged. It is a POST, not a GET, so the couple's birth dates never sit in a URL,
a browser history or an access log.

The page holds the result back until the couple has given their contact details,
and posts those here with the calculation they are unlocking. That stores the
shared tool lead and emails them their Ba Zi card and a copy of the result. The gate is soft, like the
other tools': the calculator itself does not enforce it.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_website_lead_submission
from app.core.config import get_settings
from app.core.database import get_db_session
from app.domains.bazi.emails import result_copy
from app.domains.bazi.response import build_response
from app.domains.bazi.schemas import BaziLeadCreate, BaziRequest, BaziResponse
from app.schemas.content import ToolLeadResponse
from app.services.email import send_email
from app.services.leads import lead_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/bazi", response_model=BaziResponse)
def bazi(payload: BaziRequest) -> BaziResponse:
    return build_response(payload)


@router.post(
    "/bazi/leads",
    dependencies=[Depends(require_website_lead_submission)],
    response_model=ToolLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_bazi_lead(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    payload: BaziLeadCreate,
) -> ToolLeadResponse:
    await lead_service.create_tool_lead(session, payload)
    # A tripped honeypot stored nothing, so it is sent nothing either -- and it
    # gets the same answer, so a bot cannot tell.
    if not payload.website:
        await _send_copy(payload)
    return ToolLeadResponse()


async def _send_copy(payload: BaziLeadCreate) -> None:
    """Sent after the lead is committed, and never allowed to fail the request:
    the page reveals the result on a 201, and a mail-provider outage must not
    withhold what the couple just gave their details for."""
    calculation = payload.calculation
    subject, body, body_html = result_copy(build_response(calculation), calculation.locale)
    # A reply to the copy is a couple with a question, so it goes to the people
    # who answer leads rather than to a sending-only address.
    team = get_settings().lead_recipients
    try:
        await send_email(
            to=[payload.email],
            subject=subject,
            text=body,
            body_html=body_html,
            reply_to=team[0] if team else None,
            locale=calculation.locale,
        )
    except Exception:  # noqa: BLE001 -- logged, never re-raised
        # No address and no birth data in the log line: neither belongs there.
        logger.exception("ba zi result copy failed to send")
