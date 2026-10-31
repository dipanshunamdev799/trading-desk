# Trading Desk — Design Spec

Local plug-and-play web app for charting, backtest inspection, and paper trading over the existing Upstox clients.

## Style anchor

Bloomberg Terminal density × Linear dark UI polish. A serious local trading desk: dark canvas, monospaced numbers, thin chrome, chart-first pages. Feels like a product, not a dashboard template.

## Palette

| Role | Hex | Use |
|------|-----|-----|
| Background | `#0B0F14` | App canvas |
| Surface | `#121820` | Cards, panels |
| Surface raised | `#1A2330` | Hover / selected rows |
| Border | `#243041` | 1px hairlines |
| Ink | `#E8EDF2` | Primary text |
| Muted | `#8B9AAB` | Labels, secondary |
| Accent | `#2DD4A8` | CTAs, live/positive, focus |
| Danger | `#F07178` | Down candles, errors, P&L negative |
| Warn | `#E5C07B` | Cache stale, paper mode badges |
| Info | `#61AFEF` | Chart line, links |

## Typography

- UI: `Inter, "Segoe UI", system-ui, sans-serif`
- Numbers/code: `"JetBrains Mono", "Cascadia Code", ui-monospace, monospace`
- Scale: 11 / 12 / 13 / 14 / 18 / 24 / 32. Data tables at 12–13px with tabular-nums.
- Weights: 400 body, 500 labels, 600 headings.

## Layout system

- Left rail 220px (nav + system status). Top bar 48px (page title + data-source badge + actions).
- Content max-width none — trading desks want horizontal room.
- Spacing rhythm: 4 / 8 / 12 / 16 / 24 / 32.
- Density: tight. Tables are the default UI. Cards only for metric strips and chart frames.
- Grid: 12-col for metric strips; full-bleed for charts and tables.

## Signature moments

1. **Live chart canvas** — TradingView-style candles + volume with equity overlay on backtests. Empty state is a calm instrument picker, not a blank box.
2. **Data-source badge** — every market series shows `DB cache` or `Upstox live` so you always know where the bars came from.

## Pages (plug-and-play)

| Route | Purpose |
|-------|---------|
| `/` | Desk overview: market status, recent backtests, paper P&L, quick chart |
| `/charts` | OHLCV explorer — instrument, interval, date range |
| `/backtests` | Scan `backtests/*.json`, equity curve, trade list, metrics |
| `/paper` | Paper orders, positions, fills, simple order ticket |
| `/data` | Instruments, candle coverage, cache controls |

## Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + lightweight-charts
- **Backend**: FastAPI + SQLAlchemy 2 + asyncpg
- **DB**: PostgreSQL 16 + TimescaleDB (hypertable `candles`)
- **Data path**: Postgres first → Upstox Analytics API on miss → upsert back to Postgres
- **Live path**: `upstox_ws_v3.py` reserved for future live tape; REST quotes for now

## Extension points (waiting on requirements)

- `backend/app/services/` — drop new strategies / data sources here
- `backtests/` — drop JSON backtest outputs (schema documented in README)
- `backend/app/routers/` — new API surface with one-line include in `main.py`
- Frontend: one nav entry + one page folder

## Out of scope for v0

- Live order placement (Upstox order APIs need static IP)
- Auth / multi-user
- Real-time WS chart streaming (REST + poll is enough until requirements land)
