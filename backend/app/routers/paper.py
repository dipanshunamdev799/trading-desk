from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import PaperOrderIn, PaperOrderOut, PaperPositionOut
from ..services import paper_service

router = APIRouter(prefix="/paper", tags=["paper"])


@router.get("/orders", response_model=list[PaperOrderOut])
async def list_orders(db: AsyncSession = Depends(get_db)):
    return await paper_service.list_orders(db)


@router.post("/orders", response_model=PaperOrderOut)
async def place_order(payload: PaperOrderIn, db: AsyncSession = Depends(get_db)):
    return await paper_service.place_order(db, payload)


@router.get("/positions", response_model=list[PaperPositionOut])
async def list_positions(db: AsyncSession = Depends(get_db)):
    return await paper_service.list_positions(db)


@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    return await paper_service.portfolio_summary(db)
