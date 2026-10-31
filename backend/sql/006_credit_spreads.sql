CREATE TABLE IF NOT EXISTS credit_spread_account (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    settings JSONB NOT NULL,
    monitor_at TIMESTAMPTZ,
    monitor_error TEXT
);
INSERT INTO credit_spread_account(id, settings) VALUES (1,
 '{"capital":1000000,"fee_per_leg":25,"slippage":0.05,"auto_exit":true}')
ON CONFLICT (id) DO NOTHING;

CREATE TABLE IF NOT EXISTS credit_spread_trades (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('OPEN','CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS credit_spread_orders (
    id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    trade_id TEXT REFERENCES credit_spread_trades(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    payload JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS credit_spread_marks (
    trade_id TEXT NOT NULL REFERENCES credit_spread_trades(id),
    quote_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL,
    PRIMARY KEY(trade_id, quote_at)
);
CREATE INDEX IF NOT EXISTS credit_spread_trade_state ON credit_spread_trades(status);
