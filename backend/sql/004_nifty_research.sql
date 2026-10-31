-- Research snapshots retain source timestamps, provenance and corrections.
-- A stable content key makes repeated collection of the same publisher snapshot
-- idempotent; different values for an existing source timestamp remain revisions.
CREATE TABLE IF NOT EXISTS nifty_observations (
    observation_key TEXT PRIMARY KEY,
    factor_id TEXT NOT NULL,
    source TEXT NOT NULL,
    reported_at TIMESTAMPTZ,
    observed_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nifty_observation_history
    ON nifty_observations(factor_id, reported_at DESC NULLS LAST, observed_at DESC);
CREATE TABLE IF NOT EXISTS nifty_research_state (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),
    payload JSONB NOT NULL,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS nifty_research_events (
    event_key TEXT PRIMARY KEY,
    event_at TIMESTAMPTZ,
    observed_at TIMESTAMPTZ NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nifty_event_calendar
    ON nifty_research_events(event_at DESC NULLS LAST);
