-- Durable market-data read-through storage. No retention/drop policy: preserve data
-- even after the upstream stops serving a contract or observation date.
CREATE TABLE IF NOT EXISTS market_datasets (
    request_key TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    parameters JSONB NOT NULL,
    payload JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ,
    data_present BOOLEAN NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_market_datasets_method ON market_datasets(method);

CREATE TABLE IF NOT EXISTS market_responses (
    recorded_at TIMESTAMPTZ NOT NULL,
    request_key TEXT NOT NULL,
    method TEXT NOT NULL,
    parameters JSONB NOT NULL,
    payload JSONB NOT NULL,
    PRIMARY KEY (recorded_at, request_key)
);
SELECT create_hypertable('market_responses', 'recorded_at', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_responses_lookup ON market_responses(request_key, recorded_at DESC);

CREATE TABLE IF NOT EXISTS candle_coverage (
    instrument_key TEXT NOT NULL,
    interval TEXT NOT NULL,
    day DATE NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL,
    valid_until TIMESTAMPTZ,
    row_count INTEGER NOT NULL,
    PRIMARY KEY (instrument_key, interval, day)
);

CREATE TABLE IF NOT EXISTS option_contracts (
    underlying_key TEXT NOT NULL,
    expiry DATE NOT NULL,
    strike DOUBLE PRECISION NOT NULL,
    option_type TEXT NOT NULL,
    instrument_key TEXT NOT NULL,
    lot_size INTEGER,
    raw JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (underlying_key, expiry, strike, option_type)
);
CREATE INDEX IF NOT EXISTS idx_option_contracts_instrument ON option_contracts(instrument_key, expiry);

CREATE TABLE IF NOT EXISTS max_pain_points (
    instrument_key TEXT NOT NULL,
    expiry DATE NOT NULL,
    bucket_minutes INTEGER NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    max_pain DOUBLE PRECISION,
    spot DOUBLE PRECISION,
    fetched_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (instrument_key, expiry, bucket_minutes, ts)
);
SELECT create_hypertable('max_pain_points', 'ts', if_not_exists => TRUE);
