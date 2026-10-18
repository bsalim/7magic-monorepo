"""A couple's compatibility and the clash check for a candidate wedding date.

Both read only three things per partner, the ones tradition weighs: the year
branch (the shio, the family side), the day branch (the spouse palace) and
the day master. The result is a list of findings and one of three tones, never
a score: a number would claim a precision the tradition does not have.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from app.domains.bazi.pillars import Chart, Pillar, chart_for, day_pillar
from app.domains.bazi.relations import RULE_KIND, Kind, Rule, branch_rules, controls, generates, stem_rules

__all__ = [
    "Compatibility",
    "DateCheck",
    "DateReason",
    "Finding",
    "chart_for",
    "check_date",
    "compatibility",
]

Tone = Literal["harmony", "balanced", "clash"]
Verdict = Literal["safe", "consider", "clash"]


@dataclass(frozen=True)
class Finding:
    rule: Rule
    kind: Kind
    pillar: Literal["year", "day", "day_master"]
    # The first and second partner's branch, or stem for the day master.
    a: int
    b: int
    # Which partner (0 or 1) generates or controls the other; None otherwise.
    source: int | None = None


@dataclass(frozen=True)
class Compatibility:
    tone: Tone
    findings: list[Finding]


@dataclass(frozen=True)
class DateReason:
    partner: int
    against: Literal["shio", "day"]
    rule: Rule


@dataclass(frozen=True)
class DateCheck:
    day: date
    pillar: Pillar
    verdict: Verdict
    reasons: list[DateReason]


def _direction(rule: Rule, a: int, b: int) -> int | None:
    ea, eb = a // 2, b // 2
    if rule == "generates":
        return 0 if generates(ea, eb) else 1
    if rule == "controls":
        return 0 if controls(ea, eb) else 1
    return None


def compatibility(first: Chart, second: Chart) -> Compatibility:
    findings: list[Finding] = []
    for pillar, a, b in (
        ("year", first.year.branch, second.year.branch),
        ("day", first.day.branch, second.day.branch),
    ):
        findings += [Finding(rule, RULE_KIND[rule], pillar, a, b) for rule in branch_rules(a, b)]
    a, b = first.day_master, second.day_master
    findings += [
        Finding(rule, RULE_KIND[rule], "day_master", a, b, _direction(rule, a, b)) for rule in stem_rules(a, b)
    ]

    # The spouse palaces clashing outweighs everything else in the reading.
    if any(f.rule == "clash" and f.pillar == "day" for f in findings):
        tone: Tone = "clash"
    else:
        harmonies = sum(f.kind == "harmony" for f in findings)
        against = sum(f.kind in ("clash", "caution") for f in findings)
        tone = "harmony" if harmonies > against else "balanced"
    return Compatibility(tone=tone, findings=findings)


def check_date(day: date, charts: tuple[Chart, Chart]) -> DateCheck:
    pillar = day_pillar(day)
    reasons = [
        DateReason(partner, against, rule)
        for partner, chart in enumerate(charts)
        for against, branch in (("shio", chart.year.branch), ("day", chart.day.branch))
        for rule in branch_rules(pillar.branch, branch)
    ]
    rules = {reason.rule for reason in reasons}
    verdict: Verdict = "clash" if "clash" in rules else "consider" if "harm" in rules else "safe"
    return DateCheck(day=day, pillar=pillar, verdict=verdict, reasons=reasons)
