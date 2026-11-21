"""Request and response shapes for POST /api/v1/public/almanac."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.domains.almanac.service import OfficerRating, Rating
from app.domains.bazi.relations import Rule
from app.domains.bazi.schemas import FIRST_YEAR, LAST_YEAR, BranchOut, PillarOut
from app.schemas.content import Locale

Animal = Literal[
    "rat", "ox", "tiger", "rabbit", "dragon", "snake",
    "horse", "goat", "monkey", "rooster", "dog", "pig",
]  # fmt: skip


class AlmanacRequest(BaseModel):
    # The same span the solar-term series is checked over for Ba Zi.
    year: int = Field(ge=FIRST_YEAR, le=LAST_YEAR)
    month: int = Field(ge=1, le=12)
    # The couple's shio, in the order the page asked for them. None or one is
    # allowed: the almanac's own reading of the month does not need them.
    shio: list[Animal] = Field(default_factory=list, max_length=2)
    locale: Locale = "id"


class OfficerOut(BaseModel):
    index: int
    char: str
    pinyin: str
    label: str
    rating: OfficerRating


class ShioReasonOut(BaseModel):
    partner: int
    rule: Rule
    rule_label: str


class AlmanacDayOut(BaseModel):
    date: date
    pillar: PillarOut
    officer: OfficerOut
    # The animal this day opposes: the "ciong" a printed almanac lists.
    clashes: BranchOut
    reasons: list[ShioReasonOut]
    rating: Rating


class AlmanacResponse(BaseModel):
    year: int
    month: int
    # The solar month each run of days belongs to, for the note under the grid.
    shio: list[BranchOut]
    days: list[AlmanacDayOut]
