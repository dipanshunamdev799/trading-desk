# Trading Desk — Design Spec

Local plug-and-play web app for charting, backtest inspection, and paper trading over the existing Upstox clients.

## Style anchor

A calm research workspace with a clear path from observation to practice. Keep the dark canvas, monospaced market values and mint accents, with more space around introductory content and controls. Data tables remain compact inside specialist tools.

## Navigation and learning

- Overview explains where to begin, followed by real market and paper-account data.
- Learn the desk provides practical exercises, saved local progress, an illustrative P&L calculator and a searchable glossary.
- Group destinations by intent: Start here, Explore markets, Practise & review, Advanced tools. Advanced links expand on demand and open automatically on an advanced route.
- Every tool has a short purpose and an expandable first-use guide with steps and definitions.
- NIFTY defaults to chart and core watch. Full research and question-based links reveal the complete workspace.
- Options expose instrument and expiry first, with historical and secondary selectors behind a disclosure.
- Paper trading starts with familiar instrument names and reviews the order in plain language before submission.
- All routes remain searchable with Ctrl+K. Mobile navigation supports keyboard focus, Escape and focus restoration.
- Keep unavailable values distinct from zero, preserve dates and sources, and label sample results and hypothetical calculations.

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

- Left rail 238px (grouped navigation + expandable connection details). Top bar 70px (location, tool search and guide).
- Content max-width none — trading desks want horizontal room.
- Spacing rhythm: 4 / 8 / 12 / 16 / 24 / 32.
- Density: comfortable for navigation, introductions and forms; compact for specialist data tables. Use cards to give learning choices a clear purpose.
- Grid: 12-col for metric strips; full-bleed for charts and tables.

## Signature moments

1. **Live chart canvas** — TradingView-style candles + volume with equity overlay on backtests. Empty state is a calm instrument picker, not a blank box.
2. **Data-source badge** — every market series shows `DB cache` or `Upstox live` so you always know where the bars came from.

## Pages (plug-and-play)

| Route | Purpose |
|-------|---------|
| `/` | Desk overview: market status, recent backtests, paper P&L, quick chart |
| `/learn` | Guided exercises, saved learning progress, local P&L example and glossary |
| `/nifty` | Index chart and core factors; full research, history, events and OHLCV explorer |
| `/charts` | Redirect to `/nifty` |
| `/maxpain` | Options positioning, volatility, Greeks, hypothetical P&L and history views |
| `/ipos` | IPO universe, issue details, demand and sourced company research |
| `/backtests` | Scan `backtests/*.json`, equity curve, trade list, metrics |
| `/paper` | Paper orders, positions, fills, simple order ticket |
| `/strategies` | Weighted strategy assessments against a shared market snapshot |
| `/trading-bots` | Independent strategy workers, execution controls and journals |
| `/credit-spreads` | Two-leg NIFTY paper spreads, checks and persistent journal |
| `/data` | Instruments, candle coverage, cache controls |

## Stack

- **Frontend**: Next.js 14 (App Router) + TypeScript + lightweight-charts
- **Backend**: FastAPI + SQLAlchemy 2 + asyncpg
- **DB**: PostgreSQL 16 + TimescaleDB (hypertable `candles`)
- **Data path**: Postgres first → Upstox Analytics API on miss → upsert back to Postgres
- **Live path**: shared browser WebSocket subscriptions for supported live fields; saved observations and REST fallback retain their own dates and sources

## Extension points (waiting on requirements)

- `backend/app/services/` — drop new strategies / data sources here
- `backtests/` — drop JSON backtest outputs (schema documented in README)
- `backend/app/routers/` — new API surface with one-line include in `main.py`
- Frontend: one nav entry + one page folder

## Out of scope for v0

- Live order placement (Upstox order APIs need static IP)
- Auth / multi-user
- Guaranteed live coverage for every dataset (provider and session availability vary)
