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
    build_parameters,
    join_contact,
    parameter_names,
    resolve_base_url,
)


def make_settings(**overrides: Any) -> Settings:
    """Every Bird field is pinned, including the ones a given test does not
    assert on. Settings falls through to apps/api/.env for anything left unset,
    so omitting one silently couples the suite to whatever a developer happens
    to have configured -- which is exactly how a local stopgap value of
    BIRD_LEAD_TEMPLATE_SLOTS once turned four assertions red."""
    base: dict[str, Any] = {
        "bird_api_key": "bk_us1_testtoken",
        "whatsapp_team_number": "+6580000000",
        "bird_lead_template": "lead_alert",
        "bird_lead_template_language": "id",
        "bird_lead_template_slots": 4,
        "bird_lead_template_params": "",
        "bird_base_url": None,
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


LEAD = {
    "name": "Ayu",
    "contact": "+628123",
    "page": "ritz-carlton",
    "message": "Tanya harga",
}


def test_four_slots_keep_every_field_separate() -> None:
    assert build_parameters(**LEAD, slots=4) == [
        "Ayu",
        "+628123",
        "ritz-carlton",
        "Tanya harga",
    ]


def test_more_slots_than_fields_does_not_pad() -> None:
    # A template with spare slots would otherwise get empty parameters, which
    # WhatsApp rejects.
    assert len(build_parameters(**LEAD, slots=6)) == 4


def test_fewer_slots_merge_from_the_right() -> None:
    """Who the lead is has to stay legible; context collapses instead."""
    assert build_parameters(**LEAD, slots=2) == [
        "Ayu",
        "+628123 / ritz-carlton / Tanya harga",
    ]
    assert build_parameters(**LEAD, slots=3) == [
        "Ayu",
        "+628123",
        "ritz-carlton / Tanya harga",
    ]


def test_one_slot_carries_everything() -> None:
    assert build_parameters(**LEAD, slots=1) == [
        "Ayu / +628123 / ritz-carlton / Tanya harga"
    ]


def test_merged_slots_are_still_flattened_and_bounded() -> None:
    merged = build_parameters(
        name="Ayu",
        contact="+628123",
        page="ritz",
        message="a\nb" + "x" * (MAX_SLOT_CHARS + 200),
        slots=2,
    )
    assert len(merged) == 2
    assert "\n" not in merged[1]
    assert len(merged[1]) <= MAX_SLOT_CHARS


@pytest.mark.anyio
async def test_slot_count_is_honoured_on_the_wire(
    transport: RecordingTransport,
) -> None:
    notifier = WhatsAppNotifier(make_settings(bird_lead_template_slots=2))
    await notifier.send_lead_alert(**LEAD)

    assert sent_parameters(transport) == [
        "Ayu",
        "+628123 / ritz-carlton / Tanya harga",
    ]


@pytest.mark.anyio
async def test_named_parameters_are_sent_when_the_template_declares_them(
    transport: RecordingTransport,
) -> None:
    """Bird rejects the entire send when the shape does not match, and its system
    templates use named parameters -- bird_booking_confirmation declares
    "{{count}}" and "{{date}}". Sending those positionally fails with E15003."""
    notifier = WhatsAppNotifier(
        make_settings(bird_lead_template_slots=2, bird_lead_template_params="count,date")
    )

    await notifier.send_lead_alert(name="Rina", contact="+62811", page="Villa", message="bali")

    parameters = json.loads(transport.request.content)["template"]["components"][0]["parameters"]
    assert [p["name"] for p in parameters] == ["count", "date"]
    assert parameters[0]["text"] == "Rina"


@pytest.mark.anyio
async def test_parameters_stay_positional_when_no_names_are_configured(
    transport: RecordingTransport,
) -> None:
    """A purpose-built template with positional slots must not grow names it never
    declared -- that mismatch is rejected just as hard as the missing one."""
    notifier = WhatsAppNotifier(make_settings(bird_lead_template_params=""))

    await notifier.send_lead_alert(name="Rina", contact="+62811", page="Villa", message="bali")

    parameters = json.loads(transport.request.content)["template"]["components"][0]["parameters"]
    assert all("name" not in p for p in parameters)


def test_extra_names_beyond_the_slot_count_are_ignored() -> None:
    """The slot count is what decides how many parameters go out; the names only
    label them. A stale, longer list must not silently add a slot."""
    assert parameter_names(make_settings(bird_lead_template_params="a, b , c"), slots=2) == [
        "a",
        "b",
    ]
    assert parameter_names(make_settings(bird_lead_template_params=""), slots=2) == []
