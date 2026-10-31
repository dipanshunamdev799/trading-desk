-- Trading desk schema (PostgreSQL + TimescaleDB)

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ---------------------------------------------------------------------------
-- Instruments
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instruments (
    instrument_key   TEXT PRIMARY KEY,
    name             TEXT,
    exchange         TEXT,
    segment          TEXT,
    instrument_type  TEXT,
    isin             TEXT,
    expiry           DATE,
    strike           DOUBLE PRECISION,
    option_type      TEXT,
    trading_symbol   TEXT,
    raw              JSONB,
    fetched_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Candles (hypertable)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candles (
    instrument_key TEXT NOT NULL,
    ts             TIMESTAMPTZ NOT NULL,
    interval       TEXT NOT NULL,
    open           DOUBLE PRECISION NOT NULL,
    high           DOUBLE PRECISION NOT NULL,
    low            DOUBLE PRECISION NOT NULL,
    close          DOUBLE PRECISION NOT NULL,
    volume         DOUBLE PRECISION,
    oi             DOUBLE PRECISION,
    source         TEXT NOT NULL DEFAULT 'upstox',
    PRIMARY KEY (instrument_key, interval, ts)
);

SELECT create_hypertable('candles', 'ts', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_candles_lookup
    ON candles (instrument_key, interval, ts DESC);

-- ---------------------------------------------------------------------------
-- Paper trading
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS paper_orders (
    id              BIGSERIAL PRIMARY KEY,
    client_order_id TEXT UNIQUE NOT NULL,
    instrument_key  TEXT NOT NULL,
    side            TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
    order_type      TEXT NOT NULL DEFAULT 'MARKET',
    qty             DOUBLE PRECISION NOT NULL,
    limit_price     DOUBLE PRECISION,
    status          TEXT NOT NULL DEFAULT 'OPEN',
    filled_qty      DOUBLE PRECISION NOT NULL DEFAULT 0,
    avg_fill_price  DOUBLE PRECISION,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS paper_fills (
    id              BIGSERIAL PRIMARY KEY,
    order_id        BIGINT NOT NULL REFERENCES paper_orders(id) ON DELETE CASCADE,
    qty             DOUBLE PRECISION NOT NULL,
    price           DOUBLE PRECISION NOT NULL,
    filled_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    fees            DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS paper_positions (
    instrument_key  TEXT PRIMARY KEY,
    qty             DOUBLE PRECISION NOT NULL DEFAULT 0,
    avg_price       DOUBLE PRECISION NOT NULL DEFAULT 0,
    realized_pnl    DOUBLE PRECISION NOT NULL DEFAULT 0,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Backtest runs (filesystem JSON is source of truth; this is the cache)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS backtest_runs (
    id              BIGSERIAL PRIMARY KEY,
    slug            TEXT UNIQUE NOT NULL,
    name            TEXT,
    strategy        TEXT,
    instrument_key  TEXT,
    interval        TEXT,
    start_date      DATE,
    end_date        DATE,
    metrics         JSONB,
    source_path     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS backtest_equity (
    run_slug        TEXT NOT NULL,
    ts              TIMESTAMPTZ NOT NULL,
    equity          DOUBLE PRECISION NOT NULL,
    drawdown        DOUBLE PRECISION,
    PRIMARY KEY (run_slug, ts)
);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id              BIGSERIAL PRIMARY KEY,
    run_slug        TEXT NOT NULL,
    entry_ts        TIMESTAMPTZ,
    exit_ts         TIMESTAMPTZ,
    side            TEXT,
    instrument_key  TEXT,
    qty             DOUBLE PRECISION,
    entry_price     DOUBLE PRECISION,
    exit_price      DOUBLE PRECISION,
    pnl             DOUBLE PRECISION,
    fees            DOUBLE PRECISION,
    extras          JSONB
);

-- Continuous aggregate for chart downsampling (optional helper)
CREATE MATERIALIZED VIEW IF NOT EXISTS candles_1h
WITH (timescaledb.continuous) AS
SELECT
    instrument_key,
    interval,
    time_bucket('1 hour', ts) AS ts,
    first(open, ts) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, ts) AS close,
    sum(volume) AS volume,
    last(oi, ts) AS oi
FROM candles
GROUP BY instrument_key, interval, time_bucket('1 hour', ts)
WITH NO DATA;
