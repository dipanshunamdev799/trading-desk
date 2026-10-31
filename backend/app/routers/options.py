from __future__ import annotations

from typing import Any, Optional, Literal

from fastapi import APIRouter, HTTPException, Query, Response

from ..services import max_pain_service
from ..services import pcr_service
from ..services import iv_service

router = APIRouter(prefix="/options", tags=["options"])


@router.get("/iv/history")
def iv_history(response: Response, expiry: str = Query(...), as_of: Optional[str] = None,
               instrument_key: str = Query("NSE_INDEX|Nifty 50")) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        return iv_service.history(expiry, as_of, instrument_key)
    except ValueError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, detail=f"IV history failed: {exc}") from exc


@router.get("/pcr/intraday")
def pcr_intraday(response: Response, expiry: str = Query(...), as_of: Optional[str] = None,
                 instrument_key: str = Query("NSE_INDEX|Nifty 50")) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        return pcr_service.intraday(expiry, as_of, instrument_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"PCR history failed: {exc}") from exc


@router.get("/expiries")
def expiries(
    instrument_key: str = Query("NSE_INDEX|Nifty 50"),
    include_past: bool = Query(True),
    past_days: int = Query(120, ge=7, le=365),
    include_unverified: bool = Query(True),
) -> list[dict[str, Any]]:
    try:
        return max_pain_service.list_expiries(
            instrument_key,
            include_past=include_past,
            past_days=past_days,
            include_unverified=include_unverified,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Upstox expiries failed: {exc}") from exc


@router.get("/max-pain")
def max_pain(
    response: Response,
    expiry: Optional[str] = None,
    as_of: Optional[str] = None,
    instrument_key: str = Query("NSE_INDEX|Nifty 50"),
    bucket: int = Query(15, ge=5, le=60),
    view: Literal["latest", "historical"] = "historical",
) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        return max_pain_service.snapshot(
            expiry=expiry, as_of=as_of, instrument_key=instrument_key, bucket=bucket, view=view
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Max pain snapshot failed: {exc}") from exc


@router.get("/max-pain/intraday")
def max_pain_intraday(
    response: Response,
    expiry: str = Query(...),
    as_of: Optional[str] = None,
    instrument_key: str = Query("NSE_INDEX|Nifty 50"),
) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        return max_pain_service.intraday(
            expiry=expiry, as_of=as_of, instrument_key=instrument_key
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Intraday refresh failed: {exc}") from exc


@router.get("/max-pain/sessions")
def max_pain_sessions(response: Response, expiry: str = Query(...),
                      instrument_key: str = Query("NSE_INDEX|Nifty 50")) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        return max_pain_service.sessions(expiry, instrument_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Trading sessions failed: {exc}") from exc


@router.get("/max-pain/history")
def max_pain_history(
    response: Response,
    expiry: Optional[str] = None,
    as_of: Optional[str] = None,
    history_days: int = Query(40, ge=5, le=120),
    signal_time: str = Query("10:15"),
    instrument_key: str = Query("NSE_INDEX|Nifty 50"),
) -> dict[str, Any]:
    response.headers["Cache-Control"] = "no-store"
    try:
        rows = max_pain_service.history(
            selected_expiry=expiry,
            as_of=as_of,
            history_days=history_days,
            signal_time=signal_time,
            instrument_key=instrument_key,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Max pain history failed: {exc}") from exc
    return {"count": len(rows), "points": rows}
