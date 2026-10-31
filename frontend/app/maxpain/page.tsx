"use client";

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import AppShell from "@/components/AppShell";
import EChartPanel from "@/components/EChartPanel";
import SnapshotChartPanel from "@/components/SnapshotChartPanel";
import IntradayMaxPainPanel from "@/components/IntradayMaxPainPanel";
import MaxPainHistory from "@/components/MaxPainHistory";
import HistoricalPremiumCoverage from "@/components/HistoricalPremiumCoverage";
import OptionGreeksPanel from "@/components/OptionGreeksPanel";
import PcrHistoryPanel from "@/components/PcrHistoryPanel";
import IvMetricsPanel from "@/components/IvMetricsPanel";
import { useLiveMarket } from "@/lib/liveMarket";
import {
  fmtInr,
  fmtLevel,
  fmtPoints,
  oiChartOption,
  payoutCurveOption,
  premiumPnlOption,
} from "@/components/maxpainCharts";
import {
  api,
  fmtNum,
  fmtPnl,
  type ExpiryRow,
  type InstrumentHit,
  type MaxPainHistoryPoint,
  type MaxPainSnapshot,
} from "@/lib/api";

const UNDERLYINGS: { label: string; group: string; key: string }[] = [
  { label: "Nifty 50", group: "Index", key: "NSE_INDEX|Nifty 50" },
  { label: "Bank Nifty", group: "Index", key: "NSE_INDEX|Nifty Bank" },
  { label: "Nifty Financial", group: "Index", key: "NSE_INDEX|Nifty Financial Services" },
  { label: "Midcap Nifty", group: "Index", key: "NSE_INDEX|Nifty Midcap 50" },
  { label: "RELIANCE", group: "Stock", key: "NSE_EQ|INE002A01018" },
  { label: "TCS", group: "Stock", key: "NSE_EQ|INE467B01029" },
  { label: "HDFC Bank", group: "Stock", key: "NSE_EQ|INE040A01034" },
  { label: "ICICI Bank", group: "Stock", key: "NSE_EQ|INE090A01021" },
  { label: "INFY", group: "Stock", key: "NSE_EQ|INE009A01021" },
  { label: "SBIN", group: "Stock", key: "NSE_EQ|INE062A01020" },
];

export default function MaxPainPage() {
  return (
    <AppShell title="Max Pain">
      <MaxPainContent />
    </AppShell>
  );
}

function normalizeSearch(raw: unknown): InstrumentHit[] {
  if (Array.isArray(raw)) return raw as InstrumentHit[];
  if (raw && typeof raw === "object" && Array.isArray((raw as { data?: unknown }).data)) {
    return (raw as { data: InstrumentHit[] }).data;
  }
  return [];
}

function MetricCard({
  label,
  value,
  sub,
  tone,
}: {
  label: string;
  value: ReactNode;
  sub?: string;
  tone?: "pos" | "neg" | "warn";
}) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className={`value ${tone ?? ""}`}>{value}</div>
      {sub && (
        <div className="muted" style={{ fontSize: 11, marginTop: 4, lineHeight: 1.35 }}>
          {sub}
        </div>
      )}
    </div>
  );
}

function payoutSnapshotOption(snap: MaxPainSnapshot | null, payoutVis: Parameters<typeof payoutCurveOption>[1]) {
  const curve = snap?.payout_curve;

  if (!curve?.candidates?.length || !snap) return null;
  return payoutCurveOption(
    {
      candidates: curve.candidates,
      call: curve.call_payout,
      put: curve.put_payout,
      total: curve.total_payout,
      maxPain: snap.max_pain,
      spot: snap.spot,
    },
    payoutVis
  );
}

function oiSnapshotOption(snap: MaxPainSnapshot | null, oiMode: "total" | "change" | "pct") {
  const strikes = snap?.strikes ?? [];

  if (!strikes.length || !snap) return null;
  if (oiMode !== "total" && snap.availability?.oi_change) return null;
  return oiChartOption({
    strikes: strikes.map((s) => s.strike),
    callOi: strikes.map((s) => s.call_oi),
    putOi: strikes.map((s) => s.put_oi),
    callPrev: strikes.map((s) => s.call_prev_oi),
    putPrev: strikes.map((s) => s.put_prev_oi),
    mode: oiMode,
    maxPain: snap.max_pain,
    spot: snap.spot,
  });
}

function premiumSnapshotOption(snap: MaxPainSnapshot | null, pnlView: "seller" | "buyer" | "compare") {
  const pp = snap?.premium_pnl;
  const baseSc = pp?.scenarios?.snapshot;

  if (!pp?.scenarios?.snapshot?.candidates?.length) return null;
  const s = pp.scenarios.snapshot;
  const cands = s.candidates;
  const series: {
    name: string;
    color: string;
    values: number[];
    dashed?: boolean;
    primary?: boolean;
  }[] = [];

  if (pnlView === "seller" || pnlView === "compare") {
    if (pnlView === "compare") {
      series.push({ name: "Sell Call", color: "#E06C75", values: s.call_pnl, dashed: true });
      series.push({ name: "Sell Put", color: "#C07070", values: s.put_pnl, dashed: true });
    }
    series.push({
      name: "Seller combined",
      color: "#E5C07B",
      values: s.combined_pnl,
      primary: true,
    });
    if (pnlView === "seller" && pp.scenarios.low_10pct) {
      series.push({
        name: "Seller −10% prem",
        color: "#8B9AAB",
        values: pp.scenarios.low_10pct.combined_pnl,
        dashed: true,
      });
      series.push({
        name: "Seller +10% prem",
        color: "#B8A0E0",
        values: pp.scenarios.high_10pct?.combined_pnl ?? [],
        dashed: true,
      });
    }
  }
  if (pnlView === "buyer" || pnlView === "compare") {
    const bc = s.buyer_combined_pnl ?? [];
    const bcall = s.buyer_call_pnl ?? [];
    const bput = s.buyer_put_pnl ?? [];
    if (pnlView === "compare") {
      series.push({ name: "Buy Call", color: "#2DD4A8", values: bcall, dashed: true });
      series.push({ name: "Buy Put", color: "#3DB88A", values: bput, dashed: true });
    }
    series.push({ name: "Buyer combined", color: "#61AFEF", values: bc, primary: true });
    if (pnlView === "buyer" && pp.scenarios.low_10pct?.buyer_combined_pnl) {
      series.push({
        name: "Buyer −10% prem",
        color: "#8B9AAB",
        values: pp.scenarios.low_10pct.buyer_combined_pnl,
        dashed: true,
      });
      series.push({
        name: "Buyer +10% prem",
        color: "#B8A0E0",
        values: pp.scenarios.high_10pct?.buyer_combined_pnl ?? [],
        dashed: true,
      });
    }
  }

  return premiumPnlOption({
    candidates: cands,
    series,
    maxPain: snap?.max_pain ?? null,
    spot: snap?.spot ?? null,
    extremePrice: baseSc?.min_pnl_price ?? null,
    extremeLabel:
      pnlView === "buyer" ? "Buyer max" : pnlView === "compare" ? "Seller min / Buyer max" : "Seller min",
    breakevens: baseSc?.breakeven_prices ?? [],
  });
}

function MaxPainContent() {
  const todayIso = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
  const [instrumentKey, setInstrumentKey] = useState(UNDERLYINGS[0].key);
  const [instrumentLabel, setInstrumentLabel] = useState(UNDERLYINGS[0].label);
  const [expiries, setExpiries] = useState<ExpiryRow[]>([]);
  const [expiry, setExpiry] = useState("");
  const [customExpiry, setCustomExpiry] = useState("");
  const [asOf, setAsOf] = useState(todayIso);
  const [snapshotView, setSnapshotView] = useState<"latest" | "historical">("latest");
  const [liveRevision, setLiveRevision] = useState(0);
  const [statusFilter, setStatusFilter] = useState<"all" | "live" | "past">("live");
  const [cycleFilter, setCycleFilter] = useState<"all" | "weekly" | "monthly">("all");
  const [oiMode, setOiMode] = useState<"total" | "change" | "pct">("total");
  const [pnlView, setPnlView] = useState<"seller" | "buyer" | "compare">("seller");
  const [payoutVis, setPayoutVis] = useState({
    combined: true,
    call: true,
    put: true,
    maxPain: true,
    spot: true,
  });
  const [snapshotResult, setSnap] = useState<MaxPainSnapshot | null>(null);
  const [historyResult, setHist] = useState<MaxPainHistoryPoint[]>([]);
  const [snapshotSelection, setSnapshotSelection] = useState("");
  const [historySelection, setHistorySelection] = useState("");
  const [loading, setLoading] = useState(false);
  const [histLoading, setHistLoading] = useState(false);
  const [histError, setHistError] = useState<string | null>(null);
  const [refreshId, setRefreshId] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [updatedAt, setUpdatedAt] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<InstrumentHit[]>([]);
  const [searchState, setSearchState] = useState<"idle" | "loading" | "ready" | "error">("idle");
  const [selectedStrike, setSelectedStrike] = useState<number | null>(null);
  const snapshotRequests = useRef(new Map<string, Promise<MaxPainSnapshot>>());

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setHits([]);
      setSearchState("idle");
      return;
    }
    let cancelled = false;
    setSearchState("loading");
    const t = setTimeout(async () => {
      try {
        const raw = await api.searchInstruments(q, 12);
        const list = normalizeSearch(raw).filter((h) =>
          /^(NSE_INDEX|NSE_EQ)\|/.test(h.instrument_key || "")
        );
        if (!cancelled) {
          setHits(list);
          setSearchState("ready");
        }
      } catch {
        if (!cancelled) {
          setHits([]);
          setSearchState("error");
        }
      }
    }, 350);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
  }, [query]);

  useEffect(() => {
    let cancelled = false;
    setExpiry("");
    setExpiries([]);
    setSnap(null);
    setHist([]);
    setError(null);
    (async () => {
      try {
        const rows = await api.expiries(instrumentKey);
        if (cancelled) return;
        setExpiries(rows);
        const today = todayIso;
        const pick =
          rows.find((e) => e.expiry >= today && (e.n_contracts ?? 0) > 0) ||
          rows.find((e) => e.expiry >= today) ||
          rows.find((e) => e.available !== false) ||
          rows[0];
        const p = pick?.expiry || "";
        setExpiry(p);
        // If the best live expiry is monthly, don't hide it behind Weekly filter.
        const row = rows.find((e) => e.expiry === p);
        const cycle = row?.cycle || (row?.weekly ? "weekly" : "monthly");
        if (cycle === "monthly") setCycleFilter((c) => (c === "weekly" ? "all" : c));
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load expiries");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [instrumentKey]);

  const effectiveExpiry = customExpiry || expiry;
  const requestDate = snapshotView === "historical" ? asOf : undefined;
  const selectionKey = `${instrumentKey}|${effectiveExpiry}|${snapshotView}|${requestDate || "latest"}`;
  const snap = snapshotSelection === selectionKey ? snapshotResult : null;
  const dataDate = snapshotView === "latest" ? snap?.as_of : asOf;
  const historyKey = `${selectionKey}|${dataDate || ""}`;
  const hist = historySelection === historyKey ? historyResult : [];
  const historyDays = 30;
  const [sessionResult, setSessionResult] = useState<{ key: string; dates: string[] } | null>(null);
  const [sessionsError, setSessionsError] = useState<string | null>(null);
  const sessionKey = `${instrumentKey}|${effectiveExpiry}`;
  const sessionDates = sessionResult?.key === sessionKey ? sessionResult.dates : [];
  useEffect(() => {
    if (!effectiveExpiry) return;
    let cancelled = false;
    setSessionsError(null);
    api.maxPainSessions({ expiry: effectiveExpiry, instrument_key: instrumentKey }).then(result => {
      if (result.expiry !== effectiveExpiry || result.instrument_key !== instrumentKey) throw new Error("Trading sessions do not match this selection.");
      if (!cancelled) setSessionResult({ key: sessionKey, dates: result.dates });
    }).catch(reason => { if (!cancelled) setSessionsError(reason instanceof Error ? reason.message : "Trading sessions could not be loaded."); });
    return () => { cancelled = true; };
  }, [effectiveExpiry, instrumentKey, sessionKey, refreshId]);
  const liveMarket = useLiveMarket([instrumentKey], () => setLiveRevision(value => value + 1), snapshotView === "latest");
  useEffect(() => {
    if (snapshotView !== "latest") return;
    const refresh = () => { if (document.visibilityState === "visible") setLiveRevision(value => value + 1); };
    const timer = setInterval(refresh, 60_000);
    document.addEventListener("visibilitychange", refresh);
    return () => { clearInterval(timer); document.removeEventListener("visibilitychange", refresh); };
  }, [snapshotView]);

  useEffect(() => {
    if (!effectiveExpiry) {
      setSnap(null);
      setLoading(false);
      setError(null);
      return;
    }
    let cancelled = false;
    if (snapshotSelection !== selectionKey) setSnap(null);
    setLoading(true);
    setError(null);
    // Date controls can emit intermediate selections while a user edits a segment.
    const requestTimer = setTimeout(async () => {
      try {
        let request = snapshotRequests.current.get(selectionKey);
        if (!request) {
          request = api.maxPain({ expiry: effectiveExpiry, as_of: requestDate, instrument_key: instrumentKey, view: snapshotView });
          snapshotRequests.current.set(selectionKey, request);
          const clear = () => snapshotRequests.current.delete(selectionKey);
          request.then(clear, clear);
        }
        const data = await request;
        if (data.expiry !== effectiveExpiry || (requestDate && data.as_of !== requestDate) || data.instrument_key !== instrumentKey || data.view !== snapshotView) {
          throw new Error("The response does not match the selected underlying, expiry and date.");
        }
        if (!cancelled) {
          setSnap(data);
          setSnapshotSelection(selectionKey);
          setUpdatedAt(new Date(data.fetched_at).toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata", hour12: false }));
          if (snapshotSelection !== selectionKey) setSelectedStrike(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load max pain");
          if (snapshotSelection !== selectionKey) setSnap(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(requestTimer);
    };
  }, [effectiveExpiry, requestDate, snapshotView, instrumentKey, refreshId, liveRevision]);

  useEffect(() => {
    if (!effectiveExpiry || !dataDate) {
      setHist([]);
      setHistLoading(false);
      setHistError(null);
      return;
    }
    let cancelled = false;
    setHistLoading(true);
    setHistError(null);
    setHist([]);
    const requestTimer = setTimeout(async () => {
      try {
        const data = await api.maxPainHistory({
          expiry: effectiveExpiry,
          as_of: dataDate,
          history_days: historyDays,
          instrument_key: instrumentKey,
        });
        if (!cancelled) {
          setHist(data.points.filter((point) => point.expiry === effectiveExpiry && point.obs_date <= dataDate));
          setHistorySelection(historyKey);
        }
      } catch (e) {
        if (!cancelled) {
          setHist([]);
          setHistError(e instanceof Error ? e.message : "Failed to load historical snapshots");
        }
      } finally {
        if (!cancelled) setHistLoading(false);
      }
    }, 250);
    return () => {
      cancelled = true;
      clearTimeout(requestTimer);
    };
  }, [effectiveExpiry, dataDate, snapshotView, instrumentKey, historyDays, refreshId]);

  const filteredExpiries = useMemo(() => {
    return expiries
      .filter((e) => {
        const past = Boolean(e.past) || e.expiry < todayIso;
        if (statusFilter === "live" && past) return false;
        if (statusFilter === "past" && !past) return false;
        const cycle = e.cycle || (e.weekly ? "weekly" : "monthly");
        if (cycleFilter !== "all" && cycle !== cycleFilter) return false;
        return true;
      })
      .sort((a, b) => {
        const pa = (Boolean(a.past) || a.expiry < todayIso) ? 1 : 0;
        const pb = (Boolean(b.past) || b.expiry < todayIso) ? 1 : 0;
        if (pa !== pb) return pa - pb;
        return pa === 0 ? a.expiry.localeCompare(b.expiry) : b.expiry.localeCompare(a.expiry);
      });
  }, [expiries, statusFilter, cycleFilter, todayIso]);

  useEffect(() => {
    if (customExpiry || filteredExpiries.some((row) => row.expiry === expiry)) return;
    setExpiry(filteredExpiries[0]?.expiry ?? "");
  }, [filteredExpiries, expiry, customExpiry]);

  const isHistoricalMode = statusFilter === "past" || Boolean(customExpiry);

  const strikes = snap?.strikes ?? [];

  const snapshotChartProps = { snapshot: snap, asOf: dataDate || "", dates: sessionDates, instrumentKey,
    expiry: effectiveExpiry, loading, refreshId };
  const dist = snap?.spot_minus_max_pain;
  const distSub =
    dist == null
      ? undefined
      : dist >= 0
        ? dist === 0 ? "Spot equals Max Pain" : `${fmtLevel(Math.abs(dist))} pts above Max Pain`
        : `${fmtLevel(Math.abs(dist))} pts below Max Pain`;

  return (
    <div className="stack maxpain-page">
      {/* Header */}
      <div className="panel maxpain-filters">
        <div className="panel-header">
          <div className="maxpain-heading">
            <h2>Max Pain <span className="muted">· {instrumentLabel}</span></h2>
            {effectiveExpiry && (
              <span className="badge db">
                Expiry {effectiveExpiry}
              </span>
            )}
            <span className="muted">{snapshotView === "latest" ? "Latest available" : "Historical as of"} · {dataDate || "checking session…"} · IST</span>
          </div>
          <div className="row">
            {loading && <span className="badge warn" role="status">Refreshing…</span>}
            {!loading && snap && (
              <span className={`badge ${snap.data_available === false ? "danger" : "db"}`}>
                {snap.data_available === false ? "No data" : "Snapshot"} · checked{" "}
                {updatedAt ?? "—"} IST
              </span>
            )}
            <button type="button" disabled={loading || histLoading || !effectiveExpiry}
              aria-label="Refresh snapshot and history" onClick={() => setRefreshId((value) => value + 1)}>Refresh</button>
          </div>
        </div>

        {/* Row 1 — main controls */}
        <div className="panel-body">
          <div className="maxpain-controls">
            <div className="field">
              <label htmlFor="maxpain-underlying">Underlying</label>
              <select
                id="maxpain-underlying"
                value={instrumentKey}
                onChange={(e) => {
                  const opt = e.target.selectedOptions[0];
                  setInstrumentKey(e.target.value);
                  setInstrumentLabel(opt?.dataset.label || e.target.value);
                  setQuery("");
                  setHits([]);
                  setCustomExpiry("");
                }}
              >
                <optgroup label="Index">
                  {UNDERLYINGS.filter((u) => u.group === "Index").map((u) => (
                    <option key={u.key} value={u.key} data-label={u.label}>
                      {u.label}
                    </option>
                  ))}
                </optgroup>
                <optgroup label="Stock">
                  {UNDERLYINGS.filter((u) => u.group === "Stock").map((u) => (
                    <option key={u.key} value={u.key} data-label={u.label}>
                      {u.label}
                    </option>
                  ))}
                </optgroup>
                {!UNDERLYINGS.some((u) => u.key === instrumentKey) && (
                  <option value={instrumentKey} data-label={instrumentLabel}>
                    {instrumentLabel}
                  </option>
                )}
              </select>
            </div>

            <div className="field maxpain-search">
              <label htmlFor="maxpain-search">Search underlying</label>
              <input
                id="maxpain-search"
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Name or symbol…"
                spellCheck={false}
              />
              {query.trim().length >= 2 && (
                <div className="maxpain-search-results" aria-label="Instrument search results">
                  {searchState === "loading" ? <div className="muted">Searching…</div>
                    : searchState === "error" ? <div className="neg">Search failed. Try again.</div>
                    : hits.length ? hits.map((hit) => (
                      <button type="button" key={hit.instrument_key} onClick={() => {
                        setInstrumentKey(hit.instrument_key);
                        setInstrumentLabel(hit.trading_symbol || hit.short_name || hit.name || hit.instrument_key);
                        setCustomExpiry("");
                        setQuery("");
                        setHits([]);
                      }}>
                        <span>{hit.trading_symbol || hit.short_name || hit.name || hit.instrument_key}</span>
                        <small className="muted">{hit.name || hit.instrument_key}</small>
                      </button>
                    )) : <div className="muted">No matching instruments.</div>}
                </div>
              )}
            </div>

            <div className="field">
              <label htmlFor="maxpain-expiry">Expiry ({filteredExpiries.length})</label>
              <select
                id="maxpain-expiry"
                disabled={!filteredExpiries.length}
                value={customExpiry ? "" : expiry}
                onChange={(e) => {
                  setCustomExpiry("");
                  setExpiry(e.target.value);
                }}
              >
                <option value="">{filteredExpiries.length ? "Select expiry" : "No matching expiries"}</option>
                {filteredExpiries.map((e) => {
                  const past = Boolean(e.past) || e.expiry < todayIso;
                  return (
                    <option key={e.expiry} value={e.expiry}>
                      {e.expiry} · {e.cycle || (e.weekly ? "weekly" : "monthly")}
                      {past ? (e.available === false ? " · unverified" : " · past") : ""}
                    </option>
                  );
                })}
              </select>
            </div>

            <div className="field">
              <label>Snapshot view</label>
              <div className="maxpain-segmented" role="group" aria-label="Snapshot view">
                <button type="button" aria-pressed={snapshotView === "latest"} className={snapshotView === "latest" ? "primary" : undefined} onClick={() => setSnapshotView("latest")}>Latest available</button>
                <button type="button" aria-pressed={snapshotView === "historical"} className={snapshotView === "historical" ? "primary" : undefined} onClick={() => { setAsOf(dataDate || todayIso); setSnapshotView("historical"); }}>Historical as of</button>
              </div>
            </div>
            <div className="field">
              <label htmlFor="maxpain-asof">As of (IST)</label>
              <select id="maxpain-asof" value={snapshotView === "latest" ? "latest" : asOf}
                onChange={event => {
                  if (event.target.value === "latest") setSnapshotView("latest");
                  else { setAsOf(event.target.value); setSnapshotView("historical"); }
                }}>
                <option value="latest">Latest available{dataDate ? ` · ${dataDate}` : ""}</option>
                {snapshotView === "historical" && !sessionDates.includes(asOf) && <option value={asOf} disabled>{asOf} · {sessionsError ? "sessions unavailable" : "not in loaded sessions"}</option>}
                {sessionDates.map(day => <option key={day} value={day}>{day}</option>)}
              </select>
              {sessionsError && <small className="neg" role="status">{sessionsError}</small>}
            </div>

            <div className="field">
              <label>Expiry status</label>
              <div className="maxpain-segmented" role="group" aria-label="Expiry status">
                {(
                  [
                    ["live", "Current"],
                    ["past", "Historical"],
                    ["all", "All"],
                  ] as const
                ).map(([k, lab]) => (
                  <button
                    key={k}
                    type="button"
                    className={statusFilter === k ? "primary" : undefined}
                    aria-pressed={statusFilter === k}
                    onClick={() => { setStatusFilter(k); if (k === "live") setCustomExpiry(""); }}
                  >
                    {lab}
                  </button>
                ))}
              </div>
            </div>

            <div className="field">
              <label>Cycle</label>
              <div className="maxpain-segmented" role="group" aria-label="Expiry cycle">
                {(
                  [
                    ["weekly", "Weekly"],
                    ["monthly", "Monthly"],
                    ["all", "All"],
                  ] as const
                ).map(([k, lab]) => (
                  <button
                    key={k}
                    type="button"
                    className={cycleFilter === k ? "primary" : undefined}
                    aria-pressed={cycleFilter === k}
                    onClick={() => setCycleFilter(k)}
                  >
                    {lab}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Row 2 — historical */}
          {isHistoricalMode && (
            <div className="toolbar" style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid var(--border)" }}>
              <div className="field">
                <label htmlFor="maxpain-custom-expiry">Custom expiry</label>
                <div className="row">
                  <input
                    id="maxpain-custom-expiry"
                    type="date"
                    value={customExpiry}
                    onChange={(e) => { setCustomExpiry(e.target.value); setSnapshotView("historical"); }}
                    max={todayIso}
                  />
                  {customExpiry && (
                    <button type="button" onClick={() => setCustomExpiry("")}>
                      clear
                    </button>
                  )}
                </div>
              </div>
              <div className="field" style={{ flex: 1, minWidth: 220 }}>
                <label>Data availability</label>
                <div className="mono muted">
                  Exact selected date and expiry · unavailable inputs stay empty
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && <div className="error-box">{error}</div>}
      {snap?.hint && (
        <div className="error-box" role="status">{snap.hint}</div>
      )}

      {/* Metric strip */}
      {snap && (
        <div className="metric-strip maxpain-summary" aria-busy={loading}>
          <MetricCard
            label="Max Pain"
            value={snap.max_pain != null ? fmtNum(snap.max_pain, 0) : "—"}
            sub="Minimum theoretical OI payout"
            tone="pos"
          />
          <MetricCard
            label="Spot"
            value={fmtLevel(snap.spot)}
            sub={`As of ${snap.as_of}`}
          />
          <MetricCard
            label="Spot − Max Pain"
            value={dist != null ? `${fmtPoints(dist)} pts` : "—"}
            sub={distSub}
            tone={dist == null ? undefined : dist >= 0 ? "pos" : "neg"}
          />
          <MetricCard
            label="PCR (OI)"
            value={snap.pcr != null ? fmtNum(snap.pcr, 3) : "—"}
            sub="Put OI ÷ Call OI"
          />
          <MetricCard
            label="Provider Max Pain"
            value={snap.provider_max_pain != null ? fmtNum(Number(snap.provider_max_pain), 0) : "—"}
            sub={snap.provider_max_pain != null && snap.max_pain != null
              ? Number(snap.provider_max_pain) === snap.max_pain ? "Matches calculated Max Pain" : `${fmtPoints(Number(snap.provider_max_pain) - snap.max_pain)} pts vs calculated`
              : "Upstox reference"}
          />
          <MetricCard
            label="Open interest"
            value={<span className="maxpain-oi-totals">
              <span><small>Call</small>{snap.call_oi_total == null ? "—" : `${fmtLevel(snap.call_oi_total / 1e6, 1)}M`}</span>
              <span><small>Put</small>{snap.put_oi_total == null ? "—" : `${fmtLevel(snap.put_oi_total / 1e6, 1)}M`}</span>
            </span>}
            sub={snap.lot_size == null ? "OI in underlying units · lot size unavailable" : `OI in underlying units · lot size ${snap.lot_size}`}
          />
        </div>
      )}

      <PcrHistoryPanel key={`pcr|${historyKey}`} expiry={effectiveExpiry} asOf={dataDate || ""} instrumentKey={instrumentKey}
        dates={sessionDates} instrumentLabel={instrumentLabel} spotObservation={liveMarket?.status.connected && liveMarket.status.fresh ? liveMarket.quotes[instrumentKey] : undefined}
        live={snapshotView === "latest" && Boolean(snap?.market_context?.active)} refreshId={refreshId}
        observation={snap?.pcr_observation} />

      <IvMetricsPanel key={`iv|${historyKey}`} expiry={effectiveExpiry} asOf={dataDate || ""} instrumentKey={instrumentKey}
        instrumentLabel={instrumentLabel} dates={sessionDates}
        live={snapshotView === "latest" && Boolean(snap?.market_context?.active)} refreshId={refreshId} />

      {/* Charts row */}
      <div className="grid-2">
        <SnapshotChartPanel title="Expiry payoff by settlement price" {...snapshotChartProps}>
          {({ snapshot: snap, loading, asOf: chartDate }) => {
            const payoutOpt = payoutSnapshotOption(snap, payoutVis);
            return <>
          <div className="panel-header">
            <h2>
              Expiry payoff by settlement price
              <div className="muted" style={{ fontSize: 11, fontWeight: 400, marginTop: 2 }}>
                Theoretical intrinsic payouts · premiums & costs excluded
              </div>
            <div className="maxpain-caption">As of {chartDate || "—"} IST</div>
            </h2>
            <div className="row" style={{ gap: 6 }}>
              {(
                [
                  ["combined", "Combined", "#E5C07B"],
                  ["call", "Call", "#E06C75"],
                  ["put", "Put", "#61AFEF"],
                  ["maxPain", "Max Pain", "#2DD4A8"],
                  ["spot", "Spot", "#8B9AAB"],
                ] as const
              ).map(([key, label, color]) => {
                const on = payoutVis[key];
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setPayoutVis((v) => ({ ...v, [key]: !v[key] }))}
                    title={`Toggle ${label}`}
                    style={{
                      padding: "3px 8px",
                      fontSize: 11,
                      border: `1px solid ${on ? color : "#243041"}`,
                      color: on ? color : "#8B9AAB",
                      background: on ? "rgba(255,255,255,0.04)" : "transparent",
                      opacity: on ? 1 : 0.55,
                    }}
                  >
                    {label}
                  </button>
                );
              })}
              <span className="muted mono" style={{ marginLeft: 4 }}>
                {snap?.lot_size ? `lot ${snap.lot_size}` : ""}
              </span>
            </div>
          </div>
          <div className="panel-body tight">
            {payoutOpt ? (
              <EChartPanel option={payoutOpt} height={340} />
            ) : (
              <div className="chart-empty" style={{ height: 340 }}>
                {loading ? "Loading dated OI…" : snap?.availability?.payout || "Payout curve unavailable for this selection"}
              </div>
            )}
          </div>
        </>;
          }}
        </SnapshotChartPanel>

        <SnapshotChartPanel title="Strike-wise open interest" {...snapshotChartProps}>
          {({ snapshot: snap, loading, asOf: chartDate }) => {
            const strikes = snap?.strikes ?? []; const oiOpt = oiSnapshotOption(snap, oiMode);
            return <>
          <div className="panel-header">
            <h2>
              Strike-wise open interest
              <div className="muted" style={{ fontSize: 11, fontWeight: 400, marginTop: 2 }}>
                OI in underlying units · Put side mirrored below zero
              </div>
            <div className="maxpain-caption">As of {chartDate || "—"} IST</div>
            </h2>
            <div className="row">
              {(
                [
                  ["total", "Total OI"],
                  ["change", "Δ OI"],
                  ["pct", "Δ %"],
                ] as const
              ).map(([k, lab]) => (
                <button
                  key={k}
                  type="button"
                  className={oiMode === k ? "primary" : undefined}
                  style={{ padding: "3px 8px", fontSize: 11 }}
                  onClick={() => setOiMode(k)}
                >
                  {lab}
                </button>
              ))}
            </div>
          </div>
          <div className="panel-body tight">
            {oiOpt ? (
              <EChartPanel
                option={oiOpt}
                height={340}
                onClick={(p) => {
                  const s = strikes[p.dataIndex];
                  if (s) setSelectedStrike(s.strike);
                }}
              />
            ) : (
              <div className="chart-empty" style={{ height: 340 }}>
                {loading ? "Loading dated OI…" : oiMode !== "total" ? snap?.availability?.oi_change || "OI change unavailable" : snap?.availability?.oi || "No OI rows for this selection"}
              </div>
            )}
          </div>
        </>;
          }}
        </SnapshotChartPanel>
      </div>

      <OptionGreeksPanel chartContext={snapshotChartProps} data={snap?.option_greeks} asOf={dataDate || ""} expiry={effectiveExpiry} feedFresh={liveMarket?.status.fresh}
        loading={loading} selectedStrike={selectedStrike} onSelectStrike={setSelectedStrike} />

      {/* Premium-adjusted hypothetical P&L */}
      <SnapshotChartPanel title="Premium-adjusted hypothetical P&L" {...snapshotChartProps}>
          {({ snapshot: snap, loading, asOf: chartDate }) => {
            const pp = snap?.premium_pnl; const baseSc = pp?.scenarios?.snapshot; const premOpt = premiumSnapshotOption(snap, pnlView);
            return <>
        <div className="panel-header">
          <h2>
            Premium-adjusted hypothetical P&L
            <div className="muted" style={{ fontSize: 11, fontWeight: 400, marginTop: 2 }}>
              Sell Call+Put vs Buy Call+Put · entry premium = {snap?.premium_prices
                ? snap.premium_prices.carried_forward ? `latest traded close on or before ${snap.premium_prices.date}`
                  : `${snap.premium_prices.date} option daily close`
                : "snapshot LTP"} · not actual market-wide
              P&L
            </div>
          <div className="maxpain-caption">As of {chartDate || "—"} IST</div>
            </h2>
          <div className="row">
            {(
              [
                ["seller", "Seller P&L"],
                ["buyer", "Buyer P&L"],
                ["compare", "Compare Both"],
              ] as const
            ).map(([k, lab]) => (
              <button
                key={k}
                type="button"
                className={pnlView === k ? "primary" : undefined}
                style={{ padding: "4px 10px", fontSize: 12 }}
                onClick={() => setPnlView(k)}
              >
                {lab}
              </button>
            ))}
            <span className="badge warn">hypothetical</span>
          </div>
        </div>
        <div className="panel-body">
          {pp?.error && <div className="error-box">{pp.error}</div>}
          <HistoricalPremiumCoverage prices={snap?.premium_prices} />
          {pp?.assumption && (
            <p className="muted" style={{ margin: "0 0 12px", fontSize: 12, lineHeight: 1.5 }}>
              {pp.assumption}{" "}
              {pp.identity && (
                <>
                  Formula: <code className="mono">{pp.identity}</code>. For fixed OI, the minimum
                  P&amp;L price within the plotted range is where theoretical payout is highest — premiums shift the curve
                  vertically (sensitivity ±10%) but do not move that extreme.
                </>
              )}
            </p>
          )}

          {baseSc && (
            <div className="metric-strip" style={{ marginBottom: 12 }}>
              {pnlView !== "buyer" ? (
                <>
                  <MetricCard
                    label="Seller min P&L"
                    value={fmtNum(baseSc.min_pnl_price, 0)}
                    sub="Worst settlement within the plotted price range"
                    tone="warn"
                  />
                  <MetricCard
                    label="Seller min P&L value"
                    value={fmtInr(baseSc.min_pnl_value, true)}
                    sub="Hypothetical short portfolio loss at that settlement"
                    tone="neg"
                  />
                </>
              ) : null}
              {pnlView !== "seller" ? (
                <>
                  <MetricCard
                    label="Buyer max P&L price"
                    value={fmtNum(baseSc.max_buy_pnl_price ?? NaN, 0)}
                    sub="Best settlement within the plotted price range"
                    tone="pos"
                  />
                  <MetricCard
                    label="Buyer max P&L value"
                    value={
                      baseSc.max_buy_pnl_value != null ? fmtInr(baseSc.max_buy_pnl_value, true) : "—"
                    }
                    sub="Hypothetical long portfolio gain at that settlement"
                    tone="pos"
                  />
                </>
              ) : null}
              <MetricCard
                label="P&L at Max Pain"
                value={
                  baseSc.pnl_at_max_pain != null
                    ? fmtInr(
                        pnlView === "buyer"
                          ? -(baseSc.pnl_at_max_pain || 0)
                          : baseSc.pnl_at_max_pain,
                        true
                      )
                    : "—"
                }
                sub={
                  pnlView === "buyer"
                    ? `Buyer PnL if ${instrumentLabel} expires at traditional Max Pain`
                    : `Seller PnL if ${instrumentLabel} expires at traditional Max Pain`
                }
              />
              <MetricCard
                label="Breakevens"
                value={
                  baseSc.breakeven_prices?.length
                    ? baseSc.breakeven_prices.map((b) => fmtLevel(b)).join(", ")
                    : "none"
                }
                sub="Seller PnL = 0 (same levels for buyer)"
              />
              <MetricCard
                label="Premium coverage"
                value={`${baseSc.call_oi_coverage_pct}% / ${baseSc.put_oi_coverage_pct}%`}
                sub="Call / Put OI with usable premiums"
              />
            </div>
          )}

          {premOpt ? (
            <EChartPanel option={premOpt} height={360} />
          ) : (
            <div className="chart-empty" style={{ height: 280 }}>
              {loading ? "Loading snapshot…" : pp?.error ? "Calculation failed" : snap?.availability?.premiums || "No option premiums for this selection"}
            </div>
          )}

          {baseSc && baseSc.warnings.length > 0 && (
            <ul className="muted" style={{ margin: "10px 0 0", paddingLeft: 18, fontSize: 12 }}>
              {baseSc.warnings.map((w) => (
                <li key={w}>{w}</li>
              ))}
            </ul>
          )}
        </div>
      </>;
          }}
        </SnapshotChartPanel>

      {/* Intraday — full width */}
      <IntradayMaxPainPanel key={historyKey} expiry={effectiveExpiry} asOf={dataDate || todayIso}
        instrumentKey={instrumentKey} dates={sessionDates} refreshId={refreshId} />

      {/* Historical snapshots */}
      <MaxPainHistory points={hist} loading={histLoading} error={histError} asOf={dataDate || todayIso} />

      {/* Strike detail */}
      {selectedStrike != null && snap && (
        <div className="panel">
          <div className="panel-header">
            <h2>Strike {selectedStrike.toLocaleString("en-IN")}</h2>
            <button type="button" onClick={() => setSelectedStrike(null)}>
              close
            </button>
          </div>
          <div className="panel-body">
            {(() => {
              const s = strikes.find((x) => x.strike === selectedStrike);
              if (!s) return <div className="muted">Strike not in current chain.</div>;
              return (
                <div className="metric-strip">
                  <MetricCard label="Call OI" value={fmtNum(s.call_oi, 0)} sub="Underlying units" />
                  <MetricCard label="Put OI" value={fmtNum(s.put_oi, 0)} sub="Underlying units" />
                  <MetricCard label={snap.premium_prices ? "Call traded close" : "Call LTP"}
                    value={fmtNum(s.call_ltp)} sub={snap.premium_prices
                      ? s.call_premium_date ? `Price date · ${s.call_premium_date}${s.call_premium_date !== snap.as_of ? " · carried forward" : ""}` : "Price unavailable"
                      : `Premium · ${snap.as_of}`} />
                  <MetricCard label={snap.premium_prices ? "Put traded close" : "Put LTP"}
                    value={fmtNum(s.put_ltp)} sub={snap.premium_prices
                      ? s.put_premium_date ? `Price date · ${s.put_premium_date}${s.put_premium_date !== snap.as_of ? " · carried forward" : ""}` : "Price unavailable"
                      : `Premium · ${snap.as_of}`} />
                  <MetricCard
                    label="Δ Call OI"
                    value={s.call_prev_oi == null ? "—" : fmtPnl(s.call_oi - s.call_prev_oi)}
                    sub="vs previous trading session close"
                  />
                  <MetricCard
                    label="Δ Put OI"
                    value={s.put_prev_oi == null ? "—" : fmtPnl(s.put_oi - s.put_prev_oi)}
                    sub="vs previous trading session close"
                  />
                  <MetricCard
                    label="Distance from spot"
                    value={
                      snap.spot != null ? fmtPnl(s.strike - snap.spot) : "—"
                    }
                    sub="Strike − spot"
                  />
                  <MetricCard
                    label="Max Pain?"
                    value={s.strike === snap.max_pain ? "Yes" : "No"}
                    sub={s.strike === snap.max_pain ? "This strike" : "Not this strike"}
                    tone={s.strike === snap.max_pain ? "pos" : undefined}
                  />
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* click helper */}
      <div className="muted" style={{ fontSize: 11, textAlign: "center" }}>
        Hover charts for tooltips · click the OI chart to inspect a strike · Max Pain is a
        theoretical OI payout minimum, not a settlement forecast.
      </div>
    </div>
  );
}
