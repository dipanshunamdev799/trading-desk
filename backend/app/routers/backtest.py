from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import BacktestDetail, BacktestSummary
from ..services import backtest_service

router = APIRouter(prefix="/backtests", tags=["backtests"])


@router.get("", response_model=list[BacktestSummary])
async def list_backtests(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    return await backtest_service.list_backtests(db)


@router.post("/sync")
async def sync_backtests(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    count = await backtest_service.sync_backtests_to_db(db)
    return {"synced": count}


@router.get("/{slug}", response_model=BacktestDetail)
async def get_backtest(slug: str) -> BacktestDetail:
    detail = backtest_service.get_backtest_detail(slug)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Backtest '{slug}' not found")
    return BacktestDetail(**detail)


@router.get("/{slug}/equity")
async def get_equity(slug: str) -> dict[str, Any]:
    detail = backtest_service.get_backtest_detail(slug)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Backtest '{slug}' not found")
    return {"slug": slug, "equity": detail.get("equity", [])}
