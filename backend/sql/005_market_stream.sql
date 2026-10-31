-- Preserve received market updates and dated chain snapshots. No drop policy.
CREATE TABLE IF NOT EXISTS market_stream_ticks (
    source_at TIMESTAMPTZ NOT NULL,
    instrument_key TEXT NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    feed_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    PRIMARY KEY(source_at,instrument_key,received_at)
);
SELECT create_hypertable('market_stream_ticks','source_at',if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_stream_ticks_key ON market_stream_ticks(instrument_key,source_at DESC);
CREATE TABLE IF NOT EXISTS market_stream_chains (
    observed_at TIMESTAMPTZ NOT NULL,
    underlying_key TEXT NOT NULL,
    expiry DATE NOT NULL,
    session_date DATE NOT NULL,
    payload JSONB NOT NULL,
    provenance JSONB NOT NULL,
    PRIMARY KEY(observed_at,underlying_key,expiry)
);
SELECT create_hypertable('market_stream_chains','observed_at',if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_market_stream_chains_selection ON market_stream_chains(underlying_key,expiry,session_date,observed_at DESC);
