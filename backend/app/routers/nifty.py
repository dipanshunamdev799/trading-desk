"""Research-only endpoints. Imported observations must identify their source."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ..db import get_db
from ..services import market_data, price_action

from ..services.nifty_catalog import FACTORS, FACTOR_MAP, SECTIONS
from ..services.nifty_service import get_nifty_service, utc_now

router = APIRouter(prefix="/nifty", tags=["NIFTY research"])


@router.get("/price-action")
async def price_action_chart(
    instrument_key: str = "NSE_INDEX|Nifty 50", interval: str = "5minute",
    from_date: str | None = None, to_date: str | None = None,
    session: str | None = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    orb_minutes: int = Query(15, ge=5, le=30), round_step: int = Query(100, ge=10, le=1000),
    db: AsyncSession = Depends(get_db),
):
    if orb_minutes not in (5, 15, 30):
        raise HTTPException(400, "Opening range must be 5, 15 or 30 minutes")
    if interval not in (*price_action.MINUTES, "1day", "1week"):
        raise HTTPException(400, "Unsupported price-action timeframe")
    if session:
        try:
            datetime.fromisoformat(session)
        except ValueError as exc:
            raise HTTPException(400, "Invalid study session") from exc
    try:
        rows, source = await market_data.get_candles(db, instrument_key, interval, from_date, to_date)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"Candle history unavailable: {exc}") from exc
    def serialize(row):
        return {"ts": row.ts.isoformat(), "open": row.open, "high": row.high, "low": row.low,
                "close": row.close, "volume": row.volume, "oi": row.oi}
    candles = [serialize(row) for row in rows]
    daily, daily_error = [], None
    selected = session or (max(row.ts for row in rows).astimezone(price_action.IST).date().isoformat() if rows else None)
    if selected and interval in price_action.MINUTES:
        anchor = datetime.fromisoformat(selected)
        try:
            daily_rows, _ = await market_data.get_candles(db, instrument_key, "1day",
                (anchor-timedelta(days=30)).date().isoformat(), (anchor-timedelta(days=1)).date().isoformat())
            daily = [serialize(row) for row in daily_rows]
        except Exception:
            daily_error = "Daily reference data unavailable; intraday patterns can still be inspected."
    study = await run_in_threadpool(price_action.analyze, candles, interval, daily=daily, session=session,
                                    orb_minutes=orb_minutes, round_step=round_step)
    if daily_error:
        study["notes"].append(daily_error)
    return {"instrument_key": instrument_key, "interval": interval, "source": source,
            "partial": source == "db_partial", "count": len(candles), "candles": candles, "study": study,
            "hint": "Retained candles; full coverage could not be verified." if source == "db_partial" else None}


class ObservationInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    factor_id: str
    value: Any
    reported_at: datetime
    source: str = Field(min_length=1, max_length=200)
    source_url: HttpUrl
    unit: str | None = Field(default=None, max_length=80)
    context: str | dict | list | None = None

    @field_validator("factor_id")
    @classmethod
    def known_factor(cls, value):
        if value not in FACTOR_MAP:
            raise ValueError("Unknown factor_id; use GET /nifty/catalog")
        return value

    @field_validator("value")
    @classmethod
    def finite_value(cls, value):
        if value is None or value == "" or value == [] or value == {} or isinstance(value, bool):
            raise ValueError("Provide a published value; do not import a missing reading")
        try:
            payload = json.dumps(value, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("Value must be finite JSON") from exc
        if len(payload) > 100000:
            raise ValueError("Observation exceeds 100 KB")
        return value

    @field_validator("context")
    @classmethod
    def finite_context(cls, value):
        try:
            payload = json.dumps(value, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("Context must be finite JSON") from exc
        if len(payload) > 100000:
            raise ValueError("Context exceeds 100 KB")
        return value

    @field_validator("reported_at")
    @classmethod
    def published_time(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("reported_at must include a timezone")
        if value > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("A published observation cannot have a future timestamp; use events for scheduled releases")
        return value


class ObservationBatch(BaseModel):
    observations: list[ObservationInput] = Field(min_length=1, max_length=500)


class EventInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    id: str = Field(min_length=1, max_length=200, pattern=r"^[A-Za-z0-9_.:-]+$")
    title: str = Field(min_length=1, max_length=500)
    event_at: datetime
    source: str = Field(min_length=1, max_length=200)
    source_url: HttpUrl
    category: str = Field(default="economic", max_length=80)
    impact: str | None = Field(default=None, max_length=80)
    actual: str | float | None = None
    forecast: str | float | None = None
    previous: str | float | None = None

    @field_validator("event_at")
    @classmethod
    def aware_time(cls, value):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("event_at must include a timezone")
        return value


class EventBatch(BaseModel):
    events: list[EventInput] = Field(min_length=1, max_length=500)


@router.get("/catalog")
def catalog():
    return {"sections": SECTIONS, "factors": FACTORS, "total": len(FACTORS)}


@router.get("/dashboard")
def dashboard():
    return get_nifty_service().dashboard()


@router.post("/refresh", status_code=202)
def refresh():
    return {"status": get_nifty_service().request_refresh()}


@router.get("/factors/{factor_id}/history")
def history(factor_id: str, limit: int = Query(365, ge=1, le=2000)):
    try:
        return get_nifty_service().history(factor_id, limit)
    except KeyError as exc:
        raise HTTPException(404, "Unknown factor") from exc


@router.get("/correlations")
def correlations(factor_id: str = "sp500"):
    try:
        return get_nifty_service().correlations(factor_id)
    except KeyError as exc:
        raise HTTPException(404, "Unknown factor") from exc


@router.post("/observations")
def import_observations(batch: ObservationBatch):
    observed_at = utc_now()
    rows = [{**item.model_dump(mode="json", exclude_none=True), "observed_at": observed_at,
             "unit": item.unit or FACTOR_MAP[item.factor_id].get("unit", ""),
             "basis": "Sourced research import; publisher time and import time are separate"} for item in batch.observations]
    return {"observations_saved": get_nifty_service().repo.save_observations(rows)}


@router.post("/events")
def import_events(batch: EventBatch):
    return {"events_saved": get_nifty_service().repo.save_events([row.model_dump(mode="json", exclude_none=True) for row in batch.events])}
