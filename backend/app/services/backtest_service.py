from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import BacktestRun


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-").lower()
    return slug or "backtest"


def _parse_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value)[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def discover_backtest_files() -> list[Path]:
    root = get_settings().backtests_dir
    if not root.exists():
        return []
    files = list(root.glob("*.json"))
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def load_backtest_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path.name}: expected a JSON object")
    return data


def normalize_backtest(path: Path, data: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """
    Accept a flexible backtest JSON shape and normalize it.

    Preferred shape:
    {
      "name": "...",
      "strategy": "...",
      "instrument_key": "NSE_EQ|INE002A01018",
      "interval": "1day",
      "start_date": "2023-01-01",
      "end_date": "2024-01-01",
      "metrics": { "total_return": 0.12, "sharpe": 1.2, "max_drawdown": -0.08, ... },
      "equity": [ {"ts": "...", "equity": 100000, "drawdown": 0} ],
      "trades": [ {"entry_ts": "...", "exit_ts": "...", "side": "BUY", ...} ]
    }
    """
    raw = data if data is not None else load_backtest_file(path)
    slug = raw.get("slug") or path.stem

    equity_raw = raw.get("equity") or raw.get("equity_curve") or []
    equity: list[dict[str, Any]] = []
    for point in equity_raw:
        if isinstance(point, dict):
            equity.append(
                {
                    "ts": point.get("ts") or point.get("timestamp") or point.get("date"),
                    "equity": float(point.get("equity") or point.get("value") or 0),
                    "drawdown": float(point["drawdown"]) if point.get("drawdown") is not None else None,
                }
            )
        elif isinstance(point, (list, tuple)) and len(point) >= 2:
            equity.append({"ts": point[0], "equity": float(point[1]), "drawdown": None})

    trades_raw = raw.get("trades") or raw.get("fills") or []
    trades: list[dict[str, Any]] = []
    for t in trades_raw:
        if not isinstance(t, dict):
            continue
        trades.append(
            {
                "entry_ts": t.get("entry_ts") or t.get("entry_time") or t.get("timestamp"),
                "exit_ts": t.get("exit_ts") or t.get("exit_time"),
                "side": t.get("side") or t.get("direction"),
                "instrument_key": t.get("instrument_key") or t.get("symbol"),
                "qty": t.get("qty") or t.get("quantity"),
                "entry_price": t.get("entry_price") or t.get("entry"),
                "exit_price": t.get("exit_price") or t.get("exit"),
                "pnl": t.get("pnl") or t.get("profit"),
                "fees": t.get("fees"),
                "extras": {k: v for k, v in t.items() if k not in {
                    "entry_ts", "entry_time", "timestamp", "exit_ts", "exit_time",
                    "side", "direction", "instrument_key", "symbol", "qty", "quantity",
                    "entry_price", "entry", "exit_price", "exit", "pnl", "profit", "fees",
                }},
            }
        )

    metrics = raw.get("metrics") or {}
    if not isinstance(metrics, dict):
        metrics = {"value": metrics}

    return {
        "slug": slug,
        "name": raw.get("name") or path.stem,
        "strategy": raw.get("strategy"),
        "instrument_key": raw.get("instrument_key") or raw.get("symbol"),
        "interval": raw.get("interval") or raw.get("timeframe"),
        "start_date": _parse_date(raw.get("start_date")),
        "end_date": _parse_date(raw.get("end_date")),
        "metrics": metrics,
        "source_path": str(path),
        "equity": equity,
        "trades": trades,
        "research": raw.get("research") if isinstance(raw.get("research"), dict) else None,
    }


async def sync_backtests_to_db(db: AsyncSession) -> int:
    """Upsert file-system backtests into backtest_runs (equity/trades stay in JSON for v0)."""
    count = 0
    for path in discover_backtest_files():
        try:
            normalized = normalize_backtest(path)
        except Exception:
            continue

        row = (
            await db.execute(select(BacktestRun).where(BacktestRun.slug == normalized["slug"]))
        ).scalar_one_or_none()
        if row is None:
            row = BacktestRun(slug=normalized["slug"])
        row.name = normalized["name"]
        row.strategy = normalized["strategy"]
        row.instrument_key = normalized["instrument_key"]
        row.interval = normalized["interval"]
        row.start_date = normalized["start_date"]
        row.end_date = normalized["end_date"]
        row.metrics = normalized["metrics"]
        row.source_path = normalized["source_path"]
        db.add(row)
        count += 1
    await db.commit()
    return count


async def list_backtests(db: AsyncSession) -> list[dict[str, Any]]:
    await sync_backtests_to_db(db)
    rows = (await db.execute(select(BacktestRun).order_by(BacktestRun.created_at.desc()))).scalars().all()
    out = []
    for r in rows:
        out.append(
            {
                "slug": r.slug,
                "name": r.name,
                "strategy": r.strategy,
                "instrument_key": r.instrument_key,
                "interval": r.interval,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "metrics": r.metrics or {},
                "source_path": r.source_path,
                "created_at": r.created_at,
            }
        )
    return out


def get_backtest_detail(slug: str) -> Optional[dict[str, Any]]:
    root = get_settings().backtests_dir
    # prefer exact file match
    candidates = [root / f"{slug}.json"] + [p for p in discover_backtest_files() if p.stem == slug]
    for path in candidates:
        if path.exists():
            return normalize_backtest(path)
    return None
