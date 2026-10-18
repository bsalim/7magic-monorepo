"""POST /api/v1/public/bazi: two birth moments in, two charts and a reading out.

The endpoint is a calculator, not a form: nothing it receives is stored, which
the last test pins, because birth dates are personal data and the lead gate is
the only path by which anything from this tool reaches the database.
"""

from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import func, select

from app.models import ContactLead

ENDPOINT = "/api/v1/public/bazi"

RAKA = {"name": "Raka", "birth_date": "1995-05-05", "birth_time": "10:00", "zone": "WIB"}
NADIA = {"name": "Nadia", "birth_date": "1996-08-17", "birth_time": None, "zone": "WITA"}


def _body(**overrides) -> dict:
    body = {"partners": [RAKA, NADIA], "dates": [], "locale": "id"}
    body.update(overrides)
    return body


def test_two_partners_get_two_charts_and_a_tone(api) -> None:
    response = api.client.post(ENDPOINT, json=_body())

    assert response.status_code == 200
    data = response.json()
    assert len(data["charts"]) == 2
    assert data["tone"] in {"harmony", "balanced", "clash"}
    assert data["tone_label"]
    raka = data["charts"][0]
    assert raka["name"] == "Raka"
    assert raka["day_master"]["element_label"] in {"Kayu", "Api", "Tanah", "Logam", "Air"}
    assert raka["shio"]["animal"] == "pig"  # 1995 after Lichun is 乙亥
    assert raka["shio"]["animal_label"] == "Babi"
    assert sum(raka["elements"].values()) == 8
    assert set(raka["elements"]) == {"wood", "fire", "earth", "metal", "water"}
    assert raka["year"]["stem"]["char"] == "乙" and raka["year"]["branch"]["char"] == "亥"
    assert all(f["rule_label"] and f["kind"] for f in data["findings"])


def test_labels_follow_the_locale(api) -> None:
    indonesian = api.client.post(ENDPOINT, json=_body()).json()
    english = api.client.post(ENDPOINT, json=_body(locale="en")).json()

    assert indonesian["charts"][0]["shio"]["animal_label"] == "Babi"
    assert english["charts"][0]["shio"]["animal_label"] == "Pig"
    assert english["charts"][0]["day_master"]["element_label"] in {"Wood", "Fire", "Earth", "Metal", "Water"}
    assert indonesian["tone"] == english["tone"]


def test_a_missing_time_returns_no_hour_pillar(api) -> None:
    nadia = api.client.post(ENDPOINT, json=_body()).json()["charts"][1]

    assert nadia["hour"] is None
    assert sum(nadia["elements"].values()) == 6


def test_a_lichun_day_without_time_is_flagged(api) -> None:
    body = _body(partners=[RAKA, {**NADIA, "birth_date": "2026-02-04", "zone": "WIB"}])
    chart = api.client.post(ENDPOINT, json=body).json()["charts"][1]

    assert chart["year"]["depends_on_time"] is True
    assert chart["month"]["depends_on_time"] is True


def test_dates_come_back_checked_in_order(api) -> None:
    data = api.client.post(ENDPOINT, json=_body(dates=["2026-10-10", "2026-09-20"])).json()

    assert [check["date"] for check in data["date_checks"]] == ["2026-10-10", "2026-09-20"]
    for check in data["date_checks"]:
        assert check["verdict"] in {"safe", "consider", "clash"}
        assert check["pillar"]["branch"]["animal_label"]
        for reason in check["reasons"]:
            assert reason["partner"] in (0, 1) and reason["against"] in ("shio", "day")
            assert reason["rule_label"]


def test_no_dates_means_no_date_checks(api) -> None:
    assert api.client.post(ENDPOINT, json=_body()).json()["date_checks"] == []


@pytest.mark.parametrize(
    "body",
    [
        _body(partners=[RAKA]),
        _body(partners=[RAKA, NADIA, RAKA]),
        _body(dates=["2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23"]),
        _body(partners=[RAKA, {**NADIA, "birth_date": "2026-02-30"}]),
        _body(partners=[RAKA, {**NADIA, "birth_date": "1899-12-31"}]),
        _body(partners=[RAKA, {**NADIA, "birth_date": "2101-01-01"}]),
        _body(dates=["2101-01-01"]),
        _body(partners=[RAKA, {**NADIA, "zone": "UTC"}]),
        _body(locale="fr"),
    ],
    ids=[
        "one-partner",
        "three-partners",
        "four-dates",
        "feb-30",
        "year-1899",
        "year-2101",
        "date-2101",
        "bad-zone",
        "bad-locale",
    ],
)
def test_bad_input_is_a_422(api, body) -> None:
    assert api.client.post(ENDPOINT, json=body).status_code == 422


def test_nothing_is_stored(api) -> None:
    async def count() -> int:
        async with api.session_factory() as session:
            return await session.scalar(select(func.count()).select_from(ContactLead)) or 0

    before = asyncio.run(count())
    api.client.post(ENDPOINT, json=_body(dates=["2026-09-20"]))
    assert asyncio.run(count()) == before
