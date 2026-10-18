"""Solar-term moments for the Ba Zi engine, checked against outside references.

The year pillar turns at Lichun and each month pillar at a jie term, so a term
moment that is off by a few minutes gives a wrong chart for anyone born in that
window. The engine is our own code; these references are not.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.domains.bazi.solar import delta_t_seconds, jie_moments, solar_longitude, term_moment

# Skyfield 1.55 with the JPL DE421 ephemeris, apparent longitude on the ecliptic
# of date, written by `scripts/bazi_reference.py solar`.
SKYFIELD_REFERENCE = [
    (1900, 285, datetime(1900, 1, 5, 18, 3, 12, tzinfo=UTC)),
    (1900, 315, datetime(1900, 2, 4, 5, 50, 45, tzinfo=UTC)),
    (1900, 345, datetime(1900, 3, 6, 0, 21, 6, tzinfo=UTC)),
    (1900, 15, datetime(1900, 4, 5, 5, 51, 55, tzinfo=UTC)),
    (1900, 45, datetime(1900, 5, 5, 23, 54, 27, tzinfo=UTC)),
    (1900, 75, datetime(1900, 6, 6, 4, 38, 11, tzinfo=UTC)),
    (1900, 105, datetime(1900, 7, 7, 15, 9, 25, tzinfo=UTC)),
    (1900, 135, datetime(1900, 8, 8, 0, 49, 50, tzinfo=UTC)),
    (1900, 165, datetime(1900, 9, 8, 3, 15, 53, tzinfo=UTC)),
    (1900, 195, datetime(1900, 10, 8, 18, 12, 24, tzinfo=UTC)),
    (1900, 225, datetime(1900, 11, 7, 20, 38, 59, tzinfo=UTC)),
    (1900, 255, datetime(1900, 12, 7, 12, 55, 6, tzinfo=UTC)),
    (1930, 285, datetime(1930, 1, 6, 1, 2, 14, tzinfo=UTC)),
    (1930, 315, datetime(1930, 2, 4, 12, 50, 49, tzinfo=UTC)),
    (1930, 345, datetime(1930, 3, 6, 7, 16, 15, tzinfo=UTC)),
    (1930, 15, datetime(1930, 4, 5, 12, 37, 4, tzinfo=UTC)),
    (1930, 45, datetime(1930, 5, 6, 6, 26, 41, tzinfo=UTC)),
    (1930, 75, datetime(1930, 6, 6, 10, 57, 44, tzinfo=UTC)),
    (1930, 105, datetime(1930, 7, 7, 21, 19, 21, tzinfo=UTC)),
    (1930, 135, datetime(1930, 8, 8, 6, 56, 39, tzinfo=UTC)),
    (1930, 165, datetime(1930, 9, 8, 9, 28, 4, tzinfo=UTC)),
    (1930, 195, datetime(1930, 10, 9, 0, 37, 9, tzinfo=UTC)),
    (1930, 225, datetime(1930, 11, 8, 3, 19, 52, tzinfo=UTC)),
    (1930, 255, datetime(1930, 12, 7, 19, 50, 18, tzinfo=UTC)),
    (1960, 285, datetime(1960, 1, 6, 7, 42, 17, tzinfo=UTC)),
    (1960, 315, datetime(1960, 2, 4, 19, 22, 58, tzinfo=UTC)),
    (1960, 345, datetime(1960, 3, 5, 13, 35, 56, tzinfo=UTC)),
    (1960, 15, datetime(1960, 4, 4, 18, 43, 23, tzinfo=UTC)),
    (1960, 45, datetime(1960, 5, 5, 12, 22, 24, tzinfo=UTC)),
    (1960, 75, datetime(1960, 6, 5, 16, 48, 24, tzinfo=UTC)),
    (1960, 105, datetime(1960, 7, 7, 3, 12, 29, tzinfo=UTC)),
    (1960, 135, datetime(1960, 8, 7, 12, 59, 35, tzinfo=UTC)),
    (1960, 165, datetime(1960, 9, 7, 15, 45, 13, tzinfo=UTC)),
    (1960, 195, datetime(1960, 10, 8, 7, 8, 30, tzinfo=UTC)),
    (1960, 225, datetime(1960, 11, 7, 10, 1, 52, tzinfo=UTC)),
    (1960, 255, datetime(1960, 12, 7, 2, 37, 35, tzinfo=UTC)),
    (1975, 285, datetime(1975, 1, 5, 23, 17, 29, tzinfo=UTC)),
    (1975, 315, datetime(1975, 2, 4, 10, 59, 10, tzinfo=UTC)),
    (1975, 345, datetime(1975, 3, 6, 5, 5, 45, tzinfo=UTC)),
    (1975, 15, datetime(1975, 4, 5, 10, 1, 28, tzinfo=UTC)),
    (1975, 45, datetime(1975, 5, 6, 3, 27, 10, tzinfo=UTC)),
    (1975, 75, datetime(1975, 6, 6, 7, 42, 0, tzinfo=UTC)),
    (1975, 105, datetime(1975, 7, 7, 17, 59, 23, tzinfo=UTC)),
    (1975, 135, datetime(1975, 8, 8, 3, 44, 52, tzinfo=UTC)),
    (1975, 165, datetime(1975, 9, 8, 6, 33, 16, tzinfo=UTC)),
    (1975, 195, datetime(1975, 10, 8, 22, 2, 2, tzinfo=UTC)),
    (1975, 225, datetime(1975, 11, 8, 1, 2, 36, tzinfo=UTC)),
    (1975, 255, datetime(1975, 12, 7, 17, 46, 9, tzinfo=UTC)),
    (1988, 285, datetime(1988, 1, 6, 3, 3, 29, tzinfo=UTC)),
    (1988, 315, datetime(1988, 2, 4, 14, 42, 48, tzinfo=UTC)),
    (1988, 345, datetime(1988, 3, 5, 8, 46, 32, tzinfo=UTC)),
    (1988, 15, datetime(1988, 4, 4, 13, 39, 3, tzinfo=UTC)),
    (1988, 45, datetime(1988, 5, 5, 7, 1, 43, tzinfo=UTC)),
    (1988, 75, datetime(1988, 6, 5, 11, 14, 52, tzinfo=UTC)),
    (1988, 105, datetime(1988, 7, 6, 21, 32, 54, tzinfo=UTC)),
    (1988, 135, datetime(1988, 8, 7, 7, 20, 15, tzinfo=UTC)),
    (1988, 165, datetime(1988, 9, 7, 10, 11, 30, tzinfo=UTC)),
    (1988, 195, datetime(1988, 10, 8, 1, 44, 28, tzinfo=UTC)),
    (1988, 225, datetime(1988, 11, 7, 4, 48, 54, tzinfo=UTC)),
    (1988, 255, datetime(1988, 12, 6, 21, 34, 28, tzinfo=UTC)),
    (1990, 285, datetime(1990, 1, 5, 14, 33, 13, tzinfo=UTC)),
    (1990, 315, datetime(1990, 2, 4, 2, 13, 59, tzinfo=UTC)),
    (1990, 345, datetime(1990, 3, 5, 20, 19, 16, tzinfo=UTC)),
    (1990, 15, datetime(1990, 4, 5, 1, 12, 54, tzinfo=UTC)),
    (1990, 45, datetime(1990, 5, 5, 18, 35, 25, tzinfo=UTC)),
    (1990, 75, datetime(1990, 6, 5, 22, 46, 18, tzinfo=UTC)),
    (1990, 105, datetime(1990, 7, 7, 9, 0, 28, tzinfo=UTC)),
    (1990, 135, datetime(1990, 8, 7, 18, 45, 31, tzinfo=UTC)),
    (1990, 165, datetime(1990, 9, 7, 21, 37, 27, tzinfo=UTC)),
    (1990, 195, datetime(1990, 10, 8, 13, 13, 47, tzinfo=UTC)),
    (1990, 225, datetime(1990, 11, 7, 16, 23, 28, tzinfo=UTC)),
    (1990, 255, datetime(1990, 12, 7, 9, 14, 9, tzinfo=UTC)),
    (2000, 285, datetime(2000, 1, 6, 1, 0, 40, tzinfo=UTC)),
    (2000, 315, datetime(2000, 2, 4, 12, 40, 22, tzinfo=UTC)),
    (2000, 345, datetime(2000, 3, 5, 6, 42, 38, tzinfo=UTC)),
    (2000, 15, datetime(2000, 4, 4, 11, 31, 57, tzinfo=UTC)),
    (2000, 45, datetime(2000, 5, 5, 4, 50, 9, tzinfo=UTC)),
    (2000, 75, datetime(2000, 6, 5, 8, 58, 33, tzinfo=UTC)),
    (2000, 105, datetime(2000, 7, 6, 19, 13, 56, tzinfo=UTC)),
    (2000, 135, datetime(2000, 8, 7, 5, 2, 59, tzinfo=UTC)),
    (2000, 165, datetime(2000, 9, 7, 7, 59, 9, tzinfo=UTC)),
    (2000, 195, datetime(2000, 10, 7, 23, 38, 11, tzinfo=UTC)),
    (2000, 225, datetime(2000, 11, 7, 2, 48, 3, tzinfo=UTC)),
    (2000, 255, datetime(2000, 12, 6, 19, 37, 1, tzinfo=UTC)),
    (2026, 285, datetime(2026, 1, 5, 8, 23, 9, tzinfo=UTC)),
    (2026, 315, datetime(2026, 2, 3, 20, 2, 7, tzinfo=UTC)),
    (2026, 345, datetime(2026, 3, 5, 13, 58, 59, tzinfo=UTC)),
    (2026, 15, datetime(2026, 4, 4, 18, 39, 59, tzinfo=UTC)),
    (2026, 45, datetime(2026, 5, 5, 11, 48, 43, tzinfo=UTC)),
    (2026, 75, datetime(2026, 6, 5, 15, 48, 21, tzinfo=UTC)),
    (2026, 105, datetime(2026, 7, 7, 1, 56, 57, tzinfo=UTC)),
    (2026, 135, datetime(2026, 8, 7, 11, 42, 44, tzinfo=UTC)),
    (2026, 165, datetime(2026, 9, 7, 14, 41, 17, tzinfo=UTC)),
    (2026, 195, datetime(2026, 10, 8, 6, 29, 17, tzinfo=UTC)),
    (2026, 225, datetime(2026, 11, 7, 9, 52, 4, tzinfo=UTC)),
    (2026, 255, datetime(2026, 12, 7, 2, 52, 31, tzinfo=UTC)),
    (2049, 285, datetime(2049, 1, 4, 22, 18, 51, tzinfo=UTC)),
    (2049, 315, datetime(2049, 2, 3, 9, 53, 31, tzinfo=UTC)),
    (2049, 345, datetime(2049, 3, 5, 3, 43, 4, tzinfo=UTC)),
    (2049, 15, datetime(2049, 4, 4, 8, 14, 31, tzinfo=UTC)),
    (2049, 45, datetime(2049, 5, 5, 1, 12, 47, tzinfo=UTC)),
    (2049, 75, datetime(2049, 6, 5, 5, 3, 53, tzinfo=UTC)),
    (2049, 105, datetime(2049, 7, 6, 15, 8, 58, tzinfo=UTC)),
    (2049, 135, datetime(2049, 8, 7, 0, 58, 4, tzinfo=UTC)),
    (2049, 165, datetime(2049, 9, 7, 4, 5, 41, tzinfo=UTC)),
    (2049, 195, datetime(2049, 10, 7, 20, 5, 10, tzinfo=UTC)),
    (2049, 225, datetime(2049, 11, 6, 23, 38, 34, tzinfo=UTC)),
    (2049, 255, datetime(2049, 12, 6, 16, 46, 48, tzinfo=UTC)),
]

# Hong Kong Observatory, "Date and Time of the 24 Solar Terms" for 2013 and 2016
# (hko.gov.hk/en/gts/astron<YYYY>/Solar_Term_<YYYY>.htm), the 12 jie terms,
# published in Hong Kong Time to the minute and converted here to UTC.
_HKT = timedelta(hours=8)
HKO_REFERENCE = [
    (year, longitude, datetime(*stamp, tzinfo=UTC) - _HKT)
    for year, longitude, stamp in (
        (2013, 285, (2013, 1, 5, 12, 34)),
        (2013, 315, (2013, 2, 4, 0, 13)),
        (2013, 345, (2013, 3, 5, 18, 15)),
        (2013, 15, (2013, 4, 4, 23, 2)),
        (2013, 45, (2013, 5, 5, 16, 18)),
        (2013, 75, (2013, 6, 5, 20, 23)),
        (2013, 105, (2013, 7, 7, 6, 35)),
        (2013, 135, (2013, 8, 7, 16, 20)),
        (2013, 165, (2013, 9, 7, 19, 16)),
        (2013, 195, (2013, 10, 8, 10, 58)),
        (2013, 225, (2013, 11, 7, 14, 14)),
        (2013, 255, (2013, 12, 7, 7, 9)),
        (2016, 285, (2016, 1, 6, 6, 8)),
        (2016, 315, (2016, 2, 4, 17, 46)),
        (2016, 345, (2016, 3, 5, 11, 44)),
        (2016, 15, (2016, 4, 4, 16, 28)),
        (2016, 45, (2016, 5, 5, 9, 42)),
        (2016, 75, (2016, 6, 5, 13, 49)),
        (2016, 105, (2016, 7, 7, 0, 3)),
        (2016, 135, (2016, 8, 7, 9, 53)),
        (2016, 165, (2016, 9, 7, 12, 51)),
        (2016, 195, (2016, 10, 8, 4, 33)),
        (2016, 225, (2016, 11, 7, 7, 48)),
        (2016, 255, (2016, 12, 7, 0, 41)),
    )
]


@pytest.mark.parametrize(("year", "longitude", "expected_utc"), SKYFIELD_REFERENCE + HKO_REFERENCE)
def test_term_moment_matches_the_reference_within_two_minutes(year, longitude, expected_utc) -> None:
    assert abs(term_moment(year, longitude) - expected_utc) <= timedelta(minutes=2)


def test_jie_moments_are_twelve_in_order_starting_with_xiaohan() -> None:
    moments = jie_moments(2026)
    assert [branch for branch, _ in moments] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]
    assert all(a[1] < b[1] for a, b in zip(moments, moments[1:], strict=False))
    assert all(moment.year == 2026 for _, moment in moments)


def test_solar_longitude_is_normalised() -> None:
    for month in range(1, 13):
        assert 0 <= solar_longitude(datetime(2026, month, 1, tzinfo=UTC)) < 360


def test_delta_t_is_in_the_known_range() -> None:
    assert 60 < delta_t_seconds(2000) < 66
    assert -5 < delta_t_seconds(1900) < 0
