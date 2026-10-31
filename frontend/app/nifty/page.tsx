"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useLiveMarket } from "@/lib/liveMarket";
import AppShell from "@/components/AppShell";
import CandleExplorer from "@/components/CandleExplorer";
import PriceActionChart from "@/components/PriceActionChart";
import EChartPanel, { type EChartsOption } from "@/components/EChartPanel";
import ExpandableChartPanel from "@/components/ExpandableChartPanel";
import NiftyFactorCard, { CashFlowDetails, FactorChange, FactorValue, factorReportLabel, factorStatusLabel, niftyDate, niftyLink, niftyNumber } from "@/components/NiftyFactorCard";
import { startMinutePolling } from "@/lib/minutePolling";
import { niftyApi, type NiftyCorrelation, type NiftyDashboard, type NiftyFactor, type NiftyHistory } from "@/lib/niftyApi";
import "./nifty.css";

const PRIORITIES = [["all", "All priorities"], ["P1", "P1 · Core"], ["P2", "P2 · Confirmation"], ["P3", "P3 · Context"], ["P4", "P4 · Advanced"]];
const CORE_IDS = ["nifty_spot", "gift_nifty", "sp500", "india_vix", "usdinr", "brent", "fii_cash", "dii_cash"];
const emptyOption: EChartsOption = {};
const chartColors = { text: "#8B9AAB", grid: "#243041", background: "#121820" };

function numberValue(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function snapshotExpiry(factor: NiftyFactor | undefined): string | null {
  if (factor?.expiry) return factor.expiry;
  if (factor?.context != null && typeof factor.context === "object" && !Array.isArray(factor.context)) {
    const context = factor.context as Record<string, unknown>;
    const value = context.expiry ?? context.expiry_date;
    if (typeof value === "string") return value;
  }
  return null;
}

function expiryLabel(value: string | null): string {
  if (!value) return "Not supplied";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric" }).format(date);
}

function OiSnapshotEvidence({ factor, label }: { factor: NiftyFactor | undefined; label: string }) {
  return <div className="nifty-oi-snapshot"><strong>{label}</strong><span>Expiry: {expiryLabel(snapshotExpiry(factor))}</span><span>{factor?.reported_at ? `Published ${niftyDate(factor.reported_at)} IST` : "Publisher time unavailable"}</span><span>Collected: {niftyDate(factor?.observed_at)}{factor?.observed_at ? " IST" : ""}</span></div>;
}

function historyOption(factor: NiftyFactor | undefined, history: NiftyHistory | null): EChartsOption {
  const revisions = new Map<string, NonNullable<NiftyHistory>["observations"][number]>();
  for (const row of history?.observations || []) {
    const key = JSON.stringify([row.source, row.unit || "", row.reported_at]);
    const previous = revisions.get(key);
    if (!previous || Date.parse(row.observed_at) >= Date.parse(previous.observed_at)) revisions.set(key, row);
  }
  const saved = Array.from(revisions.values()).filter(row => !row.quality_note && numberValue(row.value) != null && (!factor?.source || row.source === factor.source) && (!row.unit || row.unit === factor?.unit));
  const points = history ? saved.map(row => ({ ts: row.reported_at || row.observed_at, value: row.value as number })) : factor?.history || [];
  if (!points.length) return emptyOption;
  const sorted = Array.from(new Map(points.map(point => [point.ts, point])).values()).sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts));
  return { animation: false, backgroundColor: "transparent", grid: { top: 30, left: 78, right: 28, bottom: 64 },
    tooltip: { trigger: "axis", confine: true, backgroundColor: chartColors.background, borderColor: chartColors.grid, textStyle: { color: "#E8EDF2" }, valueFormatter: value => `${niftyNumber(value)} ${factor?.unit || ""}` },
    xAxis: { type: "category", data: sorted.map(row => niftyDate(row.ts, true)), boundaryGap: false, axisLabel: { color: chartColors.text, hideOverlap: true } },
    yAxis: { type: "value", scale: true, name: factor?.unit, nameTextStyle: { color: chartColors.text }, axisLabel: { color: chartColors.text }, splitLine: { lineStyle: { color: chartColors.grid } } },
    dataZoom: [{ type: "inside" }, { type: "slider", bottom: 8, height: 18, borderColor: chartColors.grid, textStyle: { color: chartColors.text } }],
    series: [{ name: factor?.label, type: "line", data: sorted.map(row => row.value), connectNulls: false, symbolSize: 5, showSymbol: sorted.length < 35,
      itemStyle: { color: "#2DD4A8" }, lineStyle: { width: 2 }, areaStyle: { color: "rgba(45,212,168,0.07)" } }],
  };
}

function oiRows(factor: NiftyFactor | undefined): Record<string, unknown>[] {
  if (factor?.strikes?.length) return factor.strikes;
  if (Array.isArray(factor?.value)) return factor.value as Record<string, unknown>[];
  if (factor?.value && typeof factor.value === "object" && "strikes" in factor.value && Array.isArray(factor.value.strikes)) return factor.value.strikes;
  return [];
}

function oiOption(factors: NiftyFactor[]): { option: EChartsOption; count: number } {
  const calls = oiRows(factors.find(factor => factor.id === "call_oi"));
  const puts = oiRows(factors.find(factor => factor.id === "put_oi"));
  const parse = (rows: Record<string, unknown>[]) => new Map(rows.flatMap(row => {
    const strike = numberValue(row.strike ?? row.strike_price);
    const oi = numberValue(row.open_interest ?? row.oi);
    return strike == null || oi == null ? [] : [[strike, oi] as const];
  }));
  const callMap = parse(calls); const putMap = parse(puts);
  const strikes = Array.from(new Set([...callMap.keys(), ...putMap.keys()])).sort((a, b) => a - b);
  return { count: strikes.length, option: {
    animation: false, backgroundColor: "transparent", grid: { left: 76, right: 24, top: 50, bottom: 65 },
    legend: { top: 4, textStyle: { color: chartColors.text } },
    tooltip: { trigger: "axis", confine: true, backgroundColor: chartColors.background, borderColor: chartColors.grid, textStyle: { color: "#E8EDF2" } },
    xAxis: { type: "category", data: strikes, axisLabel: { color: chartColors.text, hideOverlap: true, rotate: 35 } },
    yAxis: { type: "value", name: "Open interest", nameTextStyle: { color: chartColors.text }, axisLabel: { color: chartColors.text }, splitLine: { lineStyle: { color: chartColors.grid } } },
    dataZoom: [{ type: "inside" }], series: [
      { name: "Call OI", type: "bar", data: strikes.map(strike => callMap.get(strike) ?? null), itemStyle: { color: "#F07178" } },
      { name: "Put OI", type: "bar", data: strikes.map(strike => putMap.get(strike) ?? null), itemStyle: { color: "#2DD4A8" } },
    ],
  } };
}

function ResearchImport({ onImported }: { onImported: () => void }) {
  const [kind, setKind] = useState("observations");
  const [payload, setPayload] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  async function submit() {
    setMessage("");
    try {
      const parsed = JSON.parse(payload);
      const rows: unknown = Array.isArray(parsed) ? parsed : parsed[kind];
      if (!Array.isArray(rows) || !rows.length) throw new Error(`Provide a nonempty JSON array or an object with an ${kind} array.`);
      setBusy(true);
      if (kind === "events") await niftyApi.importEvents(rows);
      else await niftyApi.importObservations(rows);
      setMessage(`Imported ${rows.length} ${kind}. Dashboard updated.`); setPayload(""); onImported();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Import failed"); }
    finally { setBusy(false); }
  }
  return <details className="panel nifty-import" id="nifty-import-research"><summary>Add sourced research observations or events</summary><div className="panel-body"><p className="muted">Use publisher dates and link to the underlying evidence. Imported observations are retained alongside collected data. Factor IDs appear in the historical research selector.</p>
    <div className="row"><label htmlFor="nifty-import-kind">Import</label><select id="nifty-import-kind" value={kind} onChange={event => { setKind(event.target.value); setMessage(""); }}><option value="observations">Factor observations</option><option value="events">Calendar events</option></select></div>
    <pre className="nifty-import-example">{kind === "observations" ? '[{"factor_id":"rbi_repo","value":6.5,"reported_at":"2026-10-01T10:00:00+05:30","source":"Publisher name","source_url":"https://publisher.example/release"}]' : '[{"id":"event-id","title":"Published event title","event_at":"2026-11-01T10:00:00+05:30","category":"economy","source":"Publisher name","source_url":"https://publisher.example/calendar"}]'}</pre>
    <label className="sr-only" htmlFor="nifty-import-json">Research JSON</label><textarea id="nifty-import-json" rows={5} placeholder="Paste your sourced JSON array here…" value={payload} onChange={event => setPayload(event.target.value)} spellCheck={false} />
    <div className="row"><button type="button" className="primary" disabled={busy || !payload.trim()} onClick={() => void submit()}>{busy ? "Importing…" : "Import research"}</button>{message && <span role="status">{message}</span>}</div>
  </div></details>;
}

export default function NiftyPage() {
  const [dashboard, setDashboard] = useState<NiftyDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const liveRequest = useRef(false);
  useLiveMarket(["NSE_INDEX|Nifty 50"], async () => {
    if (liveRequest.current) return;
    liveRequest.current = true;
    try { setDashboard(await niftyApi.dashboard()); setError(null); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load live NIFTY research"); }
    finally { liveRequest.current = false; }
  });
  const [manualPending, setManualPending] = useState(false);
  const [query, setQuery] = useState("");
  const [priority, setPriority] = useState("all");
  const [kind, setKind] = useState("all");
  const [status, setStatus] = useState("all");
  const [selected, setSelected] = useState("sp500");
  const [history, setHistory] = useState<NiftyHistory | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [correlation, setCorrelation] = useState<NiftyCorrelation | null>(null);
  const [correlationLoading, setCorrelationLoading] = useState(false);
  const [correlationError, setCorrelationError] = useState<string | null>(null);
  const [explorerOpen, setExplorerOpen] = useState(false);
  const [upcomingOnly, setUpcomingOnly] = useState(true);

  useEffect(() => startMinutePolling({ live: true, load: niftyApi.dashboard,
    onData: data => { setDashboard(data); setError(null); }, onError: reason => setError(reason instanceof Error ? reason.message : "Unable to load NIFTY research"), onLoading: setLoading,
  }), [reload]);

  const refreshing = manualPending || Boolean(dashboard?.refreshing);
  useEffect(() => {
    if (!refreshing) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout>;
    async function check() {
      try {
        const data = await niftyApi.dashboard();
        if (cancelled) return;
        setDashboard(data); setManualPending(false); setError(null);
        if (data.refreshing) timer = setTimeout(check, 4000);
      } catch (reason) { if (!cancelled) { setError(reason instanceof Error ? reason.message : "Refresh status unavailable"); setManualPending(false); timer = setTimeout(check, 10000); } }
    }
    timer = setTimeout(check, 3000);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [refreshing]);

  const factors = useMemo(() => dashboard?.sections.flatMap(section => section.factors) || [], [dashboard]);
  const current = factors.find(factor => factor.id === selected);
  const core = CORE_IDS.flatMap(id => { const factor = factors.find(item => item.id === id); return factor ? [factor] : []; });
  const featured = core.length ? core : factors.filter(factor => factor.priority.startsWith("P1")).slice(0, 8);
  const visibleSections = useMemo(() => (dashboard?.sections || []).map(section => ({ ...section, factors: section.factors.filter(factor => {
    const match = `${factor.label} ${factor.id} ${factor.description} ${factor.source || ""} ${section.title}`.toLowerCase().includes(query.trim().toLowerCase());
    return match && (priority === "all" || factor.priority.startsWith(priority)) && (kind === "all" || factor.kind === kind) && (status === "all" || factor.status === status);
  }) })).filter(section => section.factors.length), [dashboard, query, priority, kind, status]);
  const visibleCount = visibleSections.reduce((sum, section) => sum + section.factors.length, 0);
  const trendOption = useMemo(() => historyOption(current, history), [current, history]);
  const openInterest = useMemo(() => oiOption(factors), [factors]);
  const callOi = factors.find(factor => factor.id === "call_oi");
  const putOi = factors.find(factor => factor.id === "put_oi");
  const callExpiry = snapshotExpiry(callOi);
  const putExpiry = snapshotExpiry(putOi);
  const mismatchedExpiries = Boolean(callExpiry && putExpiry && callExpiry !== putExpiry);
  const selectedExpiry = callExpiry && callExpiry === putExpiry ? callExpiry : null;
  const events = useMemo(() => (dashboard?.events || []).filter(event => !upcomingOnly || Date.parse(event.event_at) >= Date.now() - 86400000).slice().sort((a, b) => Date.parse(a.event_at) - Date.parse(b.event_at)), [dashboard, upcomingOnly]);

  useEffect(() => {
    if (!factors.length || factors.some(factor => factor.id === selected)) return;
    setSelected(factors.find(factor => typeof factor.value === "number")?.id || factors[0].id);
  }, [factors, selected]);

  useEffect(() => {
    let cancelled = false;
    setHistory(null); setHistoryError(null); setCorrelation(null); setCorrelationError(null);
    if (!selected) return;
    setHistoryLoading(true);
    niftyApi.history(selected).then(result => { if (!cancelled) setHistory(result); }).catch(reason => {
      if (!cancelled) setHistoryError(reason instanceof Error ? reason.message : "History unavailable");
    }).finally(() => { if (!cancelled) setHistoryLoading(false); });
    return () => { cancelled = true; };
  }, [selected, dashboard?.last_refresh, reload]);

  async function refreshSources() {
    setManualPending(true); setError(null);
    try { await niftyApi.refresh(); }
    catch (reason) { setManualPending(false); setError(reason instanceof Error ? reason.message : "Could not start refresh"); }
  }

  async function exploreCorrelation() {
    const factorId = selected;
    setCorrelationLoading(true); setCorrelationError(null); setCorrelation(null);
    try { const result = await niftyApi.correlation(factorId); setCorrelation(result); }
    catch (reason) { setCorrelationError(reason instanceof Error ? reason.message : "Correlation unavailable"); }
    finally { setCorrelationLoading(false); }
  }

  function selectFactor(id: string) {
    setSelected(id);
    document.getElementById("nifty-research")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  const summary = dashboard?.summary;
  const coverage = summary?.total ? Math.round(summary.available / summary.total * 100) : 0;
  return <AppShell title="NIFTY"><div className="nifty-page stack">
    <section className="nifty-intro"><div><span className="nifty-eyebrow">INDIA / INDEX RESEARCH</span><h2>The forces behind NIFTY 50.</h2><p>A complete factor map across global markets, capital flows, positioning and the Indian economy.</p></div><div className="nifty-sync"><span className={`nifty-sync-label ${refreshing ? "nifty-working" : ""}`}><span className="dot ok" />{refreshing ? "Collecting source updates…" : loading ? "Checking saved research…" : "Research desk · 1 min updates"}</span><span className="muted">Last collection: {niftyDate(dashboard?.last_refresh, true)}{dashboard?.last_refresh ? " IST" : ""}</span><button type="button" className="primary" disabled={refreshing} onClick={() => void refreshSources()}>{refreshing ? "Refreshing sources…" : "Refresh sources ↻"}</button></div></section>
    {error && <div className="error-box" role="status">{error}{dashboard ? " · Retained research remains visible with its original timestamps." : ""}</div>}
    {dashboard?.source_errors.length ? <div className="nifty-source-warning" role="status"><details><summary>{dashboard.source_errors.length} source{dashboard.source_errors.length === 1 ? "" : "s"} could not update. Inspect collection status.</summary>{dashboard.source_errors.map((source, i) => <p key={`${source.source}-${i}`}><strong>{source.source}:</strong> {source.error}</p>)}</details></div> : null}
    <div className="nifty-coverage-strip">{[["Factors tracked", summary?.total, "Across all 10 sections"], ["Available", summary?.available, "Within source cadence"], ["Stale", summary?.stale, "Retained · check publisher time"], ["Unavailable", summary?.missing, "Explicit research gaps"]].map(([label, value, caption], i) => <div className={`nifty-coverage-stat nifty-coverage-stat-${i}`} key={label as string}><span>{label}</span><strong>{value == null ? "—" : String(value)}</strong><small>{caption}</small></div>)}<div className="nifty-coverage-meter"><span>Current coverage <strong>{summary ? `${coverage}%` : "—"}</strong></span><div className="nifty-meter"><i style={{ width: `${coverage}%` }} /></div><small>{summary?.drivers ?? "—"} drivers · {summary?.indicators ?? "—"} indicators</small></div></div>
    <nav className="nifty-top-nav" aria-label="Research workspace"><a href="#nifty-research">Historical research ↗</a><a href="#nifty-factor-map">Complete factor map ↗</a><a href="#nifty-positioning">Options & calendar ↗</a><a href="#nifty-import-research">Add research ↗</a></nav>
    <div className="nifty-section-label"><h2>Core watch</h2><span>Value, change and the time behind the reading</span></div>
    <div className="nifty-core-grid">{featured.map(factor => <button type="button" className={`nifty-core-card nifty-core-${factor.status}`} key={factor.id} onClick={() => selectFactor(factor.id)}><div className="nifty-core-label"><span>{factor.label}</span><span className={`nifty-status nifty-status-${factor.status}`}>{factorStatusLabel(factor)}</span></div><strong><FactorValue value={factor.value} unit={factor.unit} compact /></strong><FactorChange factor={factor} /><CashFlowDetails factor={factor} /><div className="nifty-core-source">{factor.source || "Source pending"}<br />{factorReportLabel(factor)}</div></button>)}</div>
    {!dashboard && <div className="panel nifty-loading" role="status">{loading ? "Loading the complete NIFTY research map…" : "Research data could not be loaded. Refresh sources to retry."}</div>}
    <div className="nifty-market-grid"><PriceActionChart initialCandles={dashboard?.candles || []} /><aside className="panel nifty-reading-guide"><span className="nifty-eyebrow">READ THE EVIDENCE</span><h3>Drivers, indicators, context.</h3><p><i className="nifty-guide-dot nifty-guide-driver" /><strong>Drivers</strong> Earnings, interest rates, policy and global shocks can change the economic backdrop.</p><p><i className="nifty-guide-dot nifty-guide-indicator" /><strong>Indicators</strong> OI, PCR, breadth and technicals describe positioning and price behaviour.</p><p><i className="nifty-guide-dot nifty-guide-context" /><strong>Context</strong> Scheduled events and structural changes help frame the session.</p><div className="nifty-guide-note">Read changes together. Indicators do not establish the direction of the next move. Missing values remain unavailable; stale values keep their original dates.</div></aside></div>

    <section id="nifty-research" className="nifty-research"><div className="nifty-section-label"><div><span className="nifty-eyebrow">CONNECT THE DOTS</span><h2>Historical research</h2></div><div className="nifty-research-select"><label htmlFor="nifty-factor-select">Explore factor</label><select id="nifty-factor-select" value={selected} onChange={event => setSelected(event.target.value)}>{dashboard?.sections.map(section => <optgroup key={section.id} label={section.title}>{section.factors.map(factor => <option key={factor.id} value={factor.id}>{factor.label}</option>)}</optgroup>)}</select></div></div>
      <div className="nifty-research-grid"><ExpandableChartPanel title={`${current?.label || "Factor"} historical observations`}><div className="panel-header"><div><h2>{current?.label || "Select a factor"} · historical observations</h2><p className="nifty-caption">{current ? `Factor ID: ${current.id} · ${current.cadence}` : "Select any item in the factor map"}</p></div></div><div className="panel-body">{trendOption !== emptyOption ? <EChartPanel option={trendOption} height={270} /> : <div className="chart-empty" style={{ height: 270 }}>{historyLoading ? "Loading retained observations…" : "No numeric history available for this factor. Published qualitative observations appear in the evidence log below."}</div>}{historyError && <p className="nifty-inline-warning" role="status">{historyError}</p>}<p className="nifty-caption">Current source and unit only; the latest revision is used at each timestamp. Publisher time is used when available, otherwise collection time. The evidence log retains both timestamps.</p></div></ExpandableChartPanel>
      <aside className="panel nifty-correlation"><span className="nifty-eyebrow">CROSS-MARKET EXPLORER</span><h3>How does it move with NIFTY?</h3><p>Compare daily changes in this factor with daily NIFTY returns on matching dates.</p><button type="button" disabled={!current || correlationLoading} onClick={() => void exploreCorrelation()}>{correlationLoading ? "Calculating…" : "Calculate correlation"}</button>{correlation && correlation.factor_id === selected && <><div className="nifty-coefficient">{correlation.coefficient == null ? "Unavailable" : niftyNumber(correlation.coefficient, 3)}</div><div className="nifty-correlation-meta">{correlation.sample_count} matched observations · {correlation.method}</div><p>{correlation.note}</p></>}{correlationError && <p role="status" className="nifty-inline-warning">{correlationError}</p>}<div className="nifty-guide-note">Correlation does not establish causality. Timing, data frequency and sample size affect the result.</div></aside></div>
      <details className="panel nifty-observation-log"><summary>Observation evidence log {history ? `(${history.observations.length})` : ""}</summary><div className="table-wrap"><table className="data"><thead><tr><th>Report date / source time (IST)</th><th>Collected (IST)</th><th>Value</th><th>Change / %</th><th>Source evidence</th></tr></thead><tbody>{history?.observations.map((row, index) => <tr key={index}><td>{row.reporting_date ? `Session ${row.reporting_date}` : niftyDate(row.reported_at)}</td><td>{niftyDate(row.observed_at)}</td><td><FactorValue value={row.value} unit={row.unit || current?.unit} compact />{row.quality_note && <p className="nifty-inline-warning">{row.quality_note}</p>}</td><td>{row.change == null ? "Unavailable" : niftyNumber(row.change)} / {row.change_pct == null ? "Unavailable" : `${niftyNumber(row.change_pct)}%`}</td><td>{niftyLink(row.source_url) ? <a href={niftyLink(row.source_url)} target="_blank" rel="noreferrer">{row.source} ↗</a> : row.source || "Not supplied"}</td></tr>)}</tbody></table>{!history?.observations.length && <div className="empty-note">No retained observations for this factor yet.</div>}</div></details>
    </section>

    <div className="nifty-section-label"><div><span className="nifty-eyebrow">THE COMPLETE FACTOR MAP</span><h2>Research across every angle</h2></div><span>{visibleCount} of {summary?.total ?? "—"} factors shown</span></div>
    <section className="panel nifty-filter-panel" id="nifty-factor-map"><div className="nifty-priority-tabs" role="group" aria-label="Factor priority">{PRIORITIES.map(([value, label]) => <button key={value} type="button" aria-pressed={priority === value} className={priority === value ? "is-active" : ""} onClick={() => setPriority(value)}>{label}</button>)}</div><div className="nifty-filters"><div className="nifty-search"><label className="sr-only" htmlFor="nifty-search">Search all research factors</label><input id="nifty-search" type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search factors, markets or sources…" /></div><label className="sr-only" htmlFor="nifty-kind">Factor type</label><select id="nifty-kind" value={kind} onChange={event => setKind(event.target.value)}><option value="all">Drivers, indicators & context</option><option value="driver">Drivers only</option><option value="indicator">Indicators only</option><option value="context">Context only</option></select><label className="sr-only" htmlFor="nifty-status">Source availability</label><select id="nifty-status" value={status} onChange={event => setStatus(event.target.value)}><option value="all">All source statuses</option><option value="available">Available</option><option value="stale">Stale</option><option value="missing">Unavailable</option></select>{(query || priority !== "all" || kind !== "all" || status !== "all") && <button type="button" onClick={() => { setQuery(""); setPriority("all"); setKind("all"); setStatus("all"); }}>Reset</button>}</div><nav className="nifty-section-nav" aria-label="Jump to factor section">{visibleSections.map((section, i) => <a href={`#nifty-section-${section.id}`} key={section.id}><span>{String((dashboard?.sections.findIndex(item => item.id === section.id) ?? i) + 1).padStart(2, "0")}</span>{section.title}<small>{section.factors.length}</small></a>)}</nav></section>
    <div className="nifty-factor-sections">{visibleSections.map(section => <section className="nifty-factor-section" id={`nifty-section-${section.id}`} key={section.id}><div className="nifty-group-heading"><div className="nifty-group-number">{String((dashboard?.sections.findIndex(item => item.id === section.id) ?? 0) + 1).padStart(2, "0")}</div><div><h2>{section.title}</h2><p>{section.description}</p></div><span>{section.factors.filter(factor => factor.status === "available").length}/{section.factors.length} current</span></div><div className="nifty-factor-grid">{section.factors.map(factor => <NiftyFactorCard key={factor.id} factor={factor} selected={selected === factor.id} onSelect={selectFactor} />)}</div></section>)}{dashboard && !visibleCount && <div className="panel empty-note">No factors match these filters. Try another priority, source status or search.</div>}</div>

    <div className="nifty-section-label" id="nifty-positioning"><div><span className="nifty-eyebrow">POSITIONING & CATALYSTS</span><h2>Options, expiries and events</h2></div></div>
    <ExpandableChartPanel title="NIFTY strike-wise open interest"><div className="panel-header"><div><h2>NIFTY strike-wise open interest</h2><p className="nifty-caption">Call and put positioning · {selectedExpiry ? `Snapshot expiry ${expiryLabel(selectedExpiry)}` : "Snapshot expiry not supplied for both legs"}</p></div></div><div className="panel-body"><div className="nifty-oi-evidence"><OiSnapshotEvidence factor={callOi} label="Call OI snapshot" /><OiSnapshotEvidence factor={putOi} label="Put OI snapshot" /></div>{mismatchedExpiries ? <div className="chart-empty" style={{ height: 220 }}>Call and put observations belong to different expiries. Refresh sources or inspect the individual factor evidence.</div> : openInterest.count ? <EChartPanel option={openInterest.option} height={310} /> : <div className="chart-empty" style={{ height: 220 }}>Strike-wise options data is unavailable. Refresh sources when an option-chain snapshot is available.</div>}<p className="nifty-caption">OI describes outstanding contracts. Call and put concentration alone does not predict the next index move. Check the options factors for the snapshot date and expiry.</p></div></ExpandableChartPanel>
    <section className="panel"><div className="panel-header"><div><h2>Research calendar</h2><p className="nifty-caption">Publisher-supplied dates · all times IST</p></div><label className="nifty-calendar-toggle"><input type="checkbox" checked={upcomingOnly} onChange={event => setUpcomingOnly(event.target.checked)} />Upcoming & today</label></div><div className="nifty-calendar">{events.map(event => <article key={event.id} className="nifty-event"><time dateTime={event.event_at}>{niftyDate(event.event_at)}</time><div><span className="nifty-eyebrow">{event.category}{event.impact ? ` · ${event.impact}` : ""}</span><h3>{event.title}</h3>{(event.actual != null || event.forecast != null || event.previous != null) && <div className="nifty-event-readings">Actual: {event.actual == null ? "Pending" : <FactorValue value={event.actual} compact />} · Forecast: {event.forecast == null ? "Not supplied" : <FactorValue value={event.forecast} compact />} · Previous: {event.previous == null ? "Not supplied" : <FactorValue value={event.previous} compact />}</div>}{niftyLink(event.source_url) ? <a href={niftyLink(event.source_url)} target="_blank" rel="noreferrer">{event.source} ↗</a> : <span className="muted">{event.source || "Source pending"}</span>}</div></article>)}{!events.length && <div className="empty-note">No {upcomingOnly ? "upcoming " : ""}sourced events are stored. Add scheduled releases or research events below.</div>}</div><details className="nifty-expiries"><summary>Exchange expiry calendar ({dashboard?.expiries.length || 0})</summary>{dashboard?.expiries.length ? <FactorValue value={dashboard.expiries} /> : <p className="muted">No current contract expiry dates available from the source.</p>}</details></section>
    <ResearchImport onImported={() => setReload(value => value + 1)} />
    <details className="panel nifty-candle-explorer" onToggle={event => setExplorerOpen(event.currentTarget.open)}><summary>OHLCV explorer · instruments, intervals and date ranges</summary>{explorerOpen && <div className="panel-body"><CandleExplorer /></div>}</details>
    {dashboard?.notes.length ? <div className="nifty-methodology"><span className="nifty-eyebrow">RESEARCH NOTES</span>{dashboard.notes.map((note, i) => <p key={i}>{note}</p>)}</div> : null}
    <p className="nifty-footnote">Every reading belongs to its own market session and publication schedule. Page refresh time is separate from publisher time. Market drivers and descriptive indicators are shown together to support research.</p>
  </div></AppShell>;
}



