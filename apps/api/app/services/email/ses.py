"""Transactional email via Amazon SES (the v2 API).

SES has its own credentials, never the `AWS_*` ones. Those names already belong
to R2 in this app's env files (see `r2_access_key_id` in config), and because
systemd loads the env file into the process environment, boto3 would also pick
up `AWS_ENDPOINT_URL` -- R2's host -- for every client it builds. So the
credentials and the endpoint are both passed explicitly, leaving boto3 nothing
to resolve from the environment.
"""

from __future__ import annotations

from typing import Any

from anyio import to_thread
from botocore.config import Config

from app.core.config import Settings

from .base import EmailMessage

REQUEST_TIMEOUT_SECONDS = 10.0
CHARSET = "UTF-8"


def ses_endpoint(region: str) -> str:
    return f"https://email.{region}.amazonaws.com"


class SesMailer:
    def __init__(self, settings: Settings, *, client: Any | None = None) -> None:
        self._settings = settings
        # Injected only by tests (a botocore Stubber), so no send in the suite
        # can reach the network.
        self._client = client

    @property
    def configured(self) -> bool:
        # No region default: SES sending identities are per region, so a guessed
        # one would fail every send with a "not verified" error anyway.
        return bool(
            self._settings.ses_access_key_id
            and self._settings.ses_secret_access_key
            and self._settings.ses_region
        )

    def _get_client(self) -> Any:
        if self._client is None:
            import boto3

            region = self._settings.ses_region
            self._client = boto3.client(
                "sesv2",
                region_name=region,
                endpoint_url=ses_endpoint(region),
                aws_access_key_id=self._settings.ses_access_key_id,
                aws_secret_access_key=self._settings.ses_secret_access_key,
                # Matches the other providers' 10 s ceiling. One retry rather
                # than botocore's default of several: the visitor's request is
                # waiting on this, and the send is best-effort anyway.
                config=Config(
                    connect_timeout=REQUEST_TIMEOUT_SECONDS,
                    read_timeout=REQUEST_TIMEOUT_SECONDS,
                    retries={"max_attempts": 2, "mode": "standard"},
                ),
            )
        return self._client

    def _request(self, message: EmailMessage) -> dict[str, Any]:
        body: dict[str, Any] = {"Text": {"Data": message.text, "Charset": CHARSET}}
        if message.html:
            body["Html"] = {"Data": message.html, "Charset": CHARSET}

        request: dict[str, Any] = {
            "FromEmailAddress": self._settings.lead_notification_from,
            "Destination": {"ToAddresses": message.to},
            "Content": {
                "Simple": {
                    # Explicit, or SES assumes 7-bit ASCII and mangles Indonesian
                    # copy with an em dash or a curly quote in it.
                    "Subject": {"Data": message.subject, "Charset": CHARSET},
                    "Body": body,
                }
            },
        }
        if message.reply_to:
            request["ReplyToAddresses"] = [message.reply_to]
        if self._settings.ses_configuration_set:
            request["ConfigurationSetName"] = self._settings.ses_configuration_set
        return request

    async def send(self, message: EmailMessage) -> None:
        request = self._request(message)
        # boto3 is blocking, so it runs off the event loop -- the same reason
        # storage.py wraps its R2 calls. Raises botocore's ClientError on a
        # rejected send.
        await to_thread.run_sync(lambda: self._get_client().send_email(**request))
