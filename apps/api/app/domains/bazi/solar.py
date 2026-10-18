"""The Sun's apparent longitude and the moments of the 12 jie solar terms.

Ba Zi years start at Lichun and months at the jie terms, so a chart is only as
good as these moments. The method is Meeus, *Astronomical Algorithms* (2nd ed.),
chapter 25 "higher accuracy": VSOP87 for the Earth, turned geocentric, then
the FK5 correction, nutation (chapter 22, the abridged series, good to half a
second of arc) and aberration. The low-accuracy chapter 25 formula is not
enough here: its ~0.01 degree error is about 15 minutes of time, the size of
the boundary cases the tool has to get right.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from functools import cache

from app.domains.bazi import vsop87_earth

# Sun longitudes of the jie terms, from Lichun (start of the Yin month) on.
# Index i opens the month whose branch is (2 + i) % 12.
JIE_LONGITUDES: tuple[float, ...] = (315, 345, 15, 45, 75, 105, 135, 165, 195, 225, 255, 285)

_UNIX_EPOCH_JD = 2440587.5
_J2000 = 2451545.0
_ARCSEC = 1 / 3600


def delta_t_seconds(year: float) -> float:
    """TT minus UT, from the Espenak-Meeus polynomials (NASA eclipse pages).

    Outside 1900-2150 the nearest polynomial is extrapolated; the tool rejects
    those years before they get here.
    """
    if year < 1920:
        t = year - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    if year < 1941:
        t = year - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if year < 1961:
        t = year - 1950
        return 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    if year < 1986:
        t = year - 1975
        return 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    if year < 2005:
        t = year - 2000
        return (
            63.86
            + 0.3345 * t
            - 0.060374 * t**2
            + 0.0017275 * t**3
            + 0.000651814 * t**4
            + 0.00002373599 * t**5
        )
    if year < 2050:
        t = year - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    return -20 + 32 * ((year - 1820) / 100) ** 2 - 0.5628 * (2150 - year)


def _julian_day(moment: datetime) -> float:
    return _UNIX_EPOCH_JD + moment.timestamp() / 86400


def _from_julian_day(jd: float) -> datetime:
    return datetime.fromtimestamp((jd - _UNIX_EPOCH_JD) * 86400, tz=UTC)


def _decimal_year(jd: float) -> float:
    return 2000 + (jd - _J2000) / 365.25


def _series(groups: vsop87_earth.Series, tau: float) -> float:
    return sum(
        sum(a * math.cos(b + c * tau) for a, b, c in terms) * tau**power
        for power, terms in enumerate(groups)
    )


def _apparent_longitude_tt(jde: float) -> float:
    tau = (jde - _J2000) / 365250
    centuries = tau * 10

    # Heliocentric Earth, turned round to give the geocentric Sun.
    longitude = math.degrees(_series(vsop87_earth.L, tau)) + 180
    radius = _series(vsop87_earth.R, tau)

    # FK5: VSOP87's dynamical equinox sits a fraction of an arcsecond off.
    longitude -= 0.09033 * _ARCSEC

    omega = math.radians(125.04452 - 1934.136261 * centuries)
    sun_mean = math.radians(280.4665 + 36000.7698 * centuries)
    moon_mean = math.radians(218.3165 + 481267.8813 * centuries)
    nutation = (
        -17.20 * math.sin(omega)
        - 1.32 * math.sin(2 * sun_mean)
        - 0.23 * math.sin(2 * moon_mean)
        + 0.21 * math.sin(2 * omega)
    )
    aberration = -20.4898 / radius
    return (longitude + (nutation + aberration) * _ARCSEC) % 360


def solar_longitude(moment: datetime) -> float:
    """Apparent geocentric longitude of the Sun in degrees, [0, 360), at a UTC moment."""
    jd = _julian_day(moment)
    return _apparent_longitude_tt(jd + delta_t_seconds(_decimal_year(jd)) / 86400)


def term_moment(year: int, longitude: float) -> datetime:
    """The UTC moment in Gregorian `year` when the Sun reaches `longitude`."""
    # The Sun is near 280.46 degrees on 1 January and moves ~0.9856 a day,
    # which lands the first guess within a couple of days of the answer.
    jan_first = _julian_day(datetime(year, 1, 1, tzinfo=UTC))
    jde = jan_first + ((longitude - 280.46) % 360) / 0.9856
    jde += delta_t_seconds(year) / 86400
    for _ in range(20):
        # Meeus's own step (chapter 27): 58 days per radian of longitude to go.
        step = 58 * math.sin(math.radians(longitude - _apparent_longitude_tt(jde)))
        jde += step
        if abs(step) < 0.5 / 86400:
            break
    utc_jd = jde - delta_t_seconds(_decimal_year(jde)) / 86400
    return _from_julian_day(utc_jd).replace(microsecond=0)


@cache
def jie_moments(year: int) -> list[tuple[int, datetime]]:
    """(month branch, UTC moment) of the 12 jie terms in Gregorian `year`, in date order."""
    moments = [
        ((2 + index) % 12, term_moment(year, longitude))
        for index, longitude in enumerate(JIE_LONGITUDES)
    ]
    return sorted(moments, key=lambda item: item[1])
