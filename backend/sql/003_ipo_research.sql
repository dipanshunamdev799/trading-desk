-- Preserve IPO identities, research and every observed demand/GMP data point.
CREATE TABLE IF NOT EXISTS ipo_companies (
    id TEXT PRIMARY KEY,
    payload JSONB NOT NULL,
    source TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS ipo_research (
    ipo_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    source_url TEXT NOT NULL,
    payload JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (ipo_id, kind)
);
CREATE TABLE IF NOT EXISTS ipo_observations (
    observed_at TIMESTAMPTZ NOT NULL,
    ipo_id TEXT NOT NULL,
    source TEXT NOT NULL,
    metric TEXT NOT NULL,
    value DOUBLE PRECISION,
    reported_at TIMESTAMPTZ,
    payload JSONB NOT NULL,
    PRIMARY KEY (observed_at, ipo_id, source, metric)
);
SELECT create_hypertable('ipo_observations', 'observed_at', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS idx_ipo_observations_history ON ipo_observations(ipo_id, metric, observed_at DESC);
CREATE TABLE IF NOT EXISTS ipo_sync_state (
    source TEXT PRIMARY KEY,
    attempted_at TIMESTAMPTZ NOT NULL,
    succeeded_at TIMESTAMPTZ,
    error TEXT
);
CREATE TABLE IF NOT EXISTS ipo_feeds (
    name TEXT PRIMARY KEY,
    ipo_ids JSONB NOT NULL,
    checked_at TIMESTAMPTZ NOT NULL
);
