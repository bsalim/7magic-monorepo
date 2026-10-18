"""The classical relations between two branches or two stems.

Only the relations the schools broadly agree on (see the design doc):
punishments are left out, and a half three-harmony counts only when it holds
the trio's middle branch. The tables are written as arithmetic on the indices,
which is exact for these sets and pinned against the named pairs in the tests.
"""

from __future__ import annotations

from typing import Literal

Rule = Literal[
    "six_combination",
    "half_harmony",
    "clash",
    "harm",
    "stem_combination",
    "generates",
    "controls",
    "same_element",
]
Kind = Literal["harmony", "caution", "clash", "neutral"]

RULE_KIND: dict[Rule, Kind] = {
    "six_combination": "harmony",
    "half_harmony": "harmony",
    "stem_combination": "harmony",
    "generates": "harmony",
    "harm": "caution",
    "controls": "caution",
    "clash": "clash",
    "same_element": "neutral",
}

# Zi, Mao, Wu, You: the middle of each three-harmony trio.
_TRIO_MIDDLES = frozenset({0, 3, 6, 9})


def branch_rules(a: int, b: int) -> list[Rule]:
    rules: list[Rule] = []
    if (a - b) % 12 == 6:
        rules.append("clash")
    if (a + b) % 12 == 1:
        rules.append("six_combination")
    if (a + b) % 12 == 7:
        rules.append("harm")
    # Trios are the branches four apart (Shen-Zi-Chen, Hai-Mao-Wei, ...).
    if a != b and a % 4 == b % 4 and (a in _TRIO_MIDDLES or b in _TRIO_MIDDLES):
        rules.append("half_harmony")
    return rules


def generates(a_element: int, b_element: int) -> bool:
    """Wood feeds fire, fire earth, earth metal, metal water, water wood."""
    return (a_element + 1) % 5 == b_element


def controls(a_element: int, b_element: int) -> bool:
    """Wood parts earth, earth dams water, water quenches fire, fire melts metal, metal cuts wood."""
    return (a_element + 2) % 5 == b_element


def stem_rules(a: int, b: int) -> list[Rule]:
    rules: list[Rule] = []
    if (a - b) % 10 == 5:
        rules.append("stem_combination")
    ea, eb = a // 2, b // 2
    if ea == eb:
        rules.append("same_element")
    elif generates(ea, eb) or generates(eb, ea):
        rules.append("generates")
    else:
        rules.append("controls")
    return rules
