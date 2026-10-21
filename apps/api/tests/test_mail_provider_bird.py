"""Bird as a mail provider, kept switchable beside SES and Resend.

Bird and Resend are near-identical -- both take a Bearer header and a flat
from/to/subject/html/text body -- so the tests that earn their place are the
ones pinning where Bird differs: its region-derived host, its list-valued
reply_to, and its category, which is "marketing" unless we say otherwise.

No test here reaches the network: every mailer is built with a recording
transport.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from app.core.config import Settings
from app.services.email.base import EmailMessage
from app.services.email.bird import BIRD_EMAIL_PATH, BirdMailer


def make_settings(**overrides: Any) -> Settings:
    """Every mail field is pinned, including ones a given test does not assert
    on. Settings falls through to apps/api/.env for anything left unset, so
    omitting one silently couples the suite to whatever a developer happens to
    have configured -- which is how a local BIRD_LEAD_TEMPLATE_SLOTS once turned
    four assertions in test_whatsapp_notifier red."""
    base: dict[str, Any] = {
        "mail_provider": "resend",
        "resend_api_key": "re_testkey",
        "bird_mail_api_key": "bk_us1_testtoken",
        "bird_mail_category": "transactional",
        "bird_base_url": None,
        "ses_access_key_id": "AKIATESTKEY",
        "ses_secret_access_key": "test-secret",
        "ses_region": "ap-southeast-1",
        "ses_configuration_set": None,
        "lead_notification_from": "7Magic <hello@7magicwedding.com>",
        "lead_notification_email": "info@7magicwedding.com",
        "admin_emails": "",
        "email_logo_url": "",
    }
    base.update(overrides)
    return Settings(**base)


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


def sent(transport: RecordingTransport) -> dict[str, Any]:
    assert transport.request is not None
    return json.loads(transport.request.content)


def bird(transport: RecordingTransport, **overrides: Any) -> BirdMailer:
    return BirdMailer(make_settings(mail_provider="bird", **overrides), transport=transport)


MESSAGE = EmailMessage(to=["dina@example.test"], subject="Hi", text="Hello")


# --- Defaults ------------------------------------------------------------------

def test_bird_mail_category_defaults_to_transactional() -> None:
    """Bird files an unset send as "marketing", which is the wrong bucket for a
    booking confirmation."""
    assert Settings(resend_api_key="re_x").bird_mail_category == "transactional"


# --- Bird on the wire ---------------------------------------------------------



@pytest.mark.asyncio
async def test_bird_posts_to_the_host_its_key_names() -> None:
    """Bird derives the region from the key itself (bk_{region}_{token}), so a
    key from another region needs no config change."""
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert transport.request is not None
    assert str(transport.request.url) == f"https://us1.platform.bird.com{BIRD_EMAIL_PATH}"


@pytest.mark.asyncio
async def test_bird_authenticates_with_bearer() -> None:
    """Bird's own SDK sends Bearer and the live API accepts it. The AccessKey
    scheme in the Channels API docs is a different surface and does not apply."""
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert transport.request is not None
    assert transport.request.headers["Authorization"] == "Bearer bk_us1_testtoken"


@pytest.mark.asyncio
async def test_bird_sends_the_configured_from_address_verbatim() -> None:
    """Bird accepts an RFC 5322 mailbox string, so one setting serves both
    providers."""
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert sent(transport)["from"] == "7Magic <hello@7magicwedding.com>"


@pytest.mark.asyncio
async def test_bird_carries_every_recipient() -> None:
    """A branch alert goes to every address the branch lists."""
    transport = RecordingTransport()

    await bird(transport).send(
        EmailMessage(to=["one@example.test", "two@example.test"], subject="Hi", text="Hello")
    )

    assert sent(transport)["to"] == ["one@example.test", "two@example.test"]


@pytest.mark.asyncio
async def test_bird_sends_html_beside_its_text_alternative() -> None:
    transport = RecordingTransport()

    await bird(transport).send(
        EmailMessage(to=["a@b.test"], subject="Hi", text="Plain", html="<p>Rich</p>")
    )

    payload = sent(transport)
    assert payload["html"] == "<p>Rich</p>"
    assert payload["text"] == "Plain"


@pytest.mark.asyncio
async def test_bird_omits_html_when_there_is_none() -> None:
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert "html" not in sent(transport)


@pytest.mark.asyncio
async def test_bird_wraps_reply_to_in_a_list() -> None:
    """Bird takes a list here where Resend takes a scalar."""
    transport = RecordingTransport()

    await bird(transport).send(
        EmailMessage(to=["a@b.test"], subject="Hi", text="Hello", reply_to="team@7magic.test")
    )

    assert sent(transport)["reply_to"] == ["team@7magic.test"]


@pytest.mark.asyncio
async def test_bird_omits_reply_to_entirely_when_unset() -> None:
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert "reply_to" not in sent(transport)


@pytest.mark.asyncio
async def test_bird_always_states_the_category() -> None:
    """Left unset, Bird files the send as marketing."""
    transport = RecordingTransport()

    await bird(transport).send(MESSAGE)

    assert sent(transport)["category"] == "transactional"


@pytest.mark.asyncio
async def test_bird_treats_202_as_success() -> None:
    """Bird returns 202 accepted, not 200."""
    await bird(RecordingTransport(status_code=202)).send(MESSAGE)


@pytest.mark.asyncio
async def test_bird_raises_on_a_rejected_send() -> None:
    """Raising is the contract; each caller decides what to do about it."""
    with pytest.raises(httpx.HTTPStatusError):
        await bird(RecordingTransport(status_code=422)).send(MESSAGE)


# --- Configuration -----------------------------------------------------------


def test_bird_is_unconfigured_without_a_key() -> None:
    assert not BirdMailer(make_settings(bird_mail_api_key=None)).configured


def test_bird_is_unconfigured_when_its_key_names_no_region() -> None:
    """A malformed key yields no host, which is as unsendable as no key at all."""
    assert not BirdMailer(make_settings(bird_mail_api_key="not-a-bird-key")).configured


def test_bird_is_configured_with_a_well_formed_key() -> None:
    assert BirdMailer(make_settings()).configured



def test_the_bird_mail_key_falls_back_to_the_shared_access_key(monkeypatch) -> None:
    """A single-key setup needs no extra config; a separate mail key lets it be
    rotated without touching WhatsApp.

    The variable must be *absent* for the fallback, not empty: an alias that is
    set wins even when its value is blank, so `BIRD_MAIL_API_KEY=` in a dotenv
    file means "no mail key" rather than "use the shared one".

    `_env_file=None` because apps/api/.env supplies a real BIRD_MAIL_API_KEY on a
    developer machine, and reading it would answer a different question.
    """
    monkeypatch.delenv("BIRD_MAIL_API_KEY", raising=False)
    monkeypatch.setenv("BIRD_ACCESS_KEY", "bk_us1_shared")

    assert Settings(_env_file=None).bird_mail_api_key == "bk_us1_shared"


def test_an_empty_mail_key_does_not_fall_back(monkeypatch) -> None:
    """Set-but-blank is not the same as unset, and the difference decides whether
    mail sends at all. Pinned because it is the opposite of what the word
    "fallback" suggests."""
    monkeypatch.setenv("BIRD_MAIL_API_KEY", "")
    monkeypatch.setenv("BIRD_ACCESS_KEY", "bk_us1_shared")

    assert Settings(_env_file=None).bird_mail_api_key == ""


def test_a_dedicated_mail_key_wins_over_the_shared_one(monkeypatch) -> None:
    monkeypatch.setenv("BIRD_MAIL_API_KEY", "bk_us1_mailonly")
    monkeypatch.setenv("BIRD_ACCESS_KEY", "bk_us1_shared")

    assert Settings(_env_file=None).bird_mail_api_key == "bk_us1_mailonly"
