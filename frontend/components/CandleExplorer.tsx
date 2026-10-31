"use client";

import { useEffect, useState } from "react";
import ChartPanel from "@/components/ChartPanel";
import { SourceBadge } from "@/components/Bits";
import { api, type CandleSeries } from "@/lib/api";
import { useLiveMarket } from "@/lib/liveMarket";
import { mergeLiveCandles } from "@/lib/liveCandles";

const INTERVALS = ["1day", "1week", "1hour", "30minute", "15minute", "5minute", "1minute"];

function defaultLookback(interval: string): number {
  switch (interval) {
    case "1minute":
      return 90;
    case "5minute":
      return 120;
    case "15minute":
      return 180;
    case "30minute":
      return 180;
    case "1hour":
      return 365;
    default:
      return 3650;
  }
}

const PRESETS = [
  { label: "Nifty 50", key: "NSE_INDEX|Nifty 50" },
  { label: "Bank Nifty", key: "NSE_INDEX|Nifty Bank" },
  { label: "RELIANCE", key: "NSE_EQ|INE002A01018" },
  { label: "TCS", key: "NSE_EQ|INE467B01029" },
];

export default function CandleExplorer() {
  const [instrumentKey, setInstrumentKey] = useState(PRESETS[0].key);
  const [debouncedKey, setDebouncedKey] = useState(PRESETS[0].key);
  const [interval, setInterval] = useState("1day");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [forceRefresh, setForceRefresh] = useState(false);
  const [series, setSeries] = useState<CandleSeries | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const live = useLiveMarket([debouncedKey], event => setSeries(previous => {
    if (!previous || previous.instrument_key !== debouncedKey || previous.interval !== interval) return previous;
    const candles = mergeLiveCandles(previous.candles, event.quotes[debouncedKey], interval, fromDate, toDate);
    return { ...previous, candles, count: candles.length };
  }));

  // Debounce free-typed instrument keys so we don't fire on every keystroke.
  useEffect(() => {
    const t = setTimeout(() => setDebouncedKey(instrumentKey.trim()), 400);
    return () => clearTimeout(t);
  }, [instrumentKey]);

  useEffect(() => {
    if (!debouncedKey) return;
    let cancelled = false;
    setLoading(true);
    setError(null);

    (async () => {
      try {
        let from = fromDate;
        if (!from) {
          const days = defaultLookback(interval);
          from = new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
        }
        const data = await api.candles({
          instrument_key: debouncedKey,
          interval,
          from_date: from || undefined,
          to_date: toDate || undefined,
          force_refresh: forceRefresh,
        });
        if (!cancelled) setSeries(data);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load candles");
          setSeries(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [debouncedKey, interval, fromDate, toDate, forceRefresh]);

  return (
    <div className="stack">
      <div className="panel">
        <div className="panel-header">
          <h2>OHLCV explorer</h2>
          <div className="row">
            {loading && <span className="badge warn">loading…</span>}
            {!loading && series && <SourceBadge source={series.source} />}
            {live?.quotes[debouncedKey] && <span className="badge db">Streamed current bars</span>}
          </div>
        </div>
        <div className="panel-body">
          <div className="toolbar">
            <div className="field" style={{ minWidth: 280 }}>
              <label>Instrument key</label>
              <input
                value={instrumentKey}
                onChange={(e) => setInstrumentKey(e.target.value)}
                placeholder="NSE_EQ|INE002A01018"
                spellCheck={false}
              />
            </div>
            <div className="field">
              <label>Interval</label>
              <select value={interval} onChange={(e) => setInterval(e.target.value)}>
                {INTERVALS.map((i) => (
                  <option key={i} value={i}>
                    {i}
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>From</label>
              <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} />
            </div>
            <div className="field">
              <label>To</label>
              <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} />
            </div>
            <div className="field">
              <label>Refresh</label>
              <label className="row" style={{ textTransform: "none", letterSpacing: 0 }}>
                <input
                  type="checkbox"
                  checked={forceRefresh}
                  onChange={(e) => setForceRefresh(e.target.checked)}
                  style={{ minWidth: 0 }}
                />
                force Upstox
              </label>
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Presets</label>
              <div className="row">
                {PRESETS.map((p) => (
                  <button key={p.key} type="button" onClick={() => setInstrumentKey(p.key)}>
                    {p.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {series?.hint && <div className="error-box" role="status">{series.hint}</div>}

      <div className="panel">
        <div className="panel-header">
          <h2>
            {debouncedKey} · {interval}
          </h2>
          <span className="muted mono">
            {series ? `${series.count} bars` : loading ? "loading…" : "—"}
          </span>
        </div>
        <div className="panel-body tight">
          {series && series.candles.length ? (
            <ChartPanel candles={series.candles} height={480} />
          ) : (
            <div className="chart-empty">
              <div>{loading ? "Loading bars…" : "No bars for this range"}</div>
              <div className="muted">
                Data is read from PostgreSQL first, then Upstox on miss, then cached back.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

