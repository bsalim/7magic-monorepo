"""Transactional email via Bird.

Bird's Email API is a different, simpler surface from the Channels API its docs
lead with. `/v1/email/messages` is addressed by region alone -- no workspace id,
no channel id -- and takes a flat body near-identical to Resend's. Auth is
Bearer, matching `services/whatsapp.py`, which talks to the same platform; the
`AccessKey` scheme in the Channels documentation does not apply here.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings
from app.services.whatsapp import resolve_base_url

from .base import EmailMessage

BIRD_EMAIL_PATH = "/v1/email/messages"
REQUEST_TIMEOUT_SECONDS = 10.0


def resolve_mail_base_url(settings: Settings) -> str | None:
    """The mail key's region host, derived from the key and nothing else.

    `whatsapp.resolve_base_url` applies the `bk_{region}_{token}` rule to
    `bird_api_key`; mail has its own key setting, so the same rule is applied to
    that one through a throwaway copy rather than a second implementation of the
    parsing.

    `BIRD_BASE_URL` is deliberately *not* honoured here. It is WhatsApp's
    override, and reusing it cross-wired the two: an operator pinning the EU
    host for an EU WhatsApp key would silently send every mail request there
    with a US mail key, and both call sites swallow the resulting 401 -- so
    confirmations would vanish with nothing to show for it. Tests reach the
    mailer through an injected transport, so no override is needed for them.
    """
    return resolve_base_url(
        settings.model_copy(update={"bird_api_key": settings.bird_mail_api_key})
    )


class BirdMailer:
    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._settings = settings
        # Injected only by tests, so no send in the suite can reach the network.
        self._transport = transport

    @property
    def configured(self) -> bool:
        # A malformed key yields no host, which is as unsendable as no key.
        return bool(self._settings.bird_mail_api_key and resolve_mail_base_url(self._settings))

    async def send(self, message: EmailMessage) -> None:
        payload: dict[str, Any] = {
            "from": self._settings.lead_notification_from,
            "to": message.to,
            "subject": message.subject,
            "text": message.text,
            # Left unset, Bird files the send as "marketing" -- the wrong bucket
            # for a booking confirmation, and it changes how the message is
            # filtered and what unsubscribe handling applies.
            "category": self._settings.bird_mail_category,
        }
        if message.html:
            payload["html"] = message.html
        if message.reply_to:
            # A list here, where Resend takes a scalar.
            payload["reply_to"] = [message.reply_to]

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS, transport=self._transport
        ) as client:
            response = await client.post(
                f"{resolve_mail_base_url(self._settings)}{BIRD_EMAIL_PATH}",
                json=payload,
                headers={"Authorization": f"Bearer {self._settings.bird_mail_api_key}"},
            )
            # 202 accepted, not 200 -- raise_for_status treats any 2xx as fine.
            response.raise_for_status()
