"""A month of the Chinese almanac, read for a wedding: Tanggal Baik Tionghoa.

Two things are weighed per day, the two a printed Tong Shu shows on every page
and the schools agree on how to work out:

- The day officer (建除十二神, Jian Chu): twelve names that run one a day. The
  day whose branch equals the solar month's branch is Jian, the next is Chu,
  and so on, so the officer is just the distance from the month branch to the
  day branch. Solar months turn at the jie terms, not on the 1st.
- The clash: every day opposes one of the twelve animals (the "ciong" printed
  beside the date), and a person of that shio traditionally avoids it.

What the officers mean for a wedding is where almanacs differ, so only the ends
they agree on are rated: Ding, Cheng and Kai are the days commonly picked, Po
(the day that clashes the month) and Bi are the ones commonly avoided, and the
other seven are left ordinary rather than given a verdict some school disputes.
Stars, lunar dates and the couple's full charts are not weighed here: this is
a first pass over a month, and the page says so.

The pillars and the solar terms are Ba Zi's (`app/domains/bazi`), so a date
read here and on the Ba Zi page has the same day pillar.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta, timezone
from typing import Literal

from app.domains.bazi.pillars import Pillar, day_pillar
from app.domains.bazi.relations import Rule, branch_rules
from app.domains.bazi.solar import jie_moments

Rating = Literal["good", "ordinary", "avoid"]
OfficerRating = Literal["favoured", "ordinary", "avoided"]

# Printed almanacs date the terms by Chinese standard time, and matching the
# almanac a family has on the wall matters more here than the reader's own zone:
# the two differ only when a term falls within the hour before Beijing midnight.
ALMANAC_ZONE = timezone(timedelta(hours=8))

# Indices into the cycle Jian, Chu, Man, Ping, Ding, Zhi, Po, Wei, Cheng, Shou, Kai, Bi.
FAVOURED_OFFICERS = frozenset({4, 8, 10})
AVOIDED_OFFICERS = frozenset({6, 11})


@dataclass(frozen=True)
class ShioReason:
    """How the day's branch sits with one partner's shio."""

    partner: int
    rule: Rule


@dataclass(frozen=True)
class DayReading:
    day: date
    pillar: Pillar
    month_branch: int
    officer: int
    # The branch (animal) this day opposes, whoever is asking.
    clashes: int
    reasons: list[ShioReason]
    rating: Rating


def officer_rating(officer: int) -> OfficerRating:
    if officer in FAVOURED_OFFICERS:
        return "favoured"
    return "avoided" if officer in AVOIDED_OFFICERS else "ordinary"


def _jie_days(year: int) -> list[tuple[date, int]]:
    """(almanac date, month branch) of each jie around `year`, oldest first."""
    return [
        (moment.astimezone(ALMANAC_ZONE).date(), branch)
        for around in (year - 1, year, year + 1)
        for branch, moment in jie_moments(around)
    ]


def month_branch_on(day: date) -> int:
    """The solar month a day belongs to. The day a jie falls on already counts
    as the new month, which is why the officer of the day before repeats on it."""
    return max((opened, branch) for opened, branch in _jie_days(day.year) if opened <= day)[1]


def read_day(day: date, shio: tuple[int, ...] = ()) -> DayReading:
    pillar = day_pillar(day)
    month_branch = month_branch_on(day)
    officer = (pillar.branch - month_branch) % 12
    reasons = [
        ShioReason(partner, rule)
        for partner, branch in enumerate(shio)
        for rule in branch_rules(pillar.branch, branch)
    ]
    rules = {reason.rule for reason in reasons}
    if officer in AVOIDED_OFFICERS or "clash" in rules:
        rating: Rating = "avoid"
    elif officer in FAVOURED_OFFICERS and "harm" not in rules:
        rating = "good"
    else:
        rating = "ordinary"
    return DayReading(
        day=day,
        pillar=pillar,
        month_branch=month_branch,
        officer=officer,
        clashes=(pillar.branch + 6) % 12,
        reasons=reasons,
        rating=rating,
    )


def read_month(year: int, month: int, shio: tuple[int, ...] = ()) -> list[DayReading]:
    days = calendar.monthrange(year, month)[1]
    return [read_day(date(year, month, number), shio) for number in range(1, days + 1)]
