"""The engine's result as the wire shape, labelled in the requested locale.

It sits in the domain rather than in the router because two callers need the
same answer: the calculator endpoint returns it, and the result gate renders
the couple's emailed copy from it. Shaping it twice would let the email and the
page disagree about a chart.
"""

from __future__ import annotations

from app.domains.bazi.labels import (
    ANIMALS,
    BRANCH_CHARS,
    BRANCH_PINYIN,
    ELEMENTS,
    STEM_CHARS,
    STEM_PINYIN,
    label,
)
from app.domains.bazi.pillars import BRANCH_ELEMENTS, Chart, Pillar
from app.domains.bazi.schemas import (
    BaziRequest,
    BaziResponse,
    BranchOut,
    ChartOut,
    DateCheckOut,
    DateReasonOut,
    FindingOut,
    PillarOut,
    StemOut,
)
from app.domains.bazi.service import chart_for, check_date, compatibility
from app.schemas.content import Locale


def _stem(index: int, locale: Locale) -> StemOut:
    element = ELEMENTS[index // 2]
    return StemOut(
        index=index,
        char=STEM_CHARS[index],
        pinyin=STEM_PINYIN[index],
        element=element,
        element_label=label("element", element, locale),
        yang=index % 2 == 0,
    )


def branch_out(index: int, locale: Locale) -> BranchOut:
    element = ELEMENTS[BRANCH_ELEMENTS[index]]
    animal = ANIMALS[index]
    return BranchOut(
        index=index,
        char=BRANCH_CHARS[index],
        pinyin=BRANCH_PINYIN[index],
        element=element,
        element_label=label("element", element, locale),
        animal=animal,
        animal_label=label("animal", animal, locale),
    )


def pillar_out(pillar: Pillar, locale: Locale) -> PillarOut:
    return PillarOut(
        stem=_stem(pillar.stem, locale),
        branch=branch_out(pillar.branch, locale),
        depends_on_time=pillar.depends_on_time,
        near_term=pillar.near_term,
    )


def _chart(chart: Chart, name: str | None, locale: Locale) -> ChartOut:
    return ChartOut(
        name=name,
        year=pillar_out(chart.year, locale),
        month=pillar_out(chart.month, locale),
        day=pillar_out(chart.day, locale),
        hour=pillar_out(chart.hour, locale) if chart.hour else None,
        day_master=_stem(chart.day_master, locale),
        shio=branch_out(chart.shio, locale),
        elements=dict(zip(ELEMENTS, chart.element_counts, strict=True)),
    )


def build_response(payload: BaziRequest) -> BaziResponse:
    locale = payload.locale
    first, second = (chart_for(p.birth_date, p.birth_time, p.zone) for p in payload.partners)
    result = compatibility(first, second)
    chars = {"year": BRANCH_CHARS, "day": BRANCH_CHARS, "day_master": STEM_CHARS}
    return BaziResponse(
        charts=[_chart(chart, p.name, locale) for chart, p in zip((first, second), payload.partners, strict=True)],
        tone=result.tone,
        tone_label=label("tone", result.tone, locale),
        findings=[
            FindingOut(
                rule=f.rule,
                rule_label=label("rule", f.rule, locale),
                kind=f.kind,
                pillar=f.pillar,
                a=chars[f.pillar][f.a],
                b=chars[f.pillar][f.b],
                source=f.source,
            )
            for f in result.findings
        ],
        date_checks=[
            DateCheckOut(
                date=check.day,
                pillar=pillar_out(check.pillar, locale),
                verdict=check.verdict,
                reasons=[
                    DateReasonOut(
                        partner=r.partner,
                        against=r.against,
                        rule=r.rule,
                        rule_label=label("rule", r.rule, locale),
                    )
                    for r in check.reasons
                ],
            )
            for check in (check_date(day, (first, second)) for day in payload.dates)
        ],
    )
