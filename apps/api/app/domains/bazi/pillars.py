"""The four pillars of a birth moment, and the flags that say how sure they are.

Indices throughout: stems 0-9 are Jia..Gui, branches 0-11 are Zi (Rat)..Hai
(Pig), elements 0-4 are wood, fire, earth, metal, water. A stem's element is
`stem // 2` and it is yang when even.

Conventions the page states to the visitor (see the design doc): the clock time
in the zone the birth certificate used, with no true-solar-time correction, and
23:00 starting the next day's pillar.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, time, timedelta, timezone
from typing import Literal

from app.domains.bazi.solar import jie_moments, term_moment

Zone = Literal["WIB", "WITA", "WIT"]
ZONE_OFFSETS: dict[Zone, int] = {"WIB": 7, "WITA": 8, "WIT": 9}

BRANCH_ELEMENTS = (4, 2, 0, 0, 2, 1, 1, 2, 3, 3, 2, 4)

LICHUN_BRANCH = 2
# Birth certificates round the time, so a pillar decided by a term this close
# is shown with a caveat rather than as certain.
NEAR_TERM = timedelta(minutes=30)
# With no birth time, the chart is read at noon: the middle of the day keeps
# every pillar but the one a term on that date can change.
NO_TIME = time(12)


@dataclass(frozen=True)
class Pillar:
    stem: int
    branch: int
    depends_on_time: bool = False
    near_term: bool = False

    @property
    def index(self) -> int:
        """Position in the sexagenary cycle, Jia-Zi = 0."""
        return (6 * self.stem - 5 * self.branch) % 60


@dataclass(frozen=True)
class Chart:
    year: Pillar
    month: Pillar
    day: Pillar
    hour: Pillar | None

    @property
    def day_master(self) -> int:
        return self.day.stem

    @property
    def shio(self) -> int:
        return self.year.branch

    @property
    def element_counts(self) -> tuple[int, int, int, int, int]:
        counts = [0] * 5
        for pillar in (self.year, self.month, self.day, self.hour):
            if pillar is None:
                continue
            counts[pillar.stem // 2] += 1
            counts[BRANCH_ELEMENTS[pillar.branch]] += 1
        return (counts[0], counts[1], counts[2], counts[3], counts[4])


def cycle_pillar(index: int) -> Pillar:
    return Pillar(stem=index % 10, branch=index % 12)


def day_pillar(day: date) -> Pillar:
    # The 60-day count has run unbroken for millennia; the offset puts Jia-Zi
    # on 1949-10-01 and Wu-Wu on 2000-01-01, the usual published anchors.
    julian_day_number = day.toordinal() + 1721425
    return cycle_pillar((julian_day_number + 49) % 60)


def _month_stem(year_stem: int, month_branch: int) -> int:
    # Five Tigers: the year stem fixes the stem of the Yin month, and the stems
    # then run on one per month.
    yin_month_stem = (2 * (year_stem % 5) + 2) % 10
    return (yin_month_stem + (month_branch - 2) % 12) % 10


def _hour_pillar(day_stem: int, hour: int) -> Pillar:
    branch = ((hour + 1) // 2) % 12
    # Five Rats: the day stem fixes the stem of the Zi hour.
    return Pillar(stem=(2 * (day_stem % 5) + branch) % 10, branch=branch)


def chart_for(birth_date: date, birth_time: time | None, zone: Zone) -> Chart:
    local_zone = timezone(timedelta(hours=ZONE_OFFSETS[zone]))
    local = datetime.combine(birth_date, birth_time or NO_TIME, local_zone)
    instant = local.astimezone(UTC)

    year = birth_date.year
    if instant < term_moment(year, 315):
        year -= 1
    year_pillar = Pillar(stem=(year - 4) % 10, branch=(year - 4) % 12)

    # The last jie at or before the birth decides the month; the previous
    # year's December terms cover a birth in early January.
    terms = jie_moments(birth_date.year - 1) + jie_moments(birth_date.year) + jie_moments(birth_date.year + 1)
    position = max(i for i, (_, moment) in enumerate(terms) if moment <= instant)
    month_branch, decided_at = terms[position]
    month_pillar = Pillar(stem=_month_stem(year_pillar.stem, month_branch), branch=month_branch)

    if birth_time is None:
        on_the_day = [branch for branch, moment in terms if moment.astimezone(local_zone).date() == birth_date]
        if on_the_day:
            month_pillar = replace(month_pillar, depends_on_time=True)
            if LICHUN_BRANCH in on_the_day:
                year_pillar = replace(year_pillar, depends_on_time=True)
    else:
        next_branch, next_at = terms[position + 1]
        near = []
        if instant - decided_at <= NEAR_TERM:
            near.append(month_branch)
        if next_at - instant <= NEAR_TERM:
            near.append(next_branch)
        if near:
            month_pillar = replace(month_pillar, near_term=True)
            if LICHUN_BRANCH in near:
                year_pillar = replace(year_pillar, near_term=True)

    pillar_date = birth_date
    if birth_time is not None and birth_time.hour >= 23:
        pillar_date += timedelta(days=1)
    day = day_pillar(pillar_date)

    hour = _hour_pillar(day.stem, birth_time.hour) if birth_time is not None else None
    return Chart(year=year_pillar, month=month_pillar, day=day, hour=hour)
