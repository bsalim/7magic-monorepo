# Bird Mail Provider and Shared Email Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put Resend and Bird behind one mail interface selected by `MAIL_PROVIDER`, and render every transactional email through one HTML shell with a header, footer and logo.

**Architecture:** `app/services/email.py` becomes a package. `base.py` defines an `EmailMessage` and a `Mailer` protocol; `resend.py` and `bird.py` each own one provider's payload; `service.py` keeps the two public entry points (`send_email`, `EmailNotifier`) and picks a mailer; `layout.py` renders the HTML. Callers import from `app.services.email` exactly as they do now, so no call site changes.

**Tech Stack:** Python 3.12+, FastAPI, Pydantic Settings, `httpx` (no SDK — Bird's REST API is six JSON fields), pytest.

**Spec:** `docs/superpowers/specs/2026-08-14-bird-mail-provider-and-email-layout-design.md`

---

## File Structure

| File | Responsibility |
|---|---|
| `app/core/config.py` | Four new settings (modify) |
| `app/services/email/__init__.py` | Re-export the public surface. No logic. |
| `app/services/email/base.py` | `EmailMessage`, `Mailer` protocol. Knows no provider. |
| `app/services/email/layout.py` | HTML shell, `paragraphs()`, `render_lead_email()`. No I/O. |
| `app/services/email/resend.py` | `ResendMailer`. Knows nothing of Bird. |
| `app/services/email/bird.py` | `BirdMailer`. Knows nothing of Resend. |
| `app/services/email/service.py` | `get_mailer()`, `send_email()`, `EmailNotifier`. Builds no wire payloads. |
| `tests/test_mail_providers.py` | Provider selection, both payloads, the three preserved contracts |
| `tests/test_email_layout.py` | Escaping, paragraph structure, logo fallback |

**Delete:** `app/services/email.py` (its contents move into the package).

---

### Task 1: Configuration

**Files:**
- Modify: `apps/api/app/core/config.py:47-62`
- Test: `apps/api/tests/test_mail_providers.py`

- [ ] **Step 1: Write the failing test**

Create `apps/api/tests/test_mail_providers.py`:

```python
"""Mail provider selection and the two provider payloads.

Bird and Resend are near-identical on the wire -- both take a Bearer header and
a flat from/to/subject/html/text body -- so the tests that matter are the ones
pinning where they differ: Bird's region-derived host, its list-valued reply_to,
and its category default, which is `marketing` unless we say otherwise.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make_settings(**overrides: Any) -> Settings:
    """Every mail field is pinned. Settings falls through to apps/api/.env for
    anything left unset, so omitting one couples the suite to whatever a
    developer happens to have configured locally."""
    base: dict[str, Any] = {
        "mail_provider": "resend",
        "resend_api_key": "re_testkey",
        "bird_mail_api_key": "bk_us1_testtoken",
        "bird_mail_category": "transactional",
        "lead_notification_from": "7Magic <hello@7magicwedding.com>",
        "lead_notification_email": "info@7magicwedding.com",
        "email_logo_url": "",
    }
    base.update(overrides)
    return Settings(**base)


def test_mail_provider_defaults_to_resend() -> None:
    assert make_settings().mail_provider == "resend"


def test_bird_is_a_valid_provider() -> None:
    assert make_settings(mail_provider="bird").mail_provider == "bird"


def test_an_unknown_provider_fails_at_settings_construction() -> None:
    """A typo must not degrade to silently sending nothing."""
    with pytest.raises(ValidationError):
        make_settings(mail_provider="sendgrid")


def test_bird_mail_category_defaults_to_transactional() -> None:
    """Bird defaults a send to `marketing`, which is the wrong bucket for a
    booking confirmation."""
    settings = Settings(resend_api_key="re_x")
    assert settings.bird_mail_category == "transactional"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: FAIL — `ValidationError` on unknown field `mail_provider`, or `AttributeError`.

- [ ] **Step 3: Add the settings**

In `apps/api/app/core/config.py`, add `Literal` to the `typing` import if absent, then insert after the `lead_notification_from` field (around line 62):

```python
    # Which provider actually sends. Both are configured independently, so a
    # switch is this one variable and a restart -- and switching back is the
    # same. A Literal rather than a str: a typo must fail at boot, not degrade
    # to silently sending nothing.
    mail_provider: Literal["resend", "bird"] = Field(
        default="resend",
        validation_alias=AliasChoices("mail_provider", "MAIL_PROVIDER"),
    )
    # Separate from BIRD_ACCESS_KEY so the mail key can be rotated or scoped
    # without touching WhatsApp; the fallbacks mean a single-key setup works
    # with no extra config.
    bird_mail_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "bird_mail_api_key", "BIRD_MAIL_API_KEY", "BIRD_ACCESS_KEY", "BIRD_API_KEY"
        ),
    )
    # Bird buckets an unset send as "marketing", which is wrong for a booking
    # confirmation and changes how it is filtered and unsubscribed from.
    bird_mail_category: str = Field(
        default="transactional",
        validation_alias=AliasChoices("bird_mail_category", "BIRD_MAIL_CATEGORY"),
    )
    # Absolute https URL. Blank renders the wordmark instead, which is also what
    # a reader with images blocked sees.
    email_logo_url: str = Field(
        default="",
        validation_alias=AliasChoices("email_logo_url", "EMAIL_LOGO_URL"),
    )
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/core/config.py apps/api/tests/test_mail_providers.py
git commit -m "feat(api): settings for mail provider selection and Bird mail"
```

---

### Task 2: The package skeleton, with Resend moved in unchanged

This task must not change behaviour. The full suite is the proof.

**Files:**
- Create: `apps/api/app/services/email/__init__.py`, `base.py`, `layout.py`, `resend.py`, `service.py`
- Delete: `apps/api/app/services/email.py`

- [ ] **Step 1: Capture the current baseline**

Run: `cd apps/api && uv run pytest -q`
Expected: `241 passed`. Write the number down; Step 6 must match it.

- [ ] **Step 2: Create `base.py`**

```python
"""What a mailer is, independent of who sends it."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EmailMessage:
    """One outbound email, provider-agnostic.

    `text` is required rather than optional: a send with no plain-text
    alternative is a deliverability problem, and making it non-optional means
    no future caller can forget it. `reply_to` stays scalar because that is
    what every caller has -- Bird's list form is that provider's concern.
    """

    to: list[str]
    subject: str
    text: str
    html: str | None = None
    reply_to: str | None = None


class Mailer(Protocol):
    @property
    def configured(self) -> bool: ...

    async def send(self, message: EmailMessage) -> None:
        """Deliver, or raise. Swallowing belongs to the caller: the tour
        endpoint wants the exception logged with its registration id, while the
        lead notifier wants a bool."""
        ...
```

- [ ] **Step 3: Create `layout.py` with the existing renderer moved in verbatim**

Move `_row` and `render_lead_email` out of the old `email.py` with no edits:

```python
"""Email HTML. No I/O, no provider knowledge -- just markup."""

from __future__ import annotations

import html
from typing import Any


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
```

- [ ] **Step 4: Create `resend.py`**

```python
"""Transactional email via Resend."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings

from .base import EmailMessage

logger = logging.getLogger("app.email")

RESEND_ENDPOINT = "https://api.resend.com/emails"
REQUEST_TIMEOUT_SECONDS = 10.0


class ResendMailer:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

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

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                RESEND_ENDPOINT,
                json=payload,
                headers={"Authorization": f"Bearer {self._settings.resend_api_key}"},
            )
            response.raise_for_status()
```

- [ ] **Step 5: Create `service.py` and `__init__.py`**

`service.py`:

```python
"""The two public ways to send mail, and the choice of who sends it.

Sending is deliberately best-effort at both entry points: the lead or the
registration is already persisted by the time we get here, so a missing key or
a provider outage must never turn into a failed submission for the visitor.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings, get_settings

from .base import EmailMessage, Mailer
from .layout import render_lead_email
from .resend import ResendMailer

logger = logging.getLogger("app.email")


def get_mailer(settings: Settings) -> Mailer:
    """One provider, chosen at call time from config."""
    if settings.mail_provider == "bird":
        from .bird import BirdMailer

        return BirdMailer(settings)
    return ResendMailer(settings)


async def send_email(
    *, to: list[str], subject: str, text: str, reply_to: str | None = None
) -> None:
    """Plain-text send, used by the tour endpoints for both the guest
    confirmation and the branch alert.

    Raises on transport failure rather than swallowing it, unlike EmailNotifier
    below: the tour endpoint decides for itself that a provider outage must not
    fail the request, and it wants the exception logged with the registration id.
    An unconfigured provider is a no-op, so a dev machine never posts live mail.
    """
    settings = get_settings()
    mailer = get_mailer(settings)
    if not mailer.configured or not to:
        logger.warning(
            "%s is not configured -- no email sent: %s", settings.mail_provider, subject
        )
        return

    await mailer.send(
        EmailMessage(to=to, subject=subject, text=text, reply_to=reply_to)
    )


class EmailNotifier:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._mailer = get_mailer(settings)

    @property
    def configured(self) -> bool:
        return self._mailer.configured

    async def send_lead_notification(
        self, *, subject: str, heading: str, fields: dict[str, Any], reply_to: str | None = None
    ) -> bool:
        """Notify the 7Magic inbox. Returns whether the send succeeded; callers
        should not treat False as a request failure."""
        if not self.configured:
            logger.warning(
                "%s is not configured -- lead saved but no email sent: %s",
                self._settings.mail_provider,
                subject,
            )
            return False

        text_lines = [heading, ""]
        text_lines += [f"{label}: {value}" for label, value in fields.items() if value]
        message = EmailMessage(
            to=[self._settings.lead_notification_email],
            subject=subject,
            text="\n".join(text_lines),
            html=render_lead_email(heading=heading, fields=fields),
            # Lets the team reply straight to the couple from the notification.
            reply_to=reply_to,
        )

        try:
            await self._mailer.send(message)
            return True
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "%s rejected the notification (%s): %s",
                self._settings.mail_provider,
                exc.response.status_code,
                exc.response.text[:300],
            )
            return False
        except httpx.HTTPError as exc:
            logger.warning("Could not reach %s: %s", self._settings.mail_provider, exc)
            return False
```

`__init__.py`:

```python
"""Transactional email.

The package's public surface is exactly what it was when this was one module,
so callers are unchanged. Providers live in `resend.py` and `bird.py`; pick one
with MAIL_PROVIDER.
"""

from .base import EmailMessage, Mailer
from .layout import render_lead_email
from .service import EmailNotifier, get_mailer, send_email

__all__ = [
    "EmailMessage",
    "EmailNotifier",
    "Mailer",
    "get_mailer",
    "render_lead_email",
    "send_email",
]
```

- [ ] **Step 6: Delete the old module and run the full suite**

```bash
cd apps/api && rm app/services/email.py && uv run pytest -q
```

Expected: the same `241 passed` from Step 1. Any change in that number is a regression from this task, not a pre-existing failure.

- [ ] **Step 7: Lint**

Run: `cd apps/api && uv run ruff check .`
Expected: `All checks passed!`

- [ ] **Step 8: Commit**

```bash
git add apps/api/app/services/email apps/api/app/services/email.py
git commit -m "refactor(api): email becomes a package behind a Mailer interface"
```

---

### Task 3: BirdMailer

**Files:**
- Create: `apps/api/app/services/email/bird.py`
- Modify: `apps/api/tests/test_mail_providers.py`

- [ ] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_mail_providers.py`:

```python
import json

import httpx

from app.services.email.base import EmailMessage
from app.services.email.bird import BIRD_EMAIL_PATH, BirdMailer


class RecordingTransport(httpx.AsyncBaseTransport):
    """Captures the request instead of reaching the provider."""

    def __init__(self, status_code: int = 202, error: Exception | None = None) -> None:
        self.status_code = status_code
        self.error = error
        self.request: httpx.Request | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        if self.error is not None:
            raise self.error
        return httpx.Response(self.status_code, json={"id": "em_1", "status": "accepted"})


def sent_payload(transport: RecordingTransport) -> dict[str, Any]:
    assert transport.request is not None
    return json.loads(transport.request.content)


@pytest.mark.asyncio
async def test_bird_posts_to_the_region_derived_host(monkeypatch) -> None:
    """Bird derives the host from the key itself (bk_{region}_{token}), so a key
    from another region needs no config change."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))

    assert transport.request is not None
    assert str(transport.request.url) == f"https://us1.platform.bird.com{BIRD_EMAIL_PATH}"


@pytest.mark.asyncio
async def test_bird_authenticates_with_bearer() -> None:
    """Bird's own SDK sends Bearer, and the live API accepts it -- the Channels
    API's AccessKey scheme is a different surface."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))

    assert transport.request is not None
    assert transport.request.headers["Authorization"] == "Bearer bk_us1_testtoken"


@pytest.mark.asyncio
async def test_bird_sends_the_configured_from_address_verbatim() -> None:
    """Bird accepts an RFC 5322 mailbox string, so the one setting serves both
    providers."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))

    assert sent_payload(transport)["from"] == "7Magic <hello@7magicwedding.com>"


@pytest.mark.asyncio
async def test_bird_carries_every_recipient() -> None:
    """A branch alert goes to every notification recipient the branch lists."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(
        EmailMessage(to=["one@b.com", "two@b.com"], subject="Hi", text="Hello")
    )

    assert sent_payload(transport)["to"] == ["one@b.com", "two@b.com"]


@pytest.mark.asyncio
async def test_bird_sends_html_with_a_text_alternative() -> None:
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(
        EmailMessage(to=["a@b.com"], subject="Hi", text="Plain", html="<p>Rich</p>")
    )

    payload = sent_payload(transport)
    assert payload["html"] == "<p>Rich</p>"
    assert payload["text"] == "Plain"


@pytest.mark.asyncio
async def test_bird_omits_html_when_there_is_none() -> None:
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Plain"))

    assert "html" not in sent_payload(transport)


@pytest.mark.asyncio
async def test_bird_wraps_reply_to_in_a_list() -> None:
    """Bird takes a list here where Resend takes a scalar."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(
        EmailMessage(to=["a@b.com"], subject="Hi", text="Hello", reply_to="c@d.com")
    )

    assert sent_payload(transport)["reply_to"] == ["c@d.com"]


@pytest.mark.asyncio
async def test_bird_omits_reply_to_entirely_when_unset() -> None:
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))

    assert "reply_to" not in sent_payload(transport)


@pytest.mark.asyncio
async def test_bird_always_sets_the_category() -> None:
    """Left unset, Bird files the send as marketing."""
    transport = RecordingTransport()
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))

    assert sent_payload(transport)["category"] == "transactional"


@pytest.mark.asyncio
async def test_bird_treats_202_as_success() -> None:
    """Bird returns 202 accepted, not 200."""
    transport = RecordingTransport(status_code=202)
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))


@pytest.mark.asyncio
async def test_bird_raises_on_a_rejected_send() -> None:
    """Raising is the contract; each caller decides what to do about it."""
    transport = RecordingTransport(status_code=422)
    mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    with pytest.raises(httpx.HTTPStatusError):
        await mailer.send(EmailMessage(to=["a@b.com"], subject="Hi", text="Hello"))


def test_bird_is_unconfigured_without_a_key() -> None:
    assert not BirdMailer(make_settings(bird_mail_api_key=None)).configured


def test_bird_is_unconfigured_when_the_key_yields_no_region() -> None:
    """A malformed key gives no host to POST to, which is as unconfigured as
    having no key at all."""
    assert not BirdMailer(make_settings(bird_mail_api_key="not-a-bird-key")).configured


def test_bird_is_configured_with_a_well_formed_key() -> None:
    assert BirdMailer(make_settings()).configured
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.services.email.bird'`

- [ ] **Step 3: Write `bird.py`**

```python
"""Transactional email via Bird.

Bird's Email API is a different surface from the Channels API its docs lead
with: `/v1/email/messages` is addressed by region alone -- no workspace id, no
channel id -- and takes a flat body near-identical to Resend's. Auth is Bearer,
matching `services/whatsapp.py`, which talks to the same platform.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import Settings
from app.services.whatsapp import resolve_base_url

from .base import EmailMessage

logger = logging.getLogger("app.email")

BIRD_EMAIL_PATH = "/v1/email/messages"
REQUEST_TIMEOUT_SECONDS = 10.0


class BirdMailer:
    def __init__(
        self, settings: Settings, *, transport: httpx.AsyncBaseTransport | None = None
    ) -> None:
        self._settings = settings
        # Injected only by tests, so no send in the suite can reach the network.
        self._transport = transport

    @property
    def _base_url(self) -> str | None:
        return resolve_base_url_for(self._settings)

    @property
    def configured(self) -> bool:
        # A malformed key yields no host, which is as unsendable as no key.
        return bool(self._settings.bird_mail_api_key and self._base_url)

    async def send(self, message: EmailMessage) -> None:
        payload: dict[str, Any] = {
            "from": self._settings.lead_notification_from,
            "to": message.to,
            "subject": message.subject,
            "text": message.text,
            # Unset, Bird files the send as "marketing", which is the wrong
            # bucket for a booking confirmation.
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
                f"{self._base_url}{BIRD_EMAIL_PATH}",
                json=payload,
                headers={"Authorization": f"Bearer {self._settings.bird_mail_api_key}"},
            )
            response.raise_for_status()


def resolve_base_url_for(settings: Settings) -> str | None:
    """The mail key's region host.

    `whatsapp.resolve_base_url` reads `bird_api_key`; mail has its own key
    setting, so the same rule is applied to that one via a throwaway copy of the
    settings rather than a second implementation of the parsing.
    """
    if settings.bird_base_url:
        return settings.bird_base_url.rstrip("/")
    return resolve_base_url(
        settings.model_copy(update={"bird_api_key": settings.bird_mail_api_key})
    )
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: PASS (18 passed)

If `pytest.mark.asyncio` errors with "async def functions are not natively supported", check `pyproject.toml` has `pytest-asyncio` in the dev group (it does) and add `asyncio_mode = "auto"` under `[tool.pytest.ini_options]`, or keep the explicit markers.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services/email/bird.py apps/api/tests/test_mail_providers.py
git commit -m "feat(api): send transactional email through Bird"
```

---

### Task 4: Provider selection and the three preserved contracts

**Files:**
- Modify: `apps/api/tests/test_mail_providers.py`

- [ ] **Step 1: Write the failing tests**

Append:

```python
from app.services.email.resend import ResendMailer
from app.services.email.service import EmailNotifier, get_mailer


def test_resend_is_the_default_mailer() -> None:
    assert isinstance(get_mailer(make_settings()), ResendMailer)


def test_bird_is_selected_by_config() -> None:
    assert isinstance(get_mailer(make_settings(mail_provider="bird")), BirdMailer)


@pytest.mark.asyncio
async def test_lead_notification_returns_false_and_does_not_raise_on_failure() -> None:
    """leads.py treats False as 'saved, not notified'. It must never see an
    exception -- the lead row is already committed."""
    transport = RecordingTransport(error=httpx.ConnectError("boom"))
    notifier = EmailNotifier(make_settings(mail_provider="bird"))
    notifier._mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_lead_notification_returns_false_when_rejected() -> None:
    transport = RecordingTransport(status_code=422)
    notifier = EmailNotifier(make_settings(mail_provider="bird"))
    notifier._mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    result = await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_lead_notification_sends_html_and_a_text_alternative() -> None:
    transport = RecordingTransport()
    notifier = EmailNotifier(make_settings(mail_provider="bird"))
    notifier._mailer = BirdMailer(make_settings(mail_provider="bird"), transport=transport)

    await notifier.send_lead_notification(
        subject="New enquiry", heading="New contact enquiry", fields={"Name": "Dina"}
    )

    payload = sent_payload(transport)
    assert "Dina" in payload["html"]
    assert "Dina" in payload["text"]


def test_an_unconfigured_notifier_reports_it() -> None:
    notifier = EmailNotifier(make_settings(mail_provider="resend", resend_api_key=None))
    assert notifier.configured is False


@pytest.mark.asyncio
async def test_an_unconfigured_notifier_returns_false_without_sending() -> None:
    notifier = EmailNotifier(make_settings(mail_provider="resend", resend_api_key=None))

    assert await notifier.send_lead_notification(
        subject="s", heading="h", fields={"Name": "Dina"}
    ) is False
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: FAIL — the notifier tests fail if `EmailNotifier` does not expose `_mailer`.

- [ ] **Step 3: No implementation needed if Task 2's `service.py` was written as specified**

`EmailNotifier.__init__` already sets `self._mailer = get_mailer(settings)`. If any test fails, fix `service.py` rather than the test.

- [ ] **Step 4: Run the whole suite**

Run: `cd apps/api && uv run pytest -q`
Expected: all pass, count = 241 + the new tests.

- [ ] **Step 5: Commit**

```bash
git add apps/api/tests/test_mail_providers.py
git commit -m "test(api): pin provider selection and the best-effort send contracts"
```

---

### Task 5: The HTML layout

**Files:**
- Modify: `apps/api/app/services/email/layout.py`
- Test: `apps/api/tests/test_email_layout.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/api/tests/test_email_layout.py`:

```python
"""The shared email shell.

Email clients are not browsers: Outlook renders through Word, Gmail strips
<style> blocks, and about half of clients block remote images by default. The
tests that matter are the ones pinning escaping (CMS text and guest-supplied
names both flow through here untrusted) and the images-off fallback.
"""

from __future__ import annotations

from app.services.email.layout import paragraphs, render_email, render_lead_email


def test_paragraphs_escapes_before_it_structures() -> None:
    """A guest named <script> must not become markup. Escaping first is the
    whole safety argument -- CMS templates and guest input both land here."""
    result = paragraphs("<script>alert(1)</script>")

    assert "<script>" not in result
    assert "&lt;script&gt;" in result


def test_paragraphs_escapes_ampersands() -> None:
    assert "Dina &amp; Rangga" in paragraphs("Dina & Rangga")


def test_blank_lines_become_separate_paragraphs() -> None:
    result = paragraphs("Halo Dina,\n\nTur Anda dikonfirmasi.")

    assert result.count("<p") == 2


def test_single_newlines_become_line_breaks() -> None:
    result = paragraphs("Venue: Jakarta\nDate: 2026-05-17")

    assert result.count("<p") == 1
    assert "<br" in result


def test_blank_text_produces_no_paragraphs() -> None:
    assert paragraphs("") == ""


def test_an_unknown_placeholder_survives_rendering() -> None:
    """domains/events/emails.py renders unknown tokens literally rather than
    raising mid-send; the layout must not undo that."""
    assert "{unknown_token}" in paragraphs("Hi {unknown_token}")


def test_the_wordmark_renders_when_no_logo_is_configured() -> None:
    """Blank is also what a reader with images blocked effectively sees."""
    result = render_email(heading="Booking confirmed", body_html="<p>Hi</p>", logo_url="")

    assert "7MAGIC" in result
    assert "<img" not in result


def test_a_configured_logo_renders_as_an_image_with_alt_text() -> None:
    result = render_email(
        heading="Booking confirmed",
        body_html="<p>Hi</p>",
        logo_url="https://media.7magicwedding.com/logo.png",
    )

    assert '<img' in result
    assert 'src="https://media.7magicwedding.com/logo.png"' in result
    assert 'alt=""' not in result


def test_the_body_is_placed_inside_the_shell() -> None:
    result = render_email(heading="Booking confirmed", body_html="<p>Hello Dina</p>")

    assert "<p>Hello Dina</p>" in result


def test_the_heading_is_escaped() -> None:
    result = render_email(heading="A & B", body_html="<p>x</p>")

    assert "A &amp; B" in result


def test_the_layout_uses_tables_not_divs_for_structure() -> None:
    """A div-based layout collapses in Outlook, which renders through Word."""
    result = render_email(heading="Hi", body_html="<p>x</p>")

    assert "<table" in result


def test_a_preheader_is_hidden_but_present() -> None:
    """The line clients show beside the subject. Unset, they scrape whatever
    text comes first, which is usually the logo alt text."""
    result = render_email(
        heading="Hi", body_html="<p>x</p>", preheader="Your tour is confirmed"
    )

    assert "Your tour is confirmed" in result
    assert "display:none" in result


def test_lead_email_still_renders_its_fields() -> None:
    """Unchanged contract: leads.py passes a dict and expects a table."""
    result = render_lead_email(heading="New enquiry", fields={"Name": "Dina"})

    assert "Dina" in result
    assert "New enquiry" in result


def test_lead_email_skips_blank_fields() -> None:
    result = render_lead_email(heading="New enquiry", fields={"Name": "Dina", "City": ""})

    assert "City" not in result
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_email_layout.py -q`
Expected: FAIL — `ImportError: cannot import name 'paragraphs'`

- [ ] **Step 3: Implement**

Add to `apps/api/app/services/email/layout.py`, above `_row`:

```python
from app.core.config import get_settings

# 600px is the width that survives every client and phone. Fonts are a system
# stack because web fonts do not load in most email clients.
_FONT = "system-ui,-apple-system,'Segoe UI',sans-serif"
_INK = "#172033"
_MUTED = "#6b7280"


def paragraphs(text: str) -> str:
    """Escape CMS-authored plain text, then structure it.

    Escaping comes first and that ordering is the point: template text and
    guest-supplied values both arrive here untrusted. This is a different job
    from core/html.py, which allowlists tags an author is permitted to write --
    here authors write no HTML at all, so escaping everything is correct.
    """
    blocks = [block for block in text.split("\n\n") if block.strip()]
    return "".join(
        f'<p style="margin:0 0 16px;font-size:15px;line-height:1.6;color:{_INK}">'
        f"{html.escape(block.strip()).replace(chr(10), '<br />')}"
        "</p>"
        for block in blocks
    )


def _header(logo_url: str) -> str:
    """An <img> when a logo is configured, a wordmark otherwise. The wordmark is
    not a placeholder -- it is what the roughly half of readers who block remote
    images see, so it has to look deliberate."""
    if logo_url:
        inner = (
            f'<img src="{html.escape(logo_url)}" alt="7Magic Wedding" '
            'width="160" style="display:block;border:0;max-width:160px;height:auto" />'
        )
    else:
        inner = (
            f'<span style="font-family:{_FONT};font-size:18px;letter-spacing:.18em;'
            f'font-weight:600;color:{_INK}">7MAGIC WEDDING</span>'
        )
    return (
        f'<tr><td style="padding:28px 32px 20px;border-bottom:1px solid #e5e7eb">{inner}</td></tr>'
    )


def _footer(note: str | None) -> str:
    lines = [
        '7Magic Wedding &middot; <a href="https://7magicwedding.com" '
        f'style="color:{_MUTED}">7magicwedding.com</a>'
    ]
    if note:
        lines.append(html.escape(note))
    body = "<br />".join(lines)
    return (
        '<tr><td style="padding:20px 32px 28px;border-top:1px solid #e5e7eb;'
        f'font-family:{_FONT};font-size:12px;line-height:1.6;color:{_MUTED}">{body}</td></tr>'
    )


def render_email(
    *,
    heading: str,
    body_html: str,
    preheader: str | None = None,
    footer_note: str | None = None,
    logo_url: str | None = None,
) -> str:
    """Wrap a rendered body in the header/footer shell.

    Tables and inline styles throughout: a div-and-flexbox layout collapses in
    Outlook, and a <style> block is stripped by Gmail.
    """
    if logo_url is None:
        logo_url = get_settings().email_logo_url

    hidden = ""
    if preheader:
        # Shown beside the subject in the inbox list, never in the body.
        hidden = (
            '<div style="display:none;max-height:0;overflow:hidden;opacity:0">'
            f"{html.escape(preheader)}</div>"
        )

    return (
        f'<div style="background:#f6f7f9;padding:24px 0">{hidden}'
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        'width="100%" style="max-width:600px;margin:0 auto;background:#ffffff;'
        'border:1px solid #e5e7eb;border-radius:8px">'
        f"{_header(logo_url)}"
        f'<tr><td style="padding:28px 32px;font-family:{_FONT}">'
        f'<h1 style="margin:0 0 16px;font-size:20px;line-height:1.3;color:{_INK}">'
        f"{html.escape(heading)}</h1>"
        f"{body_html}</td></tr>"
        f"{_footer(footer_note)}"
        "</table></div>"
    )
```

Then change `render_lead_email` to use the shell:

```python
def render_lead_email(*, heading: str, fields: dict[str, Any]) -> str:
    rows = "".join(_row(label, value) for label, value in fields.items())
    body = (
        f'<p style="margin:0 0 16px;color:{_MUTED};font-size:14px">'
        "Sent from the 7Magic website.</p>"
        f'<table style="border-collapse:collapse;font-size:14px;color:{_INK}">{rows}</table>'
    )
    return render_email(heading=heading, body_html=body, preheader=heading)
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd apps/api && uv run pytest tests/test_email_layout.py -q`
Expected: PASS (14 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/services/email/layout.py apps/api/tests/test_email_layout.py
git commit -m "feat(api): one HTML shell for every transactional email"
```

---

### Task 6: Tour emails gain HTML

**Files:**
- Modify: `apps/api/app/services/email/service.py`
- Modify: `apps/api/tests/test_mail_providers.py`

`registration_confirmation()` and `branch_alert()` keep returning `(subject, text)`. The wrapping happens in `send_email`, so `domains/events/emails.py` gains no knowledge of HTML.

- [ ] **Step 1: Write the failing tests**

Append to `apps/api/tests/test_mail_providers.py`:

```python
@pytest.mark.asyncio
async def test_send_email_wraps_plain_text_in_the_shell(monkeypatch) -> None:
    """The tour emails are authored as plain text; the HTML is derived, so the
    domain module never has to know about markup."""
    from app.core import config as config_module
    from app.services.email import service as service_module

    settings = make_settings(mail_provider="bird")
    monkeypatch.setattr(service_module, "get_settings", lambda: settings)
    transport = RecordingTransport()
    monkeypatch.setattr(
        service_module, "get_mailer", lambda s: BirdMailer(s, transport=transport)
    )

    await service_module.send_email(
        to=["a@b.com"],
        subject="Your booking is confirmed",
        text="Hi Dina,\n\nVenue: Jakarta\nDate: 2026-05-17",
    )

    payload = sent_payload(transport)
    # The original text still ships as the alternative part.
    assert payload["text"] == "Hi Dina,\n\nVenue: Jakarta\nDate: 2026-05-17"
    # And an HTML sibling was derived from it.
    assert "<p" in payload["html"]
    assert "Hi Dina," in payload["html"]
    assert "7MAGIC WEDDING" in payload["html"]


@pytest.mark.asyncio
async def test_send_email_escapes_guest_supplied_text(monkeypatch) -> None:
    from app.services.email import service as service_module

    settings = make_settings(mail_provider="bird")
    monkeypatch.setattr(service_module, "get_settings", lambda: settings)
    transport = RecordingTransport()
    monkeypatch.setattr(
        service_module, "get_mailer", lambda s: BirdMailer(s, transport=transport)
    )

    await service_module.send_email(
        to=["a@b.com"], subject="s", text="Name: <script>alert(1)</script>"
    )

    assert "<script>" not in sent_payload(transport)["html"]
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -k send_email_wraps -q`
Expected: FAIL — `KeyError: 'html'`, because `send_email` sends text only.

- [ ] **Step 3: Implement**

In `service.py`, add the layout import:

```python
from .layout import paragraphs, render_email, render_lead_email
```

and change the send in `send_email`:

```python
    await mailer.send(
        EmailMessage(
            to=to,
            subject=subject,
            text=text,
            # Derived, not authored: the CMS templates are plain text and stay
            # that way, and the original ships as the alternative part.
            html=render_email(
                heading=subject, body_html=paragraphs(text), preheader=subject
            ),
            reply_to=reply_to,
        )
    )
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd apps/api && uv run pytest tests/test_mail_providers.py -q`
Expected: PASS

- [ ] **Step 5: Run the whole suite and lint**

Run: `cd apps/api && uv run pytest -q && uv run ruff check .`
Expected: all pass; `All checks passed!`

The three tour tests in `tests/test_public_tour_api.py:123,151,171` monkeypatch `tour_module.send_email` and assert on the text, so they are unaffected. If one fails, the wrapping leaked into the wrong argument.

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/services/email/service.py apps/api/tests/test_mail_providers.py
git commit -m "feat(api): tour emails ship HTML alongside their plain text"
```

---

### Task 7: Document the env vars

**Files:**
- Modify: `deploy/env/api.env.example`

- [ ] **Step 1: Add the block**

After the existing Bird section:

```bash
# --- Transactional email ------------------------------------------------------
# Which provider sends. "resend" (default) or "bird". Both can stay configured;
# this picks one, so switching back is this variable and a restart.
MAIL_PROVIDER=resend
# Bird's mail key. Separate from BIRD_ACCESS_KEY so it can be rotated without
# touching WhatsApp; falls back to BIRD_ACCESS_KEY when unset. The region host
# is derived from the bk_{region}_ prefix, so no base URL is needed.
BIRD_MAIL_API_KEY=
# Bird files an unset send as "marketing". A booking confirmation is not that.
BIRD_MAIL_CATEGORY=transactional
# Absolute https URL. Blank renders a text wordmark, which is also what a reader
# with images blocked sees.
EMAIL_LOGO_URL=
```

- [ ] **Step 2: Verify nothing references a channel id**

Run: `rg -n "BIRD_EMAIL_CHANNEL|MAIL_FROM_USERNAME" deploy/ apps/api/ || echo "clean"`
Expected: `clean` — the Email API needs neither.

- [ ] **Step 3: Commit**

```bash
git add deploy/env/api.env.example
git commit -m "docs(deploy): document the mail provider env vars"
```

---

### Task 8: Verify against the live Bird API

Not a test in the suite — a one-off check that the built code sends, run once by hand. The suite must never reach the network.

- [ ] **Step 1: Set the key and provider in `apps/api/.env`**

```bash
MAIL_PROVIDER=bird
BIRD_MAIL_API_KEY=<the bk_us1_... key>
LEAD_NOTIFICATION_FROM=Bird <onboarding@messagebird.dev>
```

The sandbox sender works on a bare key. Sending as `7magicwedding.com` needs the domain verified in Bird first (DKIM, SPF, return-path CNAME).

- [ ] **Step 2: Send one through the real code path**

```bash
cd apps/api && uv run python -c "
import asyncio
from app.services.email import send_email
asyncio.run(send_email(
    to=['byonosalim@gmail.com'],
    subject='7Magic layout check',
    text='Hi Dina,\n\nVenue: Jakarta\nDate: 2026-05-17\nGuests: 2\n\nSee you soon!\nThe 7Magic team',
))
print('sent')
"
```

Expected: `sent`, and an email that renders with the header, wordmark and footer.

- [ ] **Step 3: Check the rendering in a real client**

Open it on a phone and in Gmail's web client. Confirm: the shell is centred and under 600px, the wordmark shows with images blocked, and the paragraphs have not run together.

- [ ] **Step 4: Put the provider back**

Set `MAIL_PROVIDER=resend` in `.env` unless the switch is meant to go live now.

---

## Self-Review

**Spec coverage.** Provider interface → Task 2. `BirdMailer` → Task 3. Selection by config → Tasks 1 and 4. The three preserved contracts → Task 4, plus the unchanged `tests/test_public_tour_api.py`. Layout, `paragraphs`, logo fallback → Task 5. Lead notification through the shell → Task 5. Tour emails through the shell with text retained → Task 6. Config surface → Tasks 1 and 7. Live verification → Task 8.

**Known deviation.** The spec's file table gives `layout.py` the job of holding `render_lead_email`; Task 2 moves it there verbatim and Task 5 rewrites its body to use the shell. Two steps, one destination — deliberate, so Task 2 can prove it changed nothing.

**Type consistency.** `EmailMessage(to, subject, text, html, reply_to)` is constructed in `service.py` only and read in both mailers. `Mailer.configured` is a property in the protocol and in both implementations. `render_email` takes `logo_url` in every call and test; `paragraphs` takes one positional `str`.
