from __future__ import annotations

from typing import Any, Optional
import asyncio
import re
import time

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from starlette.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import CandleSeries, MarketStatusOut, QuoteOut
from ..services import market_data, upstox_service

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/live/status")
def live_status(instrument_key: str = "NSE_INDEX|Nifty 50"):
    client = upstox_service.get_upstox()
    return {"stream": client.live.status(), "session": client.get_market_session(instrument_key)}


@router.websocket("/live")
async def market_live(websocket: WebSocket):
    from ..config import get_settings
    origin = websocket.headers.get("origin")
    if origin and origin.rstrip("/") not in {value.rstrip("/") for value in get_settings().cors_list}:
        await websocket.close(code=1008)
        return
    client = upstox_service.get_upstox()
    stream = client.live
    await websocket.accept()
    keys, revision, last_sent, session = [], -1, 0, None
    try:
        while True:
            try:
                message = await asyncio.wait_for(websocket.receive_json(), timeout=1)
                if not isinstance(message, dict):
                    await websocket.close(code=1008)
                    return
                requested = message.get("instrument_keys", [])
                if message.get("type") != "watch" or not isinstance(requested, list) or len(requested) > 500 or any(
                    not isinstance(key, str) or not re.fullmatch(r"[A-Z_]+\|[^\r\n|]{1,140}", key) for key in requested):
                    await websocket.close(code=1008)
                    return
                keys = sorted(set(requested))
                stream.watch(keys, renew_group=True)
                if keys:
                    session = await run_in_threadpool(client.get_market_session, keys[0])
            except asyncio.TimeoutError:
                pass
            update = stream.updates(revision)
            changed = bool(set(update["instrument_keys"]) & set(keys))
            if changed or revision < 0 or time.monotonic() - last_sent >= 15:
                if keys and time.monotonic() - last_sent >= 15:
                    session = await run_in_threadpool(client.get_market_session, keys[0])
                update["instrument_keys"] = sorted(set(update["instrument_keys"]) & set(keys))
                update["quotes"] = stream.quotes(keys) if changed else {}
                update["session"] = session
                await websocket.send_json(update)
                last_sent = time.monotonic()
            revision = update["revision"]
    except (WebSocketDisconnect, RuntimeError, ValueError):
        return


@router.get("/candles", response_model=CandleSeries)
async def get_candles(
    instrument_key: str = Query(..., description="e.g. NSE_EQ|INE002A01018"),
    interval: str = Query("1day"),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    force_refresh: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> CandleSeries:
    try:
        rows, source = await market_data.get_candles(
            db,
            instrument_key=instrument_key,
            interval=interval,
            from_date=from_date,
            to_date=to_date,
            force_refresh=force_refresh,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Candle fetch failed: {exc}") from exc
    return CandleSeries(
        instrument_key=instrument_key,
        interval=interval,
        source=source,
        partial=source == "db_partial",
        hint="Showing retained candles; upstream is unavailable and complete range coverage could not be verified." if source == "db_partial" else None,
        count=len(rows),
        candles=[
            {
                "ts": c.ts,
                "open": c.open,
                "high": c.high,
                "low": c.low,
                "close": c.close,
                "volume": c.volume,
                "oi": c.oi,
            }
            for c in rows
        ],
    )


@router.get("/intraday", response_model=CandleSeries)
def get_intraday(
    instrument_key: str,
    interval: str = "1minute",
) -> CandleSeries:
    try:
        rows = upstox_service.fetch_intraday(instrument_key, interval)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Upstox intraday failed: {exc}") from exc
    return CandleSeries(
        instrument_key=instrument_key,
        interval=interval,
        source="stored",
        count=len(rows),
        candles=[
            {
                "ts": c["ts"],
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"],
                "volume": c.get("volume"),
                "oi": c.get("oi"),
            }
            for c in rows
        ],
    )


@router.get("/ltp")
def get_ltp(instrument_keys: str = Query(..., description="Comma-separated keys")):
    keys = [k.strip() for k in instrument_keys.split(",") if k.strip()]
    if not keys:
        raise HTTPException(status_code=400, detail="instrument_keys required")
    try:
        raw = upstox_service.fetch_ltp(keys)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Upstox LTP failed: {exc}") from exc

    # normalize
    out: list[QuoteOut] = []
    if isinstance(raw, dict):
        for key in keys:
            entry = (raw.get(key) or raw.get(key.replace("|", "_")) or raw.get(key.replace("|", ":"))
                     or next((value for value in raw.values() if isinstance(value, dict)
                              and (value.get("instrument_token") == key or value.get("instrument_key") == key)), {}))
            ltp = None
            if isinstance(entry, dict):
                ltp = entry.get("last_price") if entry.get("last_price") is not None else entry.get("ltp")
            elif isinstance(entry, (int, float)):
                ltp = float(entry)
            out.append(QuoteOut(instrument_key=key, ltp=ltp, raw=entry if isinstance(entry, dict) else None))
    return {"quotes": out}


@router.get("/status", response_model=MarketStatusOut)
def market_status(exchange: str = "NSE") -> MarketStatusOut:
    try:
        status = upstox_service.fetch_market_status(exchange)
        return MarketStatusOut(exchange=exchange, status=status, source="upstox")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Upstox status failed: {exc}") from exc


@router.get("/search")
def search(q: str, records: int = 20) -> Any:
    try:
        return upstox_service.search_instruments(q, records=records)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Upstox search failed: {exc}") from exc
