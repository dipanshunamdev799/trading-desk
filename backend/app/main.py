from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from .config import get_settings
from .routers import backtest, data, health, market, options, paper, ipos, nifty, credit_spreads

settings = get_settings()
settings.backtests_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from .services.upstox_service import get_market_store
    await run_in_threadpool(get_market_store().initialize)
    from .services.upstox_service import get_upstox
    stream = get_upstox().live
    stream.start()
    async def collect_ipos():
        from .services.ipo_service import get_ipo_service
        while True:
            try:
                await run_in_threadpool(get_ipo_service().refresh_all)
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.getLogger(__name__).exception("IPO refresh failed; retained observations remain available")
            await asyncio.sleep(max(60, settings.ipo_refresh_seconds))
    collector = asyncio.create_task(collect_ipos()) if settings.ipo_collector_enabled else None
    async def collect_nifty():
        from .services.nifty_service import get_nifty_service
        while True:
            try:
                await run_in_threadpool(get_nifty_service().refresh)
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.getLogger(__name__).exception("NIFTY refresh failed; retained research remains available")
            await asyncio.sleep(max(60, settings.nifty_refresh_seconds))
    nifty_collector = asyncio.create_task(collect_nifty()) if settings.nifty_collector_enabled else None
    async def monitor_spreads():
        from .services.credit_spreads import get_credit_spreads
        while True:
            try:
                await run_in_threadpool(get_credit_spreads().monitor)
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.getLogger(__name__).exception("Credit spread paper monitor failed; no unpriced fills were made")
            await asyncio.sleep(10)
    spread_monitor = asyncio.create_task(monitor_spreads())
    try:
        yield
    finally:
        await run_in_threadpool(stream.stop)
        for task in (collector, nifty_collector, spread_monitor):
            if not task:
                continue
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await run_in_threadpool(get_market_store().engine.dispose)

app = FastAPI(
    title="Trading Desk API",
    version="0.1.0",
    description="Local plug-and-play API for charts, backtests, and paper trading.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(market.router)
app.include_router(backtest.router)
app.include_router(paper.router)
app.include_router(data.router)
app.include_router(options.router)
app.include_router(ipos.router)
app.include_router(nifty.router)
app.include_router(credit_spreads.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Trading Desk API",
        "docs": "/docs",
        "health": "/health",
    }
