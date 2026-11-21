"""The almanac month as the wire shape, labelled in the requested locale."""

from __future__ import annotations

from app.domains.almanac.schemas import (
    AlmanacDayOut,
    AlmanacRequest,
    AlmanacResponse,
    OfficerOut,
    ShioReasonOut,
)
from app.domains.almanac.service import officer_rating, read_month
from app.domains.bazi.labels import ANIMALS, label
from app.domains.bazi.response import branch_out, pillar_out
from app.schemas.content import Locale

OFFICER_CHARS = "建除满平定执破危成收开闭"
OFFICER_PINYIN = (
    "Jiàn",
    "Chú",
    "Mǎn",
    "Píng",
    "Dìng",
    "Zhí",
    "Pò",
    "Wēi",
    "Chéng",
    "Shōu",
    "Kāi",
    "Bì",
)
# Short glosses only; what a day is good for is the page's copy.
_OFFICER_LABELS: dict[Locale, tuple[str, ...]] = {
    "id": (
        "Tegak", "Singkir", "Penuh", "Rata", "Mantap", "Pegang",
        "Pecah", "Bahaya", "Berhasil", "Terima", "Buka", "Tutup",
    ),
    "en": (
        "Establish", "Remove", "Full", "Balance", "Stable", "Initiate",
        "Destruction", "Danger", "Success", "Receive", "Open", "Close",
    ),
}  # fmt: skip


def _officer(index: int, locale: Locale) -> OfficerOut:
    return OfficerOut(
        index=index,
        char=OFFICER_CHARS[index],
        pinyin=OFFICER_PINYIN[index],
        label=_OFFICER_LABELS[locale][index],
        rating=officer_rating(index),
    )


def build_response(payload: AlmanacRequest) -> AlmanacResponse:
    locale = payload.locale
    shio = tuple(ANIMALS.index(animal) for animal in payload.shio)
    return AlmanacResponse(
        year=payload.year,
        month=payload.month,
        shio=[branch_out(branch, locale) for branch in shio],
        days=[
            AlmanacDayOut(
                date=reading.day,
                pillar=pillar_out(reading.pillar, locale),
                officer=_officer(reading.officer, locale),
                clashes=branch_out(reading.clashes, locale),
                reasons=[
                    ShioReasonOut(
                        partner=reason.partner,
                        rule=reason.rule,
                        rule_label=label("rule", reason.rule, locale),
                    )
                    for reason in reading.reasons
                ],
                rating=reading.rating,
            )
            for reading in read_month(payload.year, payload.month, shio)
        ],
    )
