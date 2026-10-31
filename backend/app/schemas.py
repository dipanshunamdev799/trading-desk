from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CandleOut(BaseModel):
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    oi: Optional[float] = None


class CandleSeries(BaseModel):
    instrument_key: str
    interval: str
    source: str  # "db" | "upstox" | "mixed"
    count: int
    candles: list[CandleOut]
    partial: bool = False
    hint: Optional[str] = None


class InstrumentOut(BaseModel):
    instrument_key: str
    name: Optional[str] = None
    exchange: Optional[str] = None
    segment: Optional[str] = None
    instrument_type: Optional[str] = None
    isin: Optional[str] = None
    trading_symbol: Optional[str] = None
    expiry: Optional[date] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None

    model_config = {"from_attributes": True}


class QuoteOut(BaseModel):
    instrument_key: str
    ltp: Optional[float] = None
    close: Optional[float] = None
    ohlc: Optional[dict[str, float]] = None
    volume: Optional[float] = None
    raw: Optional[dict[str, Any]] = None


class MarketStatusOut(BaseModel):
    exchange: str
    status: Any
    source: str


class PaperOrderIn(BaseModel):
    instrument_key: str
    side: str = Field(pattern="^(BUY|SELL)$")
    qty: float = Field(gt=0)
    order_type: str = "MARKET"
    limit_price: Optional[float] = None
    notes: Optional[str] = None


class PaperOrderOut(BaseModel):
    id: int
    client_order_id: str
    instrument_key: str
    side: str
    order_type: str
    qty: float
    limit_price: Optional[float] = None
    status: str
    filled_qty: float
    avg_fill_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class PaperPositionOut(BaseModel):
    instrument_key: str
    qty: float
    avg_price: float
    realized_pnl: float
    updated_at: datetime

    model_config = {"from_attributes": True}


class BacktestSummary(BaseModel):
    slug: str
    name: Optional[str] = None
    strategy: Optional[str] = None
    instrument_key: Optional[str] = None
    interval: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    source_path: Optional[str] = None
    created_at: Optional[datetime] = None


class BacktestDetail(BacktestSummary):
    equity: list[dict[str, Any]] = Field(default_factory=list)
    trades: list[dict[str, Any]] = Field(default_factory=list)
    research: Optional[dict[str, Any]] = None


class HealthOut(BaseModel):
    ok: bool
    database: str
    upstox_token: bool
    version: str = "0.1.0"
