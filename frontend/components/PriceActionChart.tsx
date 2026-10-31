"use client";

import { useEffect, useMemo, useState } from "react";
import ChartPanel from "@/components/ChartPanel";
import ExpandableChartPanel from "@/components/ExpandableChartPanel";
import { SourceBadge } from "@/components/Bits";
import { api, type Candle, type InstrumentHit } from "@/lib/api";
import { startMinutePolling } from "@/lib/minutePolling";
import { useLiveMarket } from "@/lib/liveMarket";
import { mergeLiveCandles } from "@/lib/liveCandles";
import { niftyApi } from "@/lib/niftyApi";
import { CONCEPT_USAGE_KEY, frequentConcepts, parseConceptUsage, istDay, selectStudy, studyTime, type ConceptUsage, type PriceActionResponse } from "@/lib/priceAction";
import PriceActionStudyPanel from "@/components/PriceActionStudyPanel";

const TICKERS = [
  { label: "NIFTY 50", key: "NSE_INDEX|Nifty 50", group: "Indices" },
  { label: "Bank NIFTY", key: "NSE_INDEX|Nifty Bank", group: "Indices" },
  { label: "India VIX", key: "NSE_INDEX|India VIX", group: "Indices" },
  { label: "NIFTY Financial Services", key: "NSE_INDEX|Nifty Fin Service", group: "Sectors" },
  { label: "NIFTY IT", key: "NSE_INDEX|Nifty IT", group: "Sectors" },
  { label: "NIFTY Auto", key: "NSE_INDEX|Nifty Auto", group: "Sectors" },
  { label: "NIFTY FMCG", key: "NSE_INDEX|Nifty FMCG", group: "Sectors" },
  { label: "NIFTY Pharma", key: "NSE_INDEX|Nifty Pharma", group: "Sectors" },
  { label: "NIFTY Metal", key: "NSE_INDEX|Nifty Metal", group: "Sectors" },
  { label: "NIFTY Energy", key: "NSE_INDEX|Nifty Energy", group: "Sectors" },
  { label: "NIFTY Realty", key: "NSE_INDEX|Nifty Realty", group: "Sectors" },
  { label: "NIFTY PSU Bank", key: "NSE_INDEX|Nifty PSU Bank", group: "Sectors" },
  { label: "RELIANCE", key: "NSE_EQ|INE002A01018", group: "Stocks" },
  { label: "HDFC BANK", key: "NSE_EQ|INE040A01034", group: "Stocks" },
  { label: "ICICI BANK", key: "NSE_EQ|INE090A01021", group: "Stocks" },
  { label: "INFOSYS", key: "NSE_EQ|INE009A01021", group: "Stocks" },
  { label: "TCS", key: "NSE_EQ|INE467B01029", group: "Stocks" },
  { label: "SBI", key: "NSE_EQ|INE062A01020", group: "Stocks" },
];
const INTERVALS = [["1minute", "1 min"], ["5minute", "5 min"], ["15minute", "15 min"], ["30minute", "30 min"], ["1hour", "1 hour"], ["1day", "Daily"], ["1week", "Weekly"]];
const RANGES: Record<string, number[]> = {
  "1minute": [1, 5, 30], "5minute": [5, 30, 90], "15minute": [30, 90, 180],
  "30minute": [30, 90, 180, 365], "1hour": [30, 90, 180, 365],
  "1day": [30, 90, 180, 365, 1095], "1week": [365, 1095, 1825],
};
const RANGE_LABELS: Record<number, string> = { 1: "1 day", 5: "5 days", 30: "1 month", 90: "3 months", 180: "6 months", 365: "1 year", 1095: "3 years", 1825: "5 years" };
const EMA_OVERLAYS = [{ period: 9, color: "#FBBF24" }, { period: 21, color: "#A78BFA" }];
type Loaded = { key: string; interval: string; days: number; session: string; orb: number; round: number; series: PriceActionResponse };

export default function PriceActionChart({ initialCandles }: { initialCandles: Candle[] }) {
  const [ticker, setTicker] = useState<{ label: string; key: string }>(TICKERS[0]);
  const [interval, setInterval] = useState("5minute");
  const [days, setDays] = useState(5);
  const [chartType, setChartType] = useState<"candlestick" | "line" | "area">("candlestick");
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reload, setReload] = useState(0);
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<InstrumentHit[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [session, setSession] = useState("");
  const [orb, setOrb] = useState(15);
  const [round, setRound] = useState(100);
  const [preset, setPreset] = useState("none");
  const [selectedConcepts, setSelectedConcepts] = useState<number[]>([]);
  const [usage, setUsage] = useState<ConceptUsage>({});
  const [focus, setFocus] = useState<string | null>(null);
  useEffect(() => {
    try { setUsage(parseConceptUsage(localStorage.getItem(CONCEPT_USAGE_KEY))); } catch { /* Chart works when browser storage is unavailable. */ }
  }, []);
  useLiveMarket([ticker.key], event => setLoaded(previous => {
    if (!previous || previous.key !== ticker.key || previous.interval !== interval || previous.days !== days) return previous;
    const candles = mergeLiveCandles(previous.series.candles, event.quotes[ticker.key], interval);
    return { ...previous, series: { ...previous.series, candles, count: candles.length } };
  }));

  useEffect(() => {
    setError(null);
    return startMinutePolling({ live: true,
      load: async () => {
        const data = await niftyApi.priceAction({ instrument_key: ticker.key, interval,
          from_date: new Date(Date.now() - days * 86400000).toISOString().slice(0, 10),
          ...(session ? { session } : {}), orb_minutes: String(orb), round_step: String(round) });
        if (data.instrument_key !== ticker.key || data.interval !== interval) throw new Error("The source returned a different instrument or timeframe. Refresh to retry.");
        return data;
      },
      onData: series => { setLoaded({ key: ticker.key, interval, days, session, orb, round, series }); setError(null); },
      onError: reason => setError(reason instanceof Error ? reason.message : "Price history is unavailable"),
      onLoading: setLoading,
    });
  }, [ticker.key, interval, days, session, orb, round, reload]);

  useEffect(() => {
    const term = query.trim();
    let cancelled = false;
    setHits([]); setSearchError(null); setSearching(false);
    if (term.length < 2) return;
    setSearching(true);
    const timer = setTimeout(async () => {
      try {
        const response = await api.searchInstruments(term, 8);
        const rows = Array.isArray(response) ? response : response.data || [];
        if (!cancelled) setHits(rows.filter(row => Boolean(row.instrument_key)));
      } catch (reason) {
        if (!cancelled) setSearchError(reason instanceof Error ? reason.message : "Instrument search is unavailable");
      } finally { if (!cancelled) setSearching(false); }
    }, 400);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [query]);

  const series = loaded?.key === ticker.key && loaded.interval === interval && loaded.days === days && loaded.session === session && loaded.orb === orb && loaded.round === round ? loaded.series : null;
  const candles = useMemo(() => {
    if (series) return series.candles;
    if (error || ticker.key !== TICKERS[0].key || interval !== "1day") return [];
    const cutoff = Date.now() - days * 86400000;
    return initialCandles.filter(row => Date.parse(row.ts) >= cutoff);
  }, [series, initialCandles, ticker.key, interval, days, error]);
  const study = series?.study || null;
  const intraday = !["1day", "1week"].includes(interval);
  const visibleCandles = useMemo(() => intraday && study?.session ? candles.filter(row => istDay(row.ts) === study.session) : candles, [candles, intraday, study?.session]);
  const overlay = useMemo(() => ({ ...selectStudy(study, [], preset, null, selectedConcepts), focus }), [study, preset, selectedConcepts, focus]);
  const frequent = useMemo(() => frequentConcepts(study?.catalog || [], usage), [study?.catalog, usage]);
  const selected = preset === "custom" ? selectedConcepts : [];
  function toggleConcept(id: number) {
    const active = preset === "all" || selected.includes(id);
    const next = (preset === "all" ? (study?.catalog || []).map(row => row.id) : selected).filter(value => value !== id);
    if (!active) {
      next.push(id);
      let stored: ConceptUsage = {};
      try { stored = parseConceptUsage(localStorage.getItem(CONCEPT_USAGE_KEY)); } catch { /* Use in-memory counts. */ }
      const counts = { ...usage, ...stored, [id]: Math.min(Number.MAX_SAFE_INTEGER, Math.max(usage[id] || 0, stored[id] || 0) + 1) };
      setUsage(counts);
      try { localStorage.setItem(CONCEPT_USAGE_KEY, JSON.stringify(counts)); } catch { /* Selection still works without storage. */ }
    }
    setSelectedConcepts(next); setPreset(next.length ? "custom" : "none"); setFocus(null);
  }
  const resetStudy = () => { setSession(""); setFocus(null); };
  const intervalLabel = INTERVALS.find(([value]) => value === interval)?.[1] || interval;
  function chooseTicker(key: string) {
    const option = TICKERS.find(row => row.key === key);
    if (option) { setTicker(option); setError(null); resetStudy(); }
  }
  function chooseInterval(next: string) {
    setInterval(next);
    setFocus(null);
    setDays(previous => RANGES[next].includes(previous) ? previous : next === "1minute" ? 5 : RANGES[next][1] || RANGES[next][0]);
  }

  return <ExpandableChartPanel title={`${ticker.label} price action`}>
    <div className="panel-header"><div><h2>{ticker.label} · price action</h2><p className="nifty-caption">{intervalLabel} · {intraday ? study?.session || "checking session…" : RANGE_LABELS[days]} · {visibleCandles.length.toLocaleString()} bars · IST{loading ? " · updating…" : ""}</p></div></div>
    <div className="price-chart-controls">
      <div className="field"><label htmlFor="price-ticker">Ticker</label><select id="price-ticker" value={ticker.key} onChange={event => chooseTicker(event.target.value)}>
        {["Indices", "Sectors", "Stocks"].map(group => <optgroup key={group} label={group}>{TICKERS.filter(row => row.group === group).map(row => <option key={row.key} value={row.key}>{row.label}</option>)}</optgroup>)}
        {!TICKERS.some(row => row.key === ticker.key) && <option value={ticker.key}>{ticker.label}</option>}
      </select></div>
      <div className="field"><label htmlFor="price-timeframe">Timeframe</label><select id="price-timeframe" value={interval} onChange={event => chooseInterval(event.target.value)}>{INTERVALS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></div>
      <div className="field"><label htmlFor="price-range">History</label><select id="price-range" value={days} onChange={event => { setDays(Number(event.target.value)); resetStudy(); }}>{RANGES[interval].map(value => <option key={value} value={value}>{RANGE_LABELS[value]}</option>)}</select></div>
      <div className="field"><label htmlFor="price-style">Chart style</label><select id="price-style" value={chartType} onChange={event => setChartType(event.target.value as typeof chartType)}><option value="candlestick">Candles</option><option value="line">Line</option><option value="area">Area</option></select></div>
      <button type="button" aria-label="Refresh price chart" disabled={loading} onClick={() => setReload(value => value + 1)}>↻ Refresh</button>
      <div className="field price-chart-search"><label htmlFor="price-search">Find another ticker</label><input id="price-search" type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Search stocks or instruments…" autoComplete="off" />
        {query.trim().length >= 2 && <div className="price-chart-results" aria-live="polite">{searching ? <span>Searching…</span> : searchError ? <span>{searchError}</span> : hits.length ? hits.map(hit => <button type="button" key={hit.instrument_key} onClick={() => { setTicker({ key: hit.instrument_key, label: hit.trading_symbol || hit.short_name || hit.name || hit.instrument_key }); setQuery(""); setError(null); resetStudy(); }}><strong>{hit.trading_symbol || hit.short_name || hit.name}</strong><small>{hit.exchange || hit.segment} · {hit.name || hit.instrument_key}</small></button>) : <span>No matching instruments.</span>}</div>}
      </div>
    </div>
    {intraday && <div className="price-study-controls">
      <div className="price-study-settings">
        <label>Study session <select aria-label="Price action study session" value={session} onChange={e => { setSession(e.target.value); setFocus(null); }}><option value="">Latest available</option>{(study?.sessions || loaded?.series.study.sessions || []).slice().reverse().map(day => <option key={day} value={day}>{day}</option>)}</select></label>
        <label>Layers <select aria-label="Price action layers" value={preset} onChange={e => { setPreset(e.target.value); setFocus(null); if (e.target.value === "none") setSelectedConcepts([]); }}><option value="none">Clean chart</option><option value="custom">Selected concepts</option><option value="all">All 47 concepts</option></select></label>
        <label>Add concept <select aria-label="Add a price action concept" value="" onChange={e => { if (e.target.value) toggleConcept(Number(e.target.value)); }}><option value="">Choose a concept…</option>{(study?.catalog || []).filter(row => preset !== "all" && !selected.includes(row.id)).map(row => <option key={row.id} value={row.id}>{row.label}</option>)}</select></label>
        <label>Opening range <select aria-label="Opening range minutes" value={orb} onChange={e => setOrb(Number(e.target.value))}>{[5, 15, 30].map(n => <option key={n} value={n}>{n} min</option>)}</select></label>
        <label>Round levels <select aria-label="Round level spacing" value={round} onChange={e => setRound(Number(e.target.value))}>{[50, 100, 500].map(n => <option key={n} value={n}>{n} pts</option>)}</select></label>
      </div>
      <div className="price-study-layers" aria-label="Frequently used concepts"><span className="muted">Frequently used:</span>{frequent.length ? frequent.map(row => <button type="button" key={row.id} aria-pressed={preset === "all" || selected.includes(row.id)} onClick={() => toggleConcept(row.id)}>{row.label}</button>) : <span className="muted">Choose concepts to build your shortcuts.</span>}</div>
      {(selected.length > 0 || focus) && <div className="price-study-layers" aria-label="Selected concepts"><span className="muted">Selected:</span>{(study?.catalog || []).filter(row => selected.includes(row.id)).map(row => <button type="button" key={row.id} aria-pressed="true" onClick={() => toggleConcept(row.id)}>{row.label} ×</button>)}{focus && <button type="button" onClick={() => setFocus(null)}>Reset focus ×</button>}</div>}
    </div>}
    <div className="price-chart-status" role="status">{error ? <span className="nifty-inline-warning">{error}{series?.candles.length ? " · Showing the last successful response for this ticker." : ""}</span> : <><span className="mono">{ticker.key}</span>{series ? <SourceBadge source={series.source} /> : candles.length ? <span>Retained NIFTY daily bars</span> : null}</>}{series?.hint && <span className="nifty-inline-warning">{series.hint}</span>}</div>
    {intraday && study && <div className="price-study-summary"><strong>{study.trend}</strong><span>{study.completed_bars} closed · through {studyTime(study.confirmed_through)} IST</span><span>PDH/PDL: {study.previous_session || "unavailable"}</span>{!!study.missing_bars && <span className="nifty-inline-warning">{study.missing_bars} missing bars</span>}{study.notes.some(note => note.startsWith("Opening range unavailable")) && <span className="nifty-inline-warning">Opening range unavailable</span>}<span>Green: upward / support · Red: downward / resistance · Hover markers for matches</span></div>}
    {!intraday && <div className="price-chart-status">Choose 5 or 15 minutes for the 47-concept price-action study.</div>}
    <div className="price-chart-status" aria-label="Moving average legend">{EMA_OVERLAYS.map(ema => <span key={ema.period} style={{ color: ema.color }}>━ EMA {ema.period}</span>)}<span>Based on candle closes · periods follow the selected timeframe</span></div>
    <div className="panel-body tight">{visibleCandles.length ? <ChartPanel key={`${ticker.key}:${interval}:${study?.session || days}:${focus || ""}`} candles={visibleCandles} chartType={chartType} height={420} timeZone="Asia/Kolkata" study={intraday ? overlay : undefined} showVolume={!ticker.key.startsWith("NSE_INDEX|")} emaOverlays={EMA_OVERLAYS} indicatorCandles={candles} /> : <div className="chart-empty" style={{ height: 360 }}><div>{loading ? `Loading ${ticker.label}…` : `No ${intervalLabel.toLowerCase()} bars for ${ticker.label} in this range.`}</div><div className="muted">Choose another history range or ticker, or refresh to retry.</div></div>}</div>
    {intraday && study && <PriceActionStudyPanel study={study} overlay={overlay} selectedConcepts={preset === "all" ? study.catalog.map(row => row.id) : selected} onConcept={toggleConcept} onFocus={event => setFocus(event.ts)} />}
  </ExpandableChartPanel>;
}
