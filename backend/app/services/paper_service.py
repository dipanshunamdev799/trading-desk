from __future__ import annotations

import uuid
import math
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from ..models import Candle, PaperFill, PaperOrder, PaperPosition
from ..schemas import PaperOrderIn
from . import upstox_service


async def _mark_price(db: AsyncSession, instrument_key: str) -> float:
    """Best-effort mark: last candle close, else Upstox LTP, else 0."""
    # Valuation must not backfill ten years of history for every position.
    close = await db.scalar(select(Candle.close).where(
        Candle.instrument_key == instrument_key,
        Candle.interval == "1day",
        Candle.close > 0,
    ).order_by(Candle.ts.desc()).limit(1))
    if close is not None and math.isfinite(close):
        return float(close)
    try:
        quotes = await run_in_threadpool(upstox_service.fetch_ltp, [instrument_key])
        if isinstance(quotes, dict):
            # response keyed by instrument key
            entry = (quotes.get(instrument_key) or quotes.get(instrument_key.replace("|", "_"))
                     or quotes.get(instrument_key.replace("|", ":"))
                     or next((item for item in quotes.values() if isinstance(item, dict)
                              and (item.get("instrument_token") == instrument_key
                                   or item.get("instrument_key") == instrument_key)), None))
            if isinstance(entry, dict):
                return float(entry.get("last_price") or entry.get("ltp") or 0)
            if isinstance(entry, (int, float)):
                return float(entry)
    except Exception:
        pass
    return 0.0


async def place_order(db: AsyncSession, payload: PaperOrderIn) -> PaperOrder:
    mark = payload.limit_price if payload.limit_price is not None else await _mark_price(
        db, payload.instrument_key
    )
    if not math.isfinite(mark) or mark <= 0:
        raise ValueError("No valid price is available for this instrument. The paper order was not filled.")

    order = PaperOrder(
        client_order_id=uuid.uuid4().hex[:12],
        instrument_key=payload.instrument_key,
        side=payload.side,
        order_type=payload.order_type,
        qty=payload.qty,
        limit_price=payload.limit_price,
        status="FILLED",
        filled_qty=payload.qty,
        avg_fill_price=mark,
        notes=payload.notes,
    )
    db.add(order)
    await db.flush()

    db.add(PaperFill(order_id=order.id, qty=payload.qty, price=mark, fees=0.0))
    await _apply_fill_to_position(db, payload.instrument_key, payload.side, payload.qty, mark)
    await db.commit()
    await db.refresh(order)
    return order


async def _apply_fill_to_position(
    db: AsyncSession,
    instrument_key: str,
    side: str,
    qty: float,
    price: float,
) -> None:
    pos = await db.get(PaperPosition, instrument_key)
    if pos is None:
        pos = PaperPosition(instrument_key=instrument_key, qty=0.0, avg_price=0.0, realized_pnl=0.0)
        db.add(pos)

    signed = qty if side == "BUY" else -qty
    new_qty = pos.qty + signed

    if pos.qty == 0 or (pos.qty > 0 and signed > 0) or (pos.qty < 0 and signed < 0):
        # increase / open
        total_cost = pos.avg_price * abs(pos.qty) + price * abs(signed)
        pos.avg_price = total_cost / abs(new_qty) if new_qty != 0 else 0.0
    else:
        # reduce / flip
        closed = min(abs(signed), abs(pos.qty))
        direction = 1 if pos.qty > 0 else -1
        pos.realized_pnl += (price - pos.avg_price) * closed * direction
        if new_qty == 0:
            pos.avg_price = 0.0
        elif (pos.qty > 0 and new_qty < 0) or (pos.qty < 0 and new_qty > 0):
            pos.avg_price = price

    pos.qty = new_qty
    pos.updated_at = datetime.now(timezone.utc)


async def list_orders(db: AsyncSession, limit: int = 100) -> list[PaperOrder]:
    stmt = select(PaperOrder).order_by(PaperOrder.created_at.desc()).limit(limit)
    return list((await db.execute(stmt)).scalars().all())


async def list_positions(db: AsyncSession) -> list[PaperPosition]:
    stmt = select(PaperPosition).order_by(PaperPosition.instrument_key)
    return list((await db.execute(stmt)).scalars().all())


async def portfolio_summary(db: AsyncSession) -> dict[str, Any]:
    positions = await list_positions(db)
    realized = sum(p.realized_pnl for p in positions)
    unrealized = 0.0
    details = []
    for p in positions:
        mark = p.avg_price
        if p.qty != 0:
            try:
                mark = await _mark_price(db, p.instrument_key) or p.avg_price
            except Exception:
                mark = p.avg_price
        upnl = (mark - p.avg_price) * p.qty if p.qty else 0.0
        unrealized += upnl
        details.append(
            {
                "instrument_key": p.instrument_key,
                "qty": p.qty,
                "avg_price": p.avg_price,
                "mark": mark,
                "unrealized_pnl": upnl,
                "realized_pnl": p.realized_pnl,
            }
        )
    return {
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": realized + unrealized,
        "open_positions": len([p for p in positions if p.qty != 0]),
        "positions": details,
    }
