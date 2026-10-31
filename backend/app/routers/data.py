from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import InstrumentOut
from ..services import market_data
from ..services.upstox_service import get_market_store

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/integration")
def integration_status() -> dict[str, Any]:
    """Inspect durable storage and cache/API usage without exposing credentials."""
    return get_market_store().status()


@router.get("/instruments", response_model=list[InstrumentOut])
async def list_instruments(db: AsyncSession = Depends(get_db)):
    return await market_data.list_instruments(db)


@router.get("/coverage")
async def coverage(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    return await market_data.coverage_summary(db)


@router.post("/candles/clear")
async def clear_candles(
    instrument_key: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    deleted = await market_data.clear_candles(db, instrument_key)
    return {"deleted": deleted}


@router.post("/instruments/upsert", response_model=InstrumentOut)
async def upsert_instrument(payload: dict[str, Any], db: AsyncSession = Depends(get_db)):
    try:
        return await market_data.upsert_instrument(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/backfill")
async def backfill(
    instrument_key: str,
    interval: str = "1minute",
    from_date: str = "2026-01-01",
    to_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Pull historical candles from Upstox in windows and persist to TimescaleDB."""
    end = to_date or datetime.now().strftime("%Y-%m-%d")
    try:
        written = await market_data.backfill_candles(
            db,
            instrument_key=instrument_key,
            interval=interval,
            from_date=from_date,
            to_date=end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Backfill failed: {exc}") from exc
    return {
        "instrument_key": instrument_key,
        "interval": interval,
        "from_date": from_date,
        "to_date": end,
        "rows_written": written,
    }
