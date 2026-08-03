"""WhatsApp lead alerts via Bird.

The rules worth pinning down are the ones Meta enforces on template parameters:
a newline or an empty value gets the whole send rejected, so those have to be
handled before the payload is built rather than discovered in production. The
rest covers the best-effort contract -- the lead is already committed when the
notifier runs, so nothing here may raise.
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from app.core.config import Settings
from app.services.whatsapp import (
    EMPTY_SLOT,
    MAX_SLOT_CHARS,
    WhatsAppNotifier,
    join_contact,
    resolve_base_url,
)


def make_settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "bird_api_key": "bk_us1_testtoken",
        "whatsapp_team_number": "+6580000000",
        "bird_lead_template": "lead_alert",
        "bird_lead_template_language": "id",
    }
    base.update(overrides)
    return Settings(**base)


class RecordingTransport(httpx.AsyncBaseTransport):
    """Captures the request instead of reaching Bird."""

    def __init__(self, status_code: int = 200, error: Exception | None = None) -> None:
        self.status_code = status_code
        self.error = error
        self.request: httpx.Request | None = None

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.request = request
        if self.error is not None:
            raise self.error
        return httpx.Response(self.status_code, json={"id": "wam_test"})


def patch_transport(
    monkeypatch: pytest.MonkeyPatch, recorder: RecordingTransport
) -> RecordingTransport:
    """The notifier builds its own AsyncClient, so the transport is injected via
    the constructor rather than passed in."""
    original = httpx.AsyncClient.__init__

    def patched(self: httpx.AsyncClient, *args: Any, **kwargs: Any) -> None:
        kwargs["transport"] = recorder
        original(self, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    return recorder


@pytest.fixture
def transport(monkeypatch: pytest.MonkeyPatch) -> RecordingTransport:
    return patch_transport(monkeypatch, RecordingTransport())


def sent_parameters(recorder: RecordingTransport) -> list[str]:
    assert recorder.request is not None
    body = json.loads(recorder.request.content)
    return [p["text"] for p in body["template"]["components"][0]["parameters"]]


def test_base_url_comes_from_the_key_region() -> None:
    assert resolve_base_url(make_settings()) == "https://us1.platform.bird.com"
    assert (
        resolve_base_url(make_settings(bird_api_key="bk_eu1_x"))
        == "https://eu1.platform.bird.com"
    )


def test_base_url_override_wins_and_loses_its_trailing_slash() -> None:
    assert resolve_base_url(make_settings(bird_base_url="https://stub.local/")) == (
        "https://stub.local"
    )


def test_base_url_is_none_for_a_key_without_a_region() -> None:
    # A malformed key must not produce a request to a nonsense host.
    assert resolve_base_url(make_settings(bird_api_key="legacy-token")) is None


@pytest.mark.parametrize(
    "overrides",
    [
        {"bird_api_key": None},
        {"whatsapp_team_number": None},
        {"bird_api_key": "legacy-token"},
    ],
    ids=["no key", "no team number", "unusable key"],
)
def test_not_configured_without_the_essentials(overrides: dict[str, Any]) -> None:
    assert WhatsAppNotifier(make_settings(**overrides)).configured is False


@pytest.mark.anyio
async def test_unconfigured_send_is_a_no_op_not_an_error(
    transport: RecordingTransport,
) -> None:
    notifier = WhatsAppNotifier(make_settings(bird_api_key=None))
    assert await notifier.send_lead_alert(name="Rina") is False
    # The lead is already saved by this point; no outbound call must be attempted.
    assert transport.request is None


@pytest.mark.anyio
async def test_send_posts_the_template_payload(transport: RecordingTransport) -> None:
    notifier = WhatsAppNotifier(make_settings())

    sent = await notifier.send_lead_alert(
        name="Rina",
        contact="+628123 / rina@example.com",
        page="ayana-bali",
        message="Mau tanya paket",
    )
    assert sent is True

    request = transport.request
    assert request is not None
    assert str(request.url) == "https://us1.platform.bird.com/v1/whatsapp/messages"
    assert request.headers["authorization"] == "Bearer bk_us1_testtoken"

    body = json.loads(request.content)
    assert body["to"] == "+6580000000"
    assert body["template"]["slug"] == "lead_alert"
    assert body["template"]["language"] == "id"
    assert sent_parameters(transport) == [
        "Rina",
        "+628123 / rina@example.com",
        "ayana-bali",
        "Mau tanya paket",
    ]


@pytest.mark.anyio
async def test_newlines_are_flattened_out_of_parameters(
    transport: RecordingTransport,
) -> None:
    """Meta rejects the whole send when a parameter contains a line break, and a
    pasted enquiry almost always has one."""
    notifier = WhatsAppNotifier(make_settings())
    await notifier.send_lead_alert(message="Halo,\n\nSaya mau\ttanya    harga.")

    message = sent_parameters(transport)[3]
    assert message == "Halo, Saya mau tanya harga."
    assert "\n" not in message and "\t" not in message


@pytest.mark.anyio
async def test_blank_fields_become_a_placeholder(transport: RecordingTransport) -> None:
    """An empty string is rejected as a parameter, so every slot needs content."""
    notifier = WhatsAppNotifier(make_settings())
    await notifier.send_lead_alert(name="Rina", contact=None, page="", message="   ")

    assert sent_parameters(transport) == ["Rina", EMPTY_SLOT, EMPTY_SLOT, EMPTY_SLOT]


@pytest.mark.anyio
async def test_long_messages_are_truncated_within_the_limit(
    transport: RecordingTransport,
) -> None:
    notifier = WhatsAppNotifier(make_settings())
    await notifier.send_lead_alert(message="a" * (MAX_SLOT_CHARS + 500))

    message = sent_parameters(transport)[3]
    assert len(message) <= MAX_SLOT_CHARS
    assert message.endswith("…")


@pytest.mark.anyio
async def test_provider_rejection_returns_false_without_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A rejected template (wrong slug, bad parameter) must not surface as an
    exception -- the lead is already committed."""
    recorder = patch_transport(monkeypatch, RecordingTransport(status_code=422))
    notifier = WhatsAppNotifier(make_settings())

    assert await notifier.send_lead_alert(name="Rina") is False
    assert recorder.request is not None


@pytest.mark.anyio
async def test_unreachable_provider_returns_false_without_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    patch_transport(
        monkeypatch, RecordingTransport(error=httpx.ConnectError("no route"))
    )
    notifier = WhatsAppNotifier(make_settings())

    assert await notifier.send_lead_alert(name="Rina") is False


def test_join_contact_drops_blanks_and_keeps_order() -> None:
    assert join_contact("+628123", None, "a@b.com") == "+628123 / a@b.com"
    assert join_contact(None, "") == EMPTY_SLOT
