"""The wedding-tool lead gate: POST /api/v1/public/tool-leads.

A couple unlocks the mahar card with email + WhatsApp. The row lands in
`contact_leads` beside the contact-form leads, and the team is alerted the same
way, so a tool lead is worked exactly like any other enquiry.
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.models import ContactLead
from app.services.leads import lead_service

ENDPOINT = "/api/v1/public/tool-leads"


def _payload(**overrides) -> dict:
    payload = {
        "tool": "mahar",
        "email": "andre@example.com",
        "phone": "+6281234567890",
        "names": "Andre & Amanda",
        "inputs": {"method": "akad", "variant": "dmy", "date": "2026-09-20", "amount": 20092026},
        "consent": True,
        "source_path": "/wedding-tools/mahar-tanggal-pernikahan",
        "website": "",
    }
    payload.update(overrides)
    return payload


def _leads(api) -> list[ContactLead]:
    async def fetch() -> list[ContactLead]:
        async with api.session_factory() as session:
            return list((await session.scalars(select(ContactLead))).all())

    return asyncio.run(fetch())


class RecordingNotifier:
    """Stands in for both notifiers so the wiring is asserted without a live send."""

    def __init__(self) -> None:
        self.emails: list[dict] = []
        self.alerts: list[dict] = []

    async def send_lead_notification(self, **kwargs) -> bool:
        self.emails.append(kwargs)
        return True

    async def send_lead_alert(self, **kwargs) -> bool:
        self.alerts.append(kwargs)
        return True


class ExplodingNotifier:
    async def send_lead_notification(self, **kwargs) -> bool:
        raise RuntimeError("resend is down")

    async def send_lead_alert(self, **kwargs) -> bool:
        raise RuntimeError("bird is down")


@pytest.fixture()
def recorder(monkeypatch: pytest.MonkeyPatch) -> RecordingNotifier:
    recording = RecordingNotifier()
    monkeypatch.setattr(lead_service, "_notifier", recording)
    monkeypatch.setattr(lead_service, "_whatsapp", recording)
    return recording


def test_a_tool_lead_is_stored_with_its_source_and_metadata(api, recorder) -> None:
    response = api.client.post(ENDPOINT, json=_payload())

    assert response.status_code == 201
    assert response.json() == {"ok": True}
    [lead] = _leads(api)
    assert lead.source == "tool_mahar"
    assert lead.full_name == "Andre & Amanda"
    assert lead.email == "andre@example.com"
    assert lead.mobile == "+6281234567890"
    metadata = lead.metadata_json or {}
    assert metadata["tool"] == "mahar"
    assert metadata["source_path"] == "/wedding-tools/mahar-tanggal-pernikahan"
    assert metadata["inputs"]["amount"] == 20092026
    assert metadata["consent_at"]


def test_a_hashtag_lead_is_stored_and_labelled_as_the_hashtag_tool(api, recorder) -> None:
    response = api.client.post(
        ENDPOINT,
        json=_payload(
            tool="hashtag",
            names="Raka & Nadia",
            inputs={"tag": "#RakaNadia", "date": "2026-09-20", "events": "akad,resepsi"},
            source_path="/wedding-tools/generator-hashtag-pernikahan",
        ),
    )

    assert response.status_code == 201
    [lead] = _leads(api)
    assert lead.source == "tool_hashtag"
    assert (lead.metadata_json or {})["inputs"]["tag"] == "#RakaNadia"
    assert "Wedding tool: Hashtag" in recorder.emails[0]["subject"]
    assert recorder.alerts[0]["page"] == "Wedding tool: Hashtag"


def test_a_bazi_lead_is_stored_and_labelled_as_the_bazi_tool(api, recorder) -> None:
    response = api.client.post(
        ENDPOINT,
        json=_payload(
            tool="bazi",
            names="Raka & Nadia",
            inputs={"shio": "Tikus / Kuda", "tone": "balanced", "dates": "2026-09-20:safe"},
            source_path="/wedding-tools/kalkulator-bazi-pasangan",
        ),
    )

    assert response.status_code == 201
    [lead] = _leads(api)
    assert lead.source == "tool_bazi"
    assert (lead.metadata_json or {})["inputs"]["dates"] == "2026-09-20:safe"
    assert "Wedding tool: Ba Zi" in recorder.emails[0]["subject"]
    assert recorder.alerts[0]["page"] == "Wedding tool: Ba Zi"


def test_an_indonesian_local_number_is_stored_as_plus_62(api, recorder) -> None:
    response = api.client.post(ENDPOINT, json=_payload(phone="0812-3456-7890"))

    assert response.status_code == 201
    assert _leads(api)[0].mobile == "+6281234567890"


def test_a_filled_honeypot_answers_201_and_stores_nothing(api, recorder) -> None:
    """A bot that fills every field must not learn it was caught, so the answer
    looks like success."""
    response = api.client.post(ENDPOINT, json=_payload(website="https://spam.example"))

    assert response.status_code == 201
    assert response.json() == {"ok": True}
    assert _leads(api) == []
    assert recorder.emails == []
    assert recorder.alerts == []


def test_consent_false_is_rejected(api, recorder) -> None:
    response = api.client.post(ENDPOINT, json=_payload(consent=False))

    assert response.status_code == 422
    assert _leads(api) == []


@pytest.mark.parametrize(
    "overrides",
    [
        {"tool": "weton"},
        {"email": "not-an-email"},
        {"phone": "12345"},
        {"phone": "+62 812 3456 7890 1234 5678"},
        {"names": "x" * 121},
        {"inputs": {f"k{index}": index for index in range(21)}},
        {"inputs": {"nested": {"a": 1}}},
    ],
)
def test_invalid_payloads_are_rejected(api, recorder, overrides) -> None:
    response = api.client.post(ENDPOINT, json=_payload(**overrides))

    assert response.status_code == 422
    assert _leads(api) == []


def test_a_tool_lead_sends_the_email_and_the_whatsapp_alert(api, recorder) -> None:
    api.client.post(ENDPOINT, json=_payload())

    assert len(recorder.emails) == 1
    email = recorder.emails[0]
    assert "Wedding tool: Mahar" in email["subject"]
    assert email["reply_to"] == "andre@example.com"
    assert email["fields"]["Email"] == "andre@example.com"
    assert email["fields"]["WhatsApp"] == "+6281234567890"

    assert len(recorder.alerts) == 1
    alert = recorder.alerts[0]
    assert alert["name"] == "Andre & Amanda"
    assert alert["contact"] == "+6281234567890 / andre@example.com"
    assert alert["page"] == "Wedding tool: Mahar"
    assert "20092026" in alert["message"]


def test_failing_notifications_never_cost_the_lead(api, monkeypatch) -> None:
    """The row is committed before either send, so a provider outage must not turn
    a saved lead into a 500."""
    monkeypatch.setattr(lead_service, "_notifier", ExplodingNotifier())
    monkeypatch.setattr(lead_service, "_whatsapp", ExplodingNotifier())

    response = api.client.post(ENDPOINT, json=_payload())

    assert response.status_code == 201
    assert len(_leads(api)) == 1
