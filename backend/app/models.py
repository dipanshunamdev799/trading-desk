from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    Double,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Instrument(Base):
    __tablename__ = "instruments"

    instrument_key: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    exchange: Mapped[Optional[str]] = mapped_column(String)
    segment: Mapped[Optional[str]] = mapped_column(String)
    instrument_type: Mapped[Optional[str]] = mapped_column(String)
    isin: Mapped[Optional[str]] = mapped_column(String)
    expiry: Mapped[Optional[date]] = mapped_column(Date)
    strike: Mapped[Optional[float]] = mapped_column(Double)
    option_type: Mapped[Optional[str]] = mapped_column(String)
    trading_symbol: Mapped[Optional[str]] = mapped_column(String)
    raw: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Candle(Base):
    __tablename__ = "candles"

    instrument_key: Mapped[str] = mapped_column(String, primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    interval: Mapped[str] = mapped_column(String, primary_key=True)
    open: Mapped[float] = mapped_column(Double)
    high: Mapped[float] = mapped_column(Double)
    low: Mapped[float] = mapped_column(Double)
    close: Mapped[float] = mapped_column(Double)
    volume: Mapped[Optional[float]] = mapped_column(Double)
    oi: Mapped[Optional[float]] = mapped_column(Double)
    source: Mapped[str] = mapped_column(String, server_default="upstox")


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    client_order_id: Mapped[str] = mapped_column(String, unique=True)
    instrument_key: Mapped[str] = mapped_column(String)
    side: Mapped[str] = mapped_column(String)
    order_type: Mapped[str] = mapped_column(String, server_default="MARKET")
    qty: Mapped[float] = mapped_column(Double)
    limit_price: Mapped[Optional[float]] = mapped_column(Double)
    status: Mapped[str] = mapped_column(String, server_default="OPEN")
    filled_qty: Mapped[float] = mapped_column(Double, server_default="0")
    avg_fill_price: Mapped[Optional[float]] = mapped_column(Double)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    notes: Mapped[Optional[str]] = mapped_column(Text)


class PaperFill(Base):
    __tablename__ = "paper_fills"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper_orders.id", ondelete="CASCADE"))
    qty: Mapped[float] = mapped_column(Double)
    price: Mapped[float] = mapped_column(Double)
    filled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fees: Mapped[float] = mapped_column(Double, server_default="0")


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    instrument_key: Mapped[str] = mapped_column(String, primary_key=True)
    qty: Mapped[float] = mapped_column(Double, server_default="0")
    avg_price: Mapped[float] = mapped_column(Double, server_default="0")
    realized_pnl: Mapped[float] = mapped_column(Double, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    strategy: Mapped[Optional[str]] = mapped_column(String)
    instrument_key: Mapped[Optional[str]] = mapped_column(String)
    interval: Mapped[Optional[str]] = mapped_column(String)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    metrics: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    source_path: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
