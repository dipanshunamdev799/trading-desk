from __future__ import annotations

import re
from fastapi import APIRouter, HTTPException, Response
from ..services.ipo_service import get_ipo_service

router = APIRouter(prefix="/ipos", tags=["IPO research"])


@router.get("")
def catalogue(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return get_ipo_service().catalogue()


@router.get("/{ipo_id}")
def detail(ipo_id: str, response: Response):
    response.headers["Cache-Control"] = "no-store"
    if not re.fullmatch(r"[a-zA-Z0-9-]{1,160}", ipo_id):
        raise HTTPException(400, "Invalid IPO identifier")
    try:
        return get_ipo_service().detail(ipo_id)
    except KeyError:
        raise HTTPException(404, "IPO is not in the retained catalogue") from None
