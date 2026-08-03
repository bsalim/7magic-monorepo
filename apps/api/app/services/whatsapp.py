"""Lead alerts over WhatsApp, via Bird.

Bird carries WhatsApp only -- the Resend email sent next to every call site here
is unchanged. Sending is best-effort for the same reason it is in `email.py`:
the lead is already committed by the time we get here, so a missing key or a
provider outage must cost a notification, never the submission.

Bird's current API accepts approved templates only; there is no free-form text
field. The alert is therefore one `utility` template and this module fills its
four slots. Meta rejects the entire send if a parameter contains a newline, a
tab, or a run of four or more spaces -- and a pasted enquiry routinely has line
breaks -- which is why every value goes through `_slot` rather than into the
payload directly.
"""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from app.core.config import Settings

logger = logging.getLogger("app.whatsapp")

MESSAGES_PATH = "/v1/whatsapp/messages"
REQUEST_TIMEOUT_SECONDS = 10.0
# Meta caps the rendered template body. Trimming each slot well inside that keeps
# one long enquiry from pushing the whole alert over the limit.
MAX_SLOT_CHARS = 300
# WhatsApp rejects an empty parameter outright, so a missing field needs a stand-in.
EMPTY_SLOT = "-"

_WHITESPACE = re.compile(r"\s+")


def _slot(value: Any, *, limit: int = MAX_SLOT_CHARS) -> str:
    """Collapse a lead field into something WhatsApp accepts as a parameter."""
    text = _WHITESPACE.sub(" ", str(value or "")).strip()
    if not text:
        return EMPTY_SLOT
    if len(text) > limit:
        # Trim so the ellipsis fits inside the limit rather than exceeding it.
        text = text[: limit - 1].rstrip() + "…"
    return text


def join_contact(*parts: Any) -> str:
    """One slot has to carry both phone and email; blanks drop out."""
    return " / ".join(_WHITESPACE.sub(" ", str(p)).strip() for p in parts if p) or EMPTY_SLOT


def resolve_base_url(settings: Settings) -> str | None:
    """Bird derives the host from the key itself (`bk_{region}_{token}`), so a
    key from another region needs no config change. An override exists mainly so
    tests can point at a local stub."""
    if settings.bird_base_url:
        return settings.bird_base_url.rstrip("/")
    parts = (settings.bird_api_key or "").split("_")
    if len(parts) >= 3 and parts[0] == "bk" and parts[1]:
        return f"https://{parts[1]}.platform.bird.com"
    return None


class WhatsAppNotifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def configured(self) -> bool:
        # The team number is as required as the key: without it there is nobody
        # to alert, and Bird would reject the send anyway.
        return bool(
            self._settings.bird_api_key
            and self._settings.whatsapp_team_number
            and resolve_base_url(self._settings)
        )

    async def send_lead_alert(
        self,
        *,
        name: Any = None,
        contact: Any = None,
        page: Any = None,
        message: Any = None,
    ) -> bool:
        """Alert the team number about a new lead. Returns whether the send
        succeeded; callers must not treat False as a request failure."""
        if not self.configured:
            logger.warning(
                "Bird is not configured -- lead saved but no WhatsApp alert sent for %s",
                _slot(name),
            )
            return False

        payload: dict[str, Any] = {
            "to": self._settings.whatsapp_team_number,
            "template": {
                "slug": self._settings.bird_lead_template,
                "language": self._settings.bird_lead_template_language,
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": _slot(name)},
                            {"type": "text", "text": _slot(contact)},
                            {"type": "text", "text": _slot(page)},
                            {"type": "text", "text": _slot(message)},
                        ],
                    }
                ],
            },
        }

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{resolve_base_url(self._settings)}{MESSAGES_PATH}",
                    json=payload,
                    headers={"Authorization": f"Bearer {self._settings.bird_api_key}"},
                )
            if response.status_code >= 400:
                logger.warning(
                    "Bird rejected the WhatsApp alert (%s): %s",
                    response.status_code,
                    response.text[:300],
                )
                return False
            return True
        except httpx.HTTPError as exc:
            logger.warning("Could not reach Bird: %s", exc)
            return False
