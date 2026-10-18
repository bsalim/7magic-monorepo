"""Request and response shapes for POST /api/v1/public/bazi."""

from __future__ import annotations

from datetime import date, time
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.domains.bazi.pillars import Zone
from app.domains.bazi.relations import Kind, Rule
from app.domains.bazi.service import Tone, Verdict
from app.schemas.content import Locale

# The range the solar-term series and the Delta T polynomials are checked over.
FIRST_YEAR = 1900
LAST_YEAR = 2100
MAX_DATES = 3


def _in_range(value: date) -> date:
    if not FIRST_YEAR <= value.year <= LAST_YEAR:
        raise ValueError(f"Dates must fall between {FIRST_YEAR} and {LAST_YEAR}.")
    return value


class PartnerIn(BaseModel):
    name: str | None = Field(default=None, max_length=40)
    birth_date: date
    birth_time: time | None = None
    zone: Zone = "WIB"

    @field_validator("birth_date")
    @classmethod
    def _birth_date_in_range(cls, value: date) -> date:
        return _in_range(value)


class BaziRequest(BaseModel):
    partners: list[PartnerIn] = Field(min_length=2, max_length=2)
    dates: list[date] = Field(default_factory=list, max_length=MAX_DATES)
    locale: Locale = "id"

    @field_validator("dates")
    @classmethod
    def _dates_in_range(cls, value: list[date]) -> list[date]:
        # A repeated date would come back as two identical checks, which the
        # page keys by date; refuse it rather than answer twice.
        if len(set(value)) != len(value):
            raise ValueError("Each date can be checked once.")
        return [_in_range(day) for day in value]


class StemOut(BaseModel):
    index: int
    char: str
    pinyin: str
    element: str
    element_label: str
    yang: bool


class BranchOut(BaseModel):
    index: int
    char: str
    pinyin: str
    element: str
    element_label: str
    animal: str
    animal_label: str


class PillarOut(BaseModel):
    stem: StemOut
    branch: BranchOut
    depends_on_time: bool
    near_term: bool


class ChartOut(BaseModel):
    name: str | None
    year: PillarOut
    month: PillarOut
    day: PillarOut
    hour: PillarOut | None
    day_master: StemOut
    shio: BranchOut
    elements: dict[str, int]


class FindingOut(BaseModel):
    rule: Rule
    rule_label: str
    kind: Kind
    pillar: Literal["year", "day", "day_master"]
    a: str
    b: str
    source: int | None


class DateReasonOut(BaseModel):
    partner: int
    against: Literal["shio", "day"]
    rule: Rule
    rule_label: str


class DateCheckOut(BaseModel):
    date: date
    pillar: PillarOut
    verdict: Verdict
    reasons: list[DateReasonOut]


class BaziResponse(BaseModel):
    charts: list[ChartOut]
    tone: Tone
    tone_label: str
    findings: list[FindingOut]
    date_checks: list[DateCheckOut]
