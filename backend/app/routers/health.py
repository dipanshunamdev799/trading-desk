from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import HealthOut
from ..services.upstox_service import has_token

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthOut)
async def health(db: AsyncSession = Depends(get_db)) -> HealthOut:
    db_state = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        db_state = f"error: {exc.__class__.__name__}"
    return HealthOut(
        ok=db_state == "ok",
        database=db_state,
        upstox_token=has_token(),
    )
