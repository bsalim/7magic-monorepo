"""The four pillars, checked against lunar-python and the classical anchors.

A chart is wrong in the places a visitor checks first: either side of Lichun or
a month term, at the turn of the calendar year, and around 23:00, when the day
pillar moves on. The reference charts cover each of those.
"""

from __future__ import annotations

from datetime import date, time, timedelta, timezone

import pytest

from app.domains.bazi.pillars import chart_for, cycle_pillar, day_pillar
from app.domains.bazi.solar import term_moment

# lunar-python 1.4.8 (6tail), written by `scripts/bazi_reference.py charts`:
# year and month from the absolute instant, day and hour from the local clock,
# sect 1 (23:00 starts the next day). Pairs are (stem, branch) indices.
REFERENCE_CHARTS = [
    (date(1984, 2, 4), time(21, 48), 'WIB', [(9, 11), (1, 1), (4, 4), (9, 11)]),  # 癸亥 乙丑 戊辰 癸亥
    (date(1984, 2, 4), time(22, 49), 'WIB', [(0, 0), (2, 2), (4, 4), (9, 11)]),  # 甲子 丙寅 戊辰 癸亥
    (date(1990, 3, 6), time(2, 49), 'WIB', [(6, 6), (4, 2), (6, 6), (3, 1)]),  # 庚午 戊寅 庚午 丁丑
    (date(1990, 3, 6), time(3, 50), 'WIB', [(6, 6), (5, 3), (6, 6), (4, 2)]),  # 庚午 己卯 庚午 戊寅
    (date(1995, 12, 31), time(23, 59), 'WIB', [(1, 11), (4, 0), (3, 9), (6, 0)]),  # 乙亥 戊子 丁酉 庚子
    (date(1996, 1, 1), time(0, 30), 'WIB', [(1, 11), (4, 0), (3, 9), (6, 0)]),  # 乙亥 戊子 丁酉 庚子
    (date(1990, 6, 15), time(22, 59), 'WIB', [(6, 6), (8, 6), (7, 11), (5, 11)]),  # 庚午 壬午 辛亥 己亥
    (date(1990, 6, 15), time(23, 0), 'WIB', [(6, 6), (8, 6), (8, 0), (6, 0)]),  # 庚午 壬午 壬子 庚子
    (date(2000, 1, 1), time(12, 0), 'WIB', [(5, 3), (2, 0), (4, 6), (4, 6)]),  # 己卯 丙子 戊午 戊午
    (date(1988, 8, 8), time(8, 8), 'WITA', [(4, 4), (6, 8), (1, 7), (6, 4)]),  # 戊辰 庚申 乙未 庚辰
    (date(2001, 11, 22), time(5, 45), 'WIT', [(7, 5), (5, 11), (5, 1), (3, 3)]),  # 辛巳 己亥 己丑 丁卯
    (date(1975, 7, 20), time(16, 10), 'WITA', [(1, 3), (9, 7), (3, 3), (4, 8)]),  # 乙卯 癸未 丁卯 戊申
]


def test_day_cycle_anchors() -> None:
    assert day_pillar(date(2000, 1, 1)).index == 54  # 戊午
    assert day_pillar(date(1949, 10, 1)).index == 0  # 甲子


def test_cycle_pillar_round_trips() -> None:
    for index in range(60):
        pillar = cycle_pillar(index)
        assert pillar.index == index
        assert pillar.stem == index % 10 and pillar.branch == index % 12


def test_1984_after_lichun_is_jia_zi_year() -> None:
    chart = chart_for(date(1984, 3, 10), time(12), "WIB")
    assert (chart.year.stem, chart.year.branch) == (0, 0)


def test_five_tigers_and_five_rats() -> None:
    chart = chart_for(date(1984, 3, 10), time(0, 30), "WIB")  # Jia year, Mao month (after Jingzhe)
    assert (chart.month.stem, chart.month.branch) == (3, 3)  # 丁卯
    assert chart.hour is not None
    assert chart.hour.branch == 0 and chart.hour.stem == (2 * (chart.day.stem % 5)) % 10


@pytest.mark.parametrize(("birth_date", "birth_time", "zone", "expected"), REFERENCE_CHARTS)
def test_charts_match_the_reference(birth_date, birth_time, zone, expected) -> None:
    chart = chart_for(birth_date, birth_time, zone)
    assert [(p.stem, p.branch) for p in (chart.year, chart.month, chart.day, chart.hour)] == expected


def test_23_00_starts_the_next_day() -> None:
    late = chart_for(date(1990, 6, 15), time(23, 30), "WIB")
    assert late.day.index == day_pillar(date(1990, 6, 16)).index
    assert late.hour is not None
    assert late.hour.branch == 0
    assert late.hour.stem == (2 * (late.day.stem % 5)) % 10


def test_lichun_day_without_time_is_flagged_not_guessed() -> None:
    chart = chart_for(date(2026, 2, 4), None, "WIB")
    assert chart.hour is None
    assert chart.year.depends_on_time and chart.month.depends_on_time


def test_a_month_term_day_without_time_flags_only_the_month() -> None:
    jingzhe = term_moment(2026, 345).astimezone(timezone(timedelta(hours=7)))
    chart = chart_for(jingzhe.date(), None, "WIB")
    assert chart.month.depends_on_time and not chart.year.depends_on_time


def test_an_ordinary_day_without_time_has_no_flags() -> None:
    chart = chart_for(date(2026, 3, 1), None, "WIB")
    assert not chart.year.depends_on_time and not chart.month.depends_on_time
    assert not chart.year.near_term and not chart.month.near_term


def test_a_birth_near_a_term_is_flagged() -> None:
    lichun = term_moment(2026, 315).astimezone(timezone(timedelta(hours=7)))
    after = lichun + timedelta(minutes=10)
    chart = chart_for(after.date(), after.time(), "WIB")
    assert chart.month.near_term and chart.year.near_term
    assert (chart.year.stem, chart.year.branch) == (2, 6)  # 丙午, the new year


def test_a_birth_just_before_a_term_is_flagged_too() -> None:
    lichun = term_moment(2026, 315).astimezone(timezone(timedelta(hours=7)))
    before = lichun - timedelta(minutes=10)
    chart = chart_for(before.date(), before.time(), "WIB")
    assert chart.month.near_term and chart.year.near_term
    assert (chart.year.stem, chart.year.branch) == (1, 5)  # 乙巳, still the old year


def test_the_zone_moves_the_term_but_not_the_clock() -> None:
    # Lichun 2026 is 03:02 WIB, which is 04:02 WITA. A 03:30 WITA birth is
    # 02:30 WIB, still before Lichun; a 03:30 WIB birth is after it.
    assert chart_for(date(2026, 2, 4), time(3, 30), "WITA").year.branch == 5
    assert chart_for(date(2026, 2, 4), time(3, 30), "WIB").year.branch == 6


def test_element_counts_cover_present_pillars_only() -> None:
    assert sum(chart_for(date(2026, 3, 1), None, "WIB").element_counts) == 6
    assert sum(chart_for(date(2026, 3, 1), time(9), "WIB").element_counts) == 8


def test_day_master_and_shio() -> None:
    chart = chart_for(date(2000, 1, 1), time(12), "WIB")
    assert chart.day_master == 4  # 戊
    assert chart.shio == 3  # 卯, Rabbit: 1 Jan 2000 is before Lichun
