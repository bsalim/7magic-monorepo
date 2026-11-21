"""Tanggal Baik Tionghoa: the almanac month, and POST /api/v1/public/almanac.

The day officers are pinned against a published almanac rather than against the
formula that produces them: June 2025's Bi days and the animal 5 June opposes
are as the printed calendars give them, including the officer repeating on the
day the Mangzhong term opens the Wu month.
"""

from __future__ import annotations

from datetime import date

import pytest

from app.domains.almanac.service import month_branch_on, read_day, read_month
from app.domains.bazi.labels import ANIMALS

ENDPOINT = "/api/v1/public/almanac"

BI, PO, DING, CHENG, KAI = 11, 6, 4, 8, 10
RAT, OX, GOAT, HORSE, PIG = (ANIMALS.index(a) for a in ("rat", "ox", "goat", "horse", "pig"))


def test_june_2025_has_its_bi_days_where_the_almanac_prints_them() -> None:
    bi_days = [reading.day.day for reading in read_month(2025, 6) if reading.officer == BI]

    assert bi_days == [4, 5, 17, 29]


def test_the_officer_repeats_on_the_day_a_term_opens_the_month() -> None:
    """Mangzhong fell on 5 June 2025: the 4th closes the Si month and the 5th
    opens Wu, and both are Bi, which is how twelve officers stay in step with
    twelve branches."""
    assert month_branch_on(date(2025, 6, 4)) == 5
    assert month_branch_on(date(2025, 6, 5)) == 6
    assert read_day(date(2025, 6, 4)).officer == read_day(date(2025, 6, 5)).officer == BI
    assert read_day(date(2025, 6, 6)).officer == 0


def test_a_day_opposes_the_animal_across_the_cycle_from_it() -> None:
    # 5 June 2025 is a Si (Snake) day; the almanac prints "clash Pig" beside it.
    assert read_day(date(2025, 6, 5)).clashes == PIG


def test_january_belongs_to_the_solar_month_that_began_the_year_before() -> None:
    # Xiaohan opens the Chou month around 5 January; the days before it are Zi.
    assert month_branch_on(date(2027, 1, 2)) == 0
    assert month_branch_on(date(2027, 1, 20)) == 1


def test_the_po_day_is_the_one_that_clashes_the_month() -> None:
    for reading in read_month(2027, 3):
        assert (reading.officer == PO) == ((reading.pillar.branch - reading.month_branch) % 12 == 6)


def test_only_the_officers_almanacs_agree_on_are_rated() -> None:
    ratings = {reading.officer: reading.rating for reading in read_month(2027, 3)}

    assert {officer for officer, rating in ratings.items() if rating == "good"} == {
        DING,
        CHENG,
        KAI,
    }
    assert {officer for officer, rating in ratings.items() if rating == "avoid"} == {PO, BI}


def test_a_favoured_day_that_clashes_a_partner_is_avoided() -> None:
    # 8 May 2025: a Cheng day, on the Ox branch, which opposes the Goat.
    day = date(2025, 5, 8)
    assert read_day(day).officer == CHENG
    assert read_day(day).rating == "good"

    reading = read_day(day, (RAT, GOAT))

    assert reading.rating == "avoid"
    assert [
        (reason.partner, reason.rule) for reason in reading.reasons if reason.rule == "clash"
    ] == [(1, "clash")]


def test_a_favoured_day_that_harms_a_partner_is_only_ordinary() -> None:
    # Ox and Horse harm each other (Liu Hai), which is a caution, not a clash.
    reading = read_day(date(2025, 5, 8), (HORSE, PIG))

    assert "harm" in {reason.rule for reason in reading.reasons}
    assert reading.rating == "ordinary"


def test_harmony_with_a_shio_is_noted_but_does_not_lift_an_ordinary_day() -> None:
    # 7 May 2025 is a Rat day under Wei, an officer left unrated; Rat and Ox combine.
    reading = read_day(date(2025, 5, 7), (OX, PIG))

    assert "six_combination" in {reason.rule for reason in reading.reasons}
    assert reading.rating == "ordinary"


def test_the_endpoint_answers_a_whole_month_labelled_in_indonesian(api) -> None:
    response = api.client.post(
        ENDPOINT, json={"year": 2025, "month": 6, "shio": ["pig", "rat"], "locale": "id"}
    )

    assert response.status_code == 200
    body = response.json()
    assert (body["year"], body["month"]) == (2025, 6)
    assert [shio["animal_label"] for shio in body["shio"]] == ["Babi", "Tikus"]
    assert len(body["days"]) == 30
    fifth = body["days"][4]
    assert fifth["date"] == "2025-06-05"
    assert fifth["pillar"]["stem"]["char"] + fifth["pillar"]["branch"]["char"] == "乙巳"
    assert fifth["officer"] == {
        "index": 11,
        "char": "闭",
        "pinyin": "Bì",
        "label": "Tutup",
        "rating": "avoided",
    }
    assert fifth["clashes"]["animal_label"] == "Babi"
    assert fifth["rating"] == "avoid"
    assert {"partner": 0, "rule": "clash", "rule_label": "Benturan (Chong)"} in fifth["reasons"]


def test_the_endpoint_answers_in_english_and_without_any_shio(api) -> None:
    response = api.client.post(ENDPOINT, json={"year": 2025, "month": 5, "locale": "en"})

    assert response.status_code == 200
    body = response.json()
    assert body["shio"] == []
    eighth = body["days"][7]
    assert eighth["officer"]["label"] == "Success"
    assert eighth["clashes"]["animal_label"] == "Goat"
    assert eighth["reasons"] == []
    assert eighth["rating"] == "good"


@pytest.mark.parametrize(
    "body",
    [
        {"year": 2027},
        {"year": 2027, "month": 13},
        {"year": 2027, "month": 0},
        {"year": 1899, "month": 5},
        {"year": 2101, "month": 5},
        {"year": 2027, "month": 5, "shio": ["cat"]},
        {"year": 2027, "month": 5, "shio": ["rat", "ox", "pig"]},
        {"year": 2027, "month": 5, "locale": "fr"},
    ],
    ids=[
        "no-month",
        "month-13",
        "month-0",
        "year-1899",
        "year-2101",
        "no-such-shio",
        "three-shio",
        "bad-locale",
    ],
)
def test_the_endpoint_refuses_what_it_cannot_read(api, body) -> None:
    assert api.client.post(ENDPOINT, json=body).status_code == 422
