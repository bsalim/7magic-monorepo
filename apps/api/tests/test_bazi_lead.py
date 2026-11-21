"""The Ba Zi result gate: POST /api/v1/public/bazi/leads.

The page holds the result back until the couple gives their details, then posts
them here with the calculation. Two things must hold: the lead is the same
`tool_bazi` row the shared gate writes, without the birth dates; and the couple
is emailed a copy the API rendered itself, in their language.
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.api.v1.public import bazi as bazi_router
from app.models import ContactLead
from app.services.leads import lead_service

ENDPOINT = "/api/v1/public/bazi/leads"

RAKA = {"name": "Raka", "birth_date": "1995-05-05", "birth_time": "10:00", "zone": "WIB"}
NADIA = {"name": "Nadia", "birth_date": "1996-04-14", "birth_time": "07:30", "zone": "WITA"}


def _payload(**overrides) -> dict:
    payload = {
        "tool": "bazi",
        "email": "raka@example.com",
        "phone": "+6281234567890",
        "names": "Raka & Nadia",
        "inputs": {"shio": "Babi & Tikus", "tone": "Seimbang"},
        "consent": True,
        "source_path": "/wedding-tools/kalkulator-bazi-pasangan",
        "website": "",
        "calculation": {"partners": [RAKA, NADIA], "dates": [], "locale": "id"},
    }
    payload.update(overrides)
    return payload


def _calculation(**overrides) -> dict:
    calculation = {"partners": [RAKA, NADIA], "dates": [], "locale": "id"}
    calculation.update(overrides)
    return calculation


def _leads(api) -> list[ContactLead]:
    async def fetch() -> list[ContactLead]:
        async with api.session_factory() as session:
            return list((await session.scalars(select(ContactLead))).all())

    return asyncio.run(fetch())


class QuietNotifier:
    """The team's alerts are test_tool_leads' business; here they only must not send."""

    async def send_lead_notification(self, **kwargs) -> bool:
        return True

    async def send_lead_alert(self, **kwargs) -> bool:
        return True


@pytest.fixture()
def copies(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Every copy the endpoint tried to send, in place of a live provider."""
    sent: list[dict] = []

    async def record(**kwargs) -> None:
        sent.append(kwargs)

    monkeypatch.setattr(bazi_router, "send_email", record)
    monkeypatch.setattr(lead_service, "_notifier", QuietNotifier())
    monkeypatch.setattr(lead_service, "_whatsapp", QuietNotifier())
    return sent


def test_the_lead_is_stored_without_the_birth_dates(api, copies) -> None:
    response = api.client.post(ENDPOINT, json=_payload())

    assert response.status_code == 201
    assert response.json() == {"ok": True}
    [lead] = _leads(api)
    assert lead.source == "tool_bazi"
    assert lead.email == "raka@example.com"
    stored = str(lead.metadata_json)
    assert "calculation" not in stored
    for birth in ("1995-05-05", "1996-04-14", "10:00", "07:30"):
        assert birth not in stored


def test_the_couple_is_emailed_a_copy_of_their_result(api, copies) -> None:
    api.client.post(ENDPOINT, json=_payload())

    [copy] = copies
    assert copy["to"] == ["raka@example.com"]
    assert copy["subject"] == "Hasil Ba Zi kalian dari 7Magic"
    assert copy["locale"] == "id"
    body = copy["text"]
    assert "Halo Raka & Nadia," in body
    assert "Empat pilar Raka" in body
    assert "Tahun: 乙亥 (Yǐ Hài) · Kayu, Babi" in body  # 1995 after Lichun
    assert "Shio: Babi" in body
    assert "Kesimpulan: " in body
    assert "Ba Zi adalah tradisi, bukan kepastian." in body


def test_the_copy_matches_what_the_calculator_answers(api, copies) -> None:
    """The email is rendered from the same response the page shows, so every
    finding the page lists is in the copy under the same rule name."""
    shown = api.client.post("/api/v1/public/bazi", json=_calculation()).json()
    api.client.post(ENDPOINT, json=_payload())

    body = copies[0]["text"]
    assert f"Kesimpulan: {shown['tone_label']}" in body
    assert shown["findings"]
    for finding in shown["findings"]:
        assert f"{finding['rule_label']} ({finding['a']} · {finding['b']})" in body


def test_the_copy_never_carries_a_birth_date_or_time(api, copies) -> None:
    api.client.post(ENDPOINT, json=_payload())

    body = copies[0]["text"]
    for birth in ("1995", "1996", "10:00", "10.00", "07:30", "07.30"):
        assert birth not in body


def test_checked_dates_are_in_the_copy_with_their_verdicts(api, copies) -> None:
    api.client.post(
        ENDPOINT, json=_payload(calculation=_calculation(dates=["2026-09-26", "2026-10-10"]))
    )

    body = copies[0]["text"]
    assert "Cek tanggal pernikahan" in body
    assert "Sabtu, 26 September 2026" in body
    assert "Sabtu, 10 Oktober 2026" in body
    assert body.count("Hasil: ") == 2


def test_the_copy_carries_the_card_as_markup(api, copies) -> None:
    """The page no longer offers the card as a download, so the email is where the
    couple gets it: both charts, the tone and the checked dates, above the reading."""
    api.client.post(
        ENDPOINT, json=_payload(calculation=_calculation(dates=["2026-09-26", "2026-10-10"]))
    )

    body = copies[0]["body_html"]
    assert "BA ZI PASANGAN" in body
    assert "Raka &amp; Nadia" in body
    assert "Day master 丙 Api · Shio Babi" in body
    assert "Tanggal yang dicek" in body
    assert "Sabtu, 26 September 2026" in body
    # The card comes after the intro and before the reading it illustrates.
    assert body.index("Ini kartu Ba Zi") < body.index("BA ZI PASANGAN") < body.index("Empat pilar Raka")
    for birth in ("1995", "1996", "10:00", "07:30"):
        assert birth not in body


def test_an_unknown_hour_keeps_its_column_on_the_card(api, copies) -> None:
    partners = [RAKA, {**NADIA, "birth_time": None}]
    api.client.post(ENDPOINT, json=_payload(calculation=_calculation(partners=partners)))

    body = copies[0]["body_html"]
    assert body.count('<td width="25%"') == 8
    assert "&ndash;" in body


def test_a_name_cannot_put_markup_into_the_card(api, copies) -> None:
    partners = [{**RAKA, "name": "<img src=x onerror=alert(1)>"}, NADIA]
    api.client.post(ENDPOINT, json=_payload(calculation=_calculation(partners=partners)))

    body = copies[0]["body_html"]
    assert "<img" not in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body


def test_no_dates_means_no_date_section(api, copies) -> None:
    api.client.post(ENDPOINT, json=_payload())

    assert "Cek tanggal pernikahan" not in copies[0]["text"]
    assert "Tanggal yang dicek" not in copies[0]["body_html"]


def test_an_english_calculation_gets_an_english_copy(api, copies) -> None:
    api.client.post(
        ENDPOINT,
        json=_payload(calculation=_calculation(locale="en", dates=["2026-09-26"])),
    )

    [copy] = copies
    assert copy["subject"] == "Your Ba Zi result from 7Magic"
    assert copy["locale"] == "en"
    body = copy["text"]
    assert "Hi Raka & Nadia," in body
    assert "Raka's four pillars" in body
    assert "Zodiac sign: Pig" in body
    assert "Saturday, 26 September 2026" in body
    assert "Kesimpulan" not in body
    # The card and the shell around it follow the same language as the reading.
    card = copy["body_html"]
    assert "COUPLE BA ZI" in card
    assert "Dates checked" in card
    assert "Day master 丙 Fire · Zodiac sign Pig" in card
    for indonesian in ("BA ZI PASANGAN", "Tanggal yang dicek", "Shio", "Aman", "Bentrok", "Kayu", "Logam"):
        assert indonesian not in card


def test_blank_names_fall_back_to_neutral_labels(api, copies) -> None:
    partners = [{**RAKA, "name": None}, {**NADIA, "name": "  "}]
    api.client.post(ENDPOINT, json=_payload(calculation=_calculation(partners=partners)))

    body = copies[0]["text"]
    assert body.startswith("Halo,\n\n")
    assert "Empat pilar Pengantin 1" in body
    assert "Empat pilar Pengantin 2" in body


def test_a_name_cannot_forge_a_line_of_its_own(api, copies) -> None:
    """The name is typed by a stranger and the email may reach someone else, so
    a newline in it must not start a row the layout would style as a real one."""
    partners = [{**RAKA, "name": "Raka\nHasil: Menang undian"}, NADIA]
    api.client.post(ENDPOINT, json=_payload(calculation=_calculation(partners=partners)))

    body = copies[0]["text"]
    assert "\nHasil: Menang undian" not in body
    assert "Raka Hasil: Menang undian" in body


def test_a_filled_honeypot_stores_and_sends_nothing(api, copies) -> None:
    response = api.client.post(ENDPOINT, json=_payload(website="https://spam.example"))

    assert response.status_code == 201
    assert response.json() == {"ok": True}
    assert _leads(api) == []
    assert copies == []


def test_a_failed_send_never_costs_the_lead_or_the_result(api, monkeypatch) -> None:
    """The page reveals the result on a 201, so a provider outage must not turn a
    saved lead into an error the couple cannot get past."""

    async def explode(**kwargs) -> None:
        raise RuntimeError("resend is down")

    monkeypatch.setattr(bazi_router, "send_email", explode)
    monkeypatch.setattr(lead_service, "_notifier", QuietNotifier())
    monkeypatch.setattr(lead_service, "_whatsapp", QuietNotifier())

    response = api.client.post(ENDPOINT, json=_payload())

    assert response.status_code == 201
    assert len(_leads(api)) == 1


@pytest.mark.parametrize(
    "overrides",
    [
        {"calculation": None},
        {"calculation": _calculation(partners=[RAKA])},
        {"calculation": _calculation(partners=[RAKA, {**NADIA, "birth_date": "1899-12-31"}])},
        {"calculation": _calculation(locale="fr")},
        {"tool": "mahar"},
        {"email": "not-an-email"},
        {"consent": False},
    ],
    ids=[
        "no-calculation",
        "one-partner",
        "year-1899",
        "bad-locale",
        "another-tool",
        "bad-email",
        "no-consent",
    ],
)
def test_invalid_payloads_store_and_send_nothing(api, copies, overrides) -> None:
    response = api.client.post(ENDPOINT, json=_payload(**overrides))

    assert response.status_code == 422
    assert _leads(api) == []
    assert copies == []
