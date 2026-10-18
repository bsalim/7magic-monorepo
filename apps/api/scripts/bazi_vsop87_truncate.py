"""Write `app/domains/bazi/vsop87_earth.py` from the published VSOP87D Earth file.

VSOP87 (Bretagnon & Francou 1988) is the planetary theory behind Meeus's
higher-accuracy solar position. The full Earth series has about 2,400 terms;
terms below AMPLITUDE_FLOOR radians (or AU) are dropped, close to the cut
Meeus makes in *Astronomical Algorithms*, Appendix III, which keeps the Sun's
longitude to about a second of arc over 1900-2100, i.e. solar terms to well
under a minute.

Download the source once (CDS mirror of the IMCCE release) and run:

    curl -O https://cdsarc.cds.unistra.fr/ftp/VI/81/VSOP87D.ear
    uv run python scripts/bazi_vsop87_truncate.py VSOP87D.ear

Re-running overwrites the module; the tests in tests/test_bazi_solar.py say
whether a different floor still holds the two-minute tolerance.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

AMPLITUDE_FLOOR = 2.5e-7
TARGET = Path(__file__).resolve().parents[1] / "app" / "domains" / "bazi" / "vsop87_earth.py"
HEADER = re.compile(r"VARIABLE (\d) \(LBR\)\s+\*T\*\*(\d)")
VARIABLES = {"1": "L", "2": "B", "3": "R"}


def read_series(path: Path) -> dict[str, list[list[tuple[float, float, float]]]]:
    series: dict[str, list[list[tuple[float, float, float]]]] = {"L": [], "B": [], "R": []}
    current: list[tuple[float, float, float]] | None = None
    for line in path.read_text().splitlines():
        header = HEADER.search(line)
        if header:
            current = []
            series[VARIABLES[header.group(1)]].append(current)
            continue
        if current is None or not line.strip():
            continue
        # The last three columns are A, B, C of A * cos(B + C * tau).
        a, b, c = (float(field) for field in line.split()[-3:])
        if abs(a) >= AMPLITUDE_FLOOR:
            current.append((a, b, c))
    return series


def render(series: dict[str, list[list[tuple[float, float, float]]]]) -> str:
    total = sum(len(terms) for groups in series.values() for terms in groups)
    lines = [
        '"""VSOP87D Earth series, truncated: generated, do not edit by hand.',
        "",
        "Bretagnon & Francou (1988), Astron. Astrophys. 202, 309; IMCCE release via",
        "CDS catalogue VI/81. Written by scripts/bazi_vsop87_truncate.py with",
        f"amplitudes below {AMPLITUDE_FLOOR:g} dropped ({total} terms kept).",
        "",
        "Each variable is a tuple of series, one per power of tau (Julian millennia",
        "from J2000.0, TT); each term (A, B, C) contributes A * cos(B + C * tau).",
        "L and B are heliocentric longitude and latitude in radians, R the radius",
        "vector in AU, referred to the ecliptic and equinox of the date.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "Series = tuple[tuple[tuple[float, float, float], ...], ...]",
    ]
    for name in ("L", "B", "R"):
        lines += ["", f"{name}: Series = ("]
        for terms in series[name]:
            lines.append("    (")
            lines += [f"        ({a!r}, {b!r}, {c!r})," for a, b, c in terms]
            lines.append("    ),")
        lines.append(")")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path, help="path to VSOP87D.ear")
    TARGET.write_text(render(read_series(parser.parse_args().source)))
    print(f"wrote {TARGET}")
