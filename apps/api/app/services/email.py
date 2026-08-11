"""Transactional email via Resend.

Used to notify the 7Magic inbox when a couple submits a pricing request or a
contact enquiry. Sending is deliberately best-effort: the lead is already
persisted by the time we get here, so a missing API key or a provider outage
must never turn into a failed submission for the visitor.
"""

from __future__ import annotations

import html
import logging
from typing import Any

import httpx

from app.core.config import Settings, get_settings

logger = logging.getLogger("app.email")

RESEND_ENDPOINT = "https://api.resend.com/emails"
REQUEST_TIMEOUT_SECONDS = 10.0


def _row(label: str, value: Any) -> str:
    if value in (None, ""):
        return ""
    return (
        '<tr>'
        f'<td style="padding:6px 12px 6px 0;color:#6b7280;white-space:nowrap">{html.escape(label)}</td>'
        f'<td style="padding:6px 0"><strong>{html.escape(str(value))}</strong></td>'
        "</tr>"
    )


def render_lead_email(*, heading: str, fields: dict[str, Any]) -> str:
    rows = "".join(_row(label, value) for label, value in fields.items())
    return (
        '<div style="font-family:system-ui,-apple-system,sans-serif;color:#172033">'
        f"<h2 style=\"margin:0 0 4px\">{html.escape(heading)}</h2>"
        '<p style="margin:0 0 16px;color:#6b7280">Sent from the 7Magic website.</p>'
        f'<table style="border-collapse:collapse;font-size:14px">{rows}</table>'
        "</div>"
    )


async def send_email(
    *, to: list[str], subject: str, text: str, reply_to: str | None = None
) -> None:
    """Plain-text send, used by the tour endpoints for both the guest
    confirmation and the branch alert.

    Raises on transport failure rather than swallowing it, unlike EmailNotifier
    below: the tour endpoint decides for itself that a provider outage must not
    fail the request, and it wants the exception logged with the registration id.
    An unset API key is a no-op, so a dev machine never posts live mail.
    """
    settings = get_settings()
    if not settings.resend_api_key or not to:
        logger.warning("Resend is not configured -- no email sent: %s", subject)
        return

    payload: dict[str, Any] = {
        "from": settings.lead_notification_from,
        "to": to,
        "subject": subject,
        "text": text,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        response = await client.post(
            RESEND_ENDPOINT,
            json=payload,
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        )
        response.raise_for_status()


class EmailNotifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def configured(self) -> bool:
        return bool(self._settings.resend_api_key)

    async def send_lead_notification(
        self, *, subject: str, heading: str, fields: dict[str, Any], reply_to: str | None = None
    ) -> bool:
        """Notify the 7Magic inbox. Returns whether the send succeeded; callers
        should not treat False as a request failure."""
        if not self.configured:
            logger.warning(
                "RESEND_API_KEY is not set -- lead saved but no email sent: %s", subject
            )
            return False

        payload: dict[str, Any] = {
            "from": self._settings.lead_notification_from,
            "to": [self._settings.lead_notification_email],
            "subject": subject,
            "html": render_lead_email(heading=heading, fields=fields),
        }
        # Lets the team reply straight to the couple from the notification.
        if reply_to:
            payload["reply_to"] = reply_to

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    RESEND_ENDPOINT,
                    json=payload,
                    headers={"Authorization": f"Bearer {self._settings.resend_api_key}"},
                )
            if response.status_code >= 400:
                logger.warning(
                    "Resend rejected the notification (%s): %s",
                    response.status_code,
                    response.text[:300],
                )
                return False
            return True
        except httpx.HTTPError as exc:
            logger.warning("Could not reach Resend: %s", exc)
            return False
