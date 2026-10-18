"""Print independent reference values for the Ba Zi engine's tests.

The engine in `app/domains/bazi/` is written from scratch, so its tests compare
it against two outside implementations instead of against itself:

- `solar`: the 12 jie solar-term moments per year, found with Skyfield on the
  JPL DE421 ephemeris (apparent longitude on the ecliptic of date). DE421 is
  downloaded by Skyfield on first run into ~/.cache/skyfield, outside the repo.
- `charts`: four-pillar charts from lunar-python (6tail), whose solar terms come
  from its own almanac code, not from ours.

Run once by hand and paste the output into the test files; it is not part of
the app. Skyfield and lunar-python are dev-only dependencies and nothing under
`app/` may import them.

    uv run python scripts/bazi_reference.py solar
    uv run python scripts/bazi_reference.py charts
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

SOLAR_YEARS = (1900, 1930, 1960, 1975, 1988, 1990, 2000, 2026, 2049)

STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"

# Local birth moments as (date-time, UTC offset in hours). Chosen where cheap
# calculators go wrong: either side of Lichun and of a month term, the turn of
# the year, and either side of 23:00.
CHARTS = (
    ("1984-02-04 21:48", 7),
    ("1984-02-04 22:49", 7),
    ("1990-03-06 02:49", 7),
    ("1990-03-06 03:50", 7),
    ("1995-12-31 23:59", 7),
    ("1996-01-01 00:30", 7),
    ("1990-06-15 22:59", 7),
    ("1990-06-15 23:00", 7),
    ("2000-01-01 12:00", 7),
    ("1988-08-08 08:08", 8),
    ("2001-11-22 05:45", 9),
    ("1975-07-20 16:10", 8),
)


def solar() -> None:
    from skyfield.api import Loader
    from skyfield.framelib import ecliptic_frame
    from skyfield.searchlib import find_discrete

    load = Loader(Path.home() / ".cache" / "skyfield")
    ts = load.timescale()
    eph = load("de421.bsp")
    earth, sun = eph["earth"], eph["sun"]

    def segment(t):
        _, lon, _ = earth.at(t).observe(sun).apparent().frame_latlon(ecliptic_frame)
        return ((lon.degrees - 15) // 30).astype(int) % 12

    segment.step_days = 5

    print("SKYFIELD_REFERENCE = [")
    for year in SOLAR_YEARS:
        times, values = find_discrete(ts.utc(year, 1, 1), ts.utc(year + 1, 1, 1), segment)
        for t, value in zip(times, values, strict=True):
            longitude = (int(value) * 30 + 15) % 360
            moment = t.utc_datetime().replace(microsecond=0)
            print(f"    ({year}, {longitude}, datetime({moment:%Y, %-m, %-d, %-H, %-M, %-S}, tzinfo=UTC)),")
    print("]")


def charts() -> None:
    from lunar_python import Solar

    print("REFERENCE_CHARTS = [")
    for stamp, offset in CHARTS:
        local = datetime.strptime(stamp, "%Y-%m-%d %H:%M").replace(tzinfo=timezone(timedelta(hours=offset)))
        # lunar-python reads Beijing time (UTC+8) for its solar terms, but its day
        # and hour pillars follow whatever clock it is given. So the year and
        # month come from the same instant in Beijing time, and the day and hour
        # from the local clock, which is the convention the tool uses.
        beijing = local.astimezone(timezone(timedelta(hours=8)))
        absolute = Solar.fromYmdHms(
            beijing.year, beijing.month, beijing.day, beijing.hour, beijing.minute, 0
        ).getLunar().getEightChar()
        clock = Solar.fromYmdHms(
            local.year, local.month, local.day, local.hour, local.minute, 0
        ).getLunar().getEightChar()
        # Sect 1: from 23:00 the day pillar is already the next day's.
        clock.setSect(1)
        pillars = [absolute.getYear(), absolute.getMonth(), clock.getDay(), clock.getTime()]
        indices = [(STEMS.index(p[0]), BRANCHES.index(p[1])) for p in pillars]
        zone = {7: "WIB", 8: "WITA", 9: "WIT"}[offset]
        print(
            f"    (date({local:%Y, %-m, %-d}), time({local:%-H, %-M}), {zone!r}, {indices}),"
            f"  # {' '.join(pillars)}"
        )
    print("]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("what", choices=("solar", "charts"))
    {"solar": solar, "charts": charts}[parser.parse_args().what]()
