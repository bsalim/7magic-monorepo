"""Branch and stem relations, the couple's compatibility, and the date check.

The relation tables are classical and short, so they are pinned both as the
named pairs and as properties (each branch has exactly one clash partner, one
combination partner, one harm partner), which catches an off-by-one in the
arithmetic forms the engine uses.
"""

from __future__ import annotations

from datetime import date, time, timedelta

from app.domains.bazi.pillars import Chart, Pillar, chart_for, day_pillar
from app.domains.bazi.relations import RULE_KIND, branch_rules, stem_rules
from app.domains.bazi.service import DateReason, check_date, compatibility


def _chart(year_branch: int, day_branch: int, day_stem: int) -> Chart:
    """A chart with only the parts compatibility reads set on purpose."""
    year = Pillar(stem=year_branch % 10, branch=year_branch)
    day = Pillar(stem=day_stem, branch=day_branch)
    return Chart(year=year, month=Pillar(stem=0, branch=2), day=day, hour=None)


def _date_with_branch(branch: int, start: date = date(2026, 9, 1)) -> date:
    for offset in range(12):
        day = start + timedelta(days=offset)
        if day_pillar(day).branch == branch:
            return day
    raise AssertionError("unreachable: branches repeat every 12 days")


def test_each_branch_has_exactly_one_clash_combination_and_harm_partner() -> None:
    for a in range(12):
        assert sum("clash" in branch_rules(a, b) for b in range(12)) == 1
        assert sum("six_combination" in branch_rules(a, b) for b in range(12)) == 1
        assert sum("harm" in branch_rules(a, b) for b in range(12)) == 1


def test_the_classical_branch_pairs() -> None:
    assert branch_rules(0, 6) == ["clash"]  # 子午
    assert branch_rules(5, 11) == ["clash"]  # 巳亥
    assert branch_rules(2, 11) == ["six_combination"]  # 寅亥
    assert branch_rules(6, 7) == ["six_combination"]  # 午未
    assert branch_rules(0, 7) == ["harm"]  # 子未
    assert branch_rules(9, 10) == ["harm"]  # 酉戌
    assert branch_rules(8, 0) == ["half_harmony"]  # 申子
    assert branch_rules(2, 6) == ["half_harmony"]  # 寅午


def test_a_half_harmony_needs_the_middle_branch() -> None:
    assert "half_harmony" not in branch_rules(8, 4)  # 申辰 without 子
    assert "half_harmony" not in branch_rules(2, 10)  # 寅戌 without 午


def test_a_branch_has_no_relation_with_itself() -> None:
    for a in range(12):
        assert branch_rules(a, a) == []


def test_stem_relations() -> None:
    assert "stem_combination" in stem_rules(0, 5)  # 甲己
    assert "stem_combination" in stem_rules(9, 4)  # 癸戊
    assert "generates" in stem_rules(0, 2)  # wood feeds fire
    assert "generates" in stem_rules(2, 0)  # either way round
    assert "controls" in stem_rules(0, 4)  # wood controls earth
    assert "controls" in stem_rules(8, 2)  # water controls fire
    assert stem_rules(0, 1) == ["same_element"]


def test_every_stem_pair_has_exactly_one_element_relation() -> None:
    element_rules = {"generates", "controls", "same_element"}
    for a in range(10):
        for b in range(10):
            assert len(element_rules & set(stem_rules(a, b))) == 1


def test_rule_kinds() -> None:
    assert RULE_KIND["clash"] == "clash"
    assert RULE_KIND["harm"] == "caution"
    assert RULE_KIND["controls"] == "caution"
    assert RULE_KIND["same_element"] == "neutral"
    for rule in ("six_combination", "half_harmony", "stem_combination", "generates"):
        assert RULE_KIND[rule] == "harmony"


def test_a_day_branch_clash_sets_the_clash_tone() -> None:
    # Year branches combine (子丑) and the day masters generate, but the spouse
    # palaces clash (子午): tradition weighs that above the rest.
    result = compatibility(_chart(0, 0, 0), _chart(1, 6, 2))
    assert result.tone == "clash"
    assert any(f.rule == "clash" and f.pillar == "day" for f in result.findings)


def test_mostly_harmony_gives_the_harmony_tone() -> None:
    # 寅亥 years, 午未 days, Jia and Bing day masters (wood feeds fire).
    result = compatibility(_chart(2, 6, 0), _chart(11, 7, 2))
    assert result.tone == "harmony"
    generates = next(f for f in result.findings if f.rule == "generates")
    assert generates.source == 0 and generates.pillar == "day_master"


def test_a_year_clash_alone_is_balanced_not_clash() -> None:
    # 子午 years clash, days unrelated (寅 and 辰 share nothing), same element.
    result = compatibility(_chart(0, 2, 0), _chart(6, 4, 1))
    assert result.tone == "balanced"


def test_the_controlling_partner_is_named() -> None:
    result = compatibility(_chart(0, 2, 4), _chart(0, 4, 0))  # earth vs wood
    controls = next(f for f in result.findings if f.rule == "controls")
    assert controls.source == 1  # wood controls earth: the second partner


def test_identical_charts_are_balanced() -> None:
    chart = chart_for(date(1995, 5, 5), time(10), "WIB")
    result = compatibility(chart, chart)
    assert result.tone == "balanced"
    assert all(f.rule != "clash" for f in result.findings)
    assert [f.rule for f in result.findings] == ["same_element"]


def test_a_date_clashing_with_either_shio_is_a_clash() -> None:
    first, second = _chart(2, 3, 0), _chart(0, 4, 2)  # second partner is a Rat
    check = check_date(_date_with_branch(6), (first, second))  # a Horse day
    assert check.verdict == "clash"
    assert DateReason(partner=1, against="shio", rule="clash") in check.reasons
    assert check.pillar.branch == 6


def test_a_date_clashing_with_a_day_branch_is_a_clash() -> None:
    first, second = _chart(2, 3, 0), _chart(4, 1, 2)
    check = check_date(_date_with_branch(9), (first, second))  # 酉 clashes 卯
    assert check.verdict == "clash"
    assert DateReason(partner=0, against="day", rule="clash") in check.reasons


def test_a_harm_only_date_needs_consideration() -> None:
    first, second = _chart(2, 3, 0), _chart(4, 1, 2)
    check = check_date(_date_with_branch(5), (first, second))  # 巳 harms 寅, touches nothing else
    assert check.verdict == "consider"
    assert DateReason(partner=0, against="shio", rule="harm") in check.reasons
    assert all(reason.rule != "clash" for reason in check.reasons)


def test_a_quiet_date_is_safe_and_lists_its_harmonies() -> None:
    first, second = _chart(2, 3, 0), _chart(4, 1, 2)
    check = check_date(_date_with_branch(11), (first, second))  # 亥 combines 寅
    assert check.verdict == "safe"
    assert DateReason(partner=0, against="shio", rule="six_combination") in check.reasons
