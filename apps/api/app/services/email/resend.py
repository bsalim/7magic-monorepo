"""Transactional email via Resend."""

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings

from .base import EmailMessage

RESEND_ENDPOINT = "https://api.resend.com/emails"
REQUEST_TIMEOUT_SECONDS = 10.0


class ResendMailer:
    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._settings = settings
        # Injected only by tests, so no send in the suite can reach the network.
        self._transport = transport

    @property
    def configured(self) -> bool:
        return bool(self._settings.resend_api_key)

    async def send(self, message: EmailMessage) -> None:
        payload: dict[str, Any] = {
            "from": self._settings.lead_notification_from,
            "to": message.to,
            "subject": message.subject,
            "text": message.text,
        }
        if message.html:
            payload["html"] = message.html
        if message.reply_to:
            payload["reply_to"] = message.reply_to

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT_SECONDS, transport=self._transport
        ) as client:
            response = await client.post(
                RESEND_ENDPOINT,
                json=payload,
                headers={"Authorization": f"Bearer {self._settings.resend_api_key}"},
            )
            response.raise_for_status()
