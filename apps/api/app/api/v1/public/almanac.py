"""Public Chinese almanac month for the wedding tools (Tanggal Baik Tionghoa).

A pure calculation: a month and, optionally, the couple's two shio in, a
reading per day out. Nothing is stored. It is a POST only to match the Ba Zi
calculator the page's proxy and client were modelled on; there is nothing
private in the request.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.domains.almanac.response import build_response
from app.domains.almanac.schemas import AlmanacRequest, AlmanacResponse

router = APIRouter()


@router.post("/almanac", response_model=AlmanacResponse)
def almanac(payload: AlmanacRequest) -> AlmanacResponse:
    return build_response(payload)
