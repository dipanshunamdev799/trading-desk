"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import EChartPanel, { type EChartsOption } from "@/components/EChartPanel";
import { useLiveMarket } from "@/lib/liveMarket";
import { spreadApi, money, points, ist, payoff, type Strategy, type SpreadDashboard, type SpreadMarket, type SpreadChart, type SpreadPreview, type SpreadTicket, type SpreadTrade, type SpreadSettings } from "@/lib/creditSpreads";
import "./spreads.css";

const names = { BEAR_CALL: "Bear call spread", BULL_PUT: "Bull put spread" };
const baseChart: EChartsOption = { animation: false, backgroundColor: "transparent", textStyle: { color: "#8B9AAB", fontFamily: "Segoe UI, sans-serif" }, tooltip: { trigger: "axis", backgroundColor: "#121820", borderColor: "#243041", textStyle: { color: "#E8EDF2" } }, grid: { left: 65, right: 30, top: 28, bottom: 46 }, xAxis: { type: "value", axisLabel: { color: "#8B9AAB" }, splitLine: { show: false } }, yAxis: { type: "value", scale: true, axisLabel: { color: "#8B9AAB" }, splitLine: { lineStyle: { color: "#1d2836" } } } };

function Panel({ title, extra, children, className = "" }: { title: string; extra?: React.ReactNode; children: React.ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><div className="panel-header"><h2>{title}</h2>{extra}</div>{children}</section>;
}

export default function CreditSpreadPage() {
  return <AppShell title="NIFTY credit spreads"><SpreadDesk /></AppShell>;
}

function SpreadDesk() {
  const [tab, setTab] = useState("workspace");
  const [desk, setDesk] = useState<SpreadDashboard | null>(null);
  const [market, setMarket] = useState<SpreadMarket | null>(null);
  const [chart, setChart] = useState<SpreadChart | null>(null);
  const [interval, setIntervalValue] = useState("1hour");
  const [expiry, setExpiry] = useState("");
  const [strategy, setStrategy] = useState<Strategy>("BEAR_CALL");
  const [shortStrike, setShort] = useState("");
  const [longStrike, setLong] = useState("");
  const [lots, setLots] = useState("1");
  const [level, setLevel] = useState("");
  const [reason, setReason] = useState("");
  const [confirmations, setConfirmations] = useState({ trend_confirmed: false, candle_confirmed: false, event_clear: false });
  const [preview, setPreview] = useState<SpreadPreview | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [error, setError] = useState("");
  const [marketError, setMarketError] = useState("");
  const [chartError, setChartError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState("");
  const [premiumMarks, setPremiumMarks] = useState<SpreadDashboard["marks"]>([]);
  const [premiumError, setPremiumError] = useState("");
  const [exitTrade, setExitTrade] = useState<SpreadTrade | null>(null);
  const [exitReason, setExitReason] = useState("MANUAL");
  const [exitNotes, setExitNotes] = useState("");
  const pendingId = useRef({ signature: "", id: "" });
  const previewSignature = useRef("");
  const loadingDesk = useRef(false);
  const loadingMarket = useRef(false);
  const marketEpoch = useRef(0);

  const refreshDesk = useCallback(async () => {
    if (loadingDesk.current) return;
    loadingDesk.current = true;
    try { setDesk(await spreadApi.dashboard()); setError(""); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not load paper account"); }
    finally { loadingDesk.current = false; }
  }, []);
  const refreshMarket = useCallback(async () => {
    if (loadingMarket.current) return;
    const epoch = marketEpoch.current;
    loadingMarket.current = true;
    try {
      const data = await spreadApi.market(expiry);
      if (epoch !== marketEpoch.current) return;
      setMarket(data); setMarketError("");
      if (!expiry && data.expiry) { marketEpoch.current++; setExpiry(data.expiry); }
    } catch (e) { if (epoch === marketEpoch.current) setMarketError(e instanceof Error ? e.message : "Market unavailable"); }
    finally { loadingMarket.current = false; }
  }, [expiry]);
  useEffect(() => { refreshDesk(); const timer = window.setInterval(refreshDesk, 5000); return () => clearInterval(timer); }, [refreshDesk]);
  useEffect(() => { refreshMarket(); const timer = window.setInterval(refreshMarket, 10000); return () => clearInterval(timer); }, [refreshMarket]);
  const settingsSignature = JSON.stringify(desk?.settings);
  useEffect(() => {
    let alive = true;
    previewSignature.current = "";
    const load = async () => {
      try { const data = await spreadApi.chart(interval); if (alive) { setChart(data); setChartError(""); } }
      catch (e) { if (alive) setChartError(e instanceof Error ? e.message : "Chart unavailable"); }
    };
    load(); const timer = window.setInterval(load, 60000);
    return () => { alive = false; clearInterval(timer); };
  }, [interval]);
  const watchKeys = useMemo(() => ["NSE_INDEX|Nifty 50", ...(desk?.trades.filter(t => t.status === "OPEN").flatMap(t => [t.short.key, t.long.key]) || [])], [desk?.trades]);
  useLiveMarket(watchKeys, refreshDesk);

  const side = strategy === "BEAR_CALL" ? "CE" : "PE";
  const options = useMemo(() => market?.expiry === expiry ? (market?.options || []).filter(o => o.type === side).sort((a, b) => a.strike - b.strike) : [], [market, expiry, side]);
  const hedges = options.filter(o => strategy === "BEAR_CALL" ? o.strike - Number(shortStrike) >= 100 && o.strike - Number(shortStrike) <= 300 : Number(shortStrike) - o.strike >= 100 && Number(shortStrike) - o.strike <= 300);
  useEffect(() => {
    if (!options.length) { setShort(""); setLong(""); return; }
    if (!options.some(o => String(o.strike) === shortStrike)) {
      const shortlist = options.filter(o => o.delta != null && Math.abs(o.delta) >= .15 && Math.abs(o.delta) <= .25);
      const candidate = [...shortlist].sort((a, b) => Math.abs(Math.abs(a.delta!) - .2) - Math.abs(Math.abs(b.delta!) - .2))[0];
      setShort(candidate ? String(candidate.strike) : "");
    }
  }, [options, shortStrike]);
  useEffect(() => {
    if (!shortStrike) { setLong(""); return; }
    if (!hedges.some(o => String(o.strike) === longStrike)) {
      const preferred = [...hedges].sort((a, b) => Math.abs(Math.abs(a.strike - Number(shortStrike)) - 200) - Math.abs(Math.abs(b.strike - Number(shortStrike)) - 200))[0];
      setLong(preferred ? String(preferred.strike) : "");
    }
  }, [shortStrike, longStrike, options, strategy]);

  const ticket = useMemo(() => ({ strategy, expiry, short_strike: Number(shortStrike), long_strike: Number(longStrike), lots: Number(lots), level: Number(level), entry_reason: reason, ...confirmations }), [strategy, expiry, shortStrike, longStrike, lots, level, reason, confirmations]);
  const signature = JSON.stringify(ticket);
  const validTicket = Boolean(expiry && shortStrike && longStrike && Number(level) > 0 && Number.isInteger(Number(lots)) && Number(lots) >= 1 && reason.trim().length >= 5);
  useEffect(() => {
    let alive = true;
    setPreview(null);
    if (!validTicket) { setPreviewing(false); return; }
    setPreviewing(true);
    const timer = setTimeout(async () => {
      try { const result = await spreadApi.preview({ ...ticket, request_id: "preview-only" }); if (alive) { setPreview(result); previewSignature.current = signature; } }
      catch (e) { if (alive) setError(e instanceof Error ? e.message : "Preview failed"); }
      finally { if (alive) setPreviewing(false); }
    }, 450);
    return () => { alive = false; clearTimeout(timer); };
  }, [signature, validTicket, market?.quote_at, settingsSignature]);

  const sendOrder = async () => {
    if (busy || previewing || !preview?.eligible || previewSignature.current !== signature) return;
    setBusy(true); setNotice("");
    if (pendingId.current.signature !== signature) pendingId.current = { signature, id: crypto.randomUUID() };
    try {
      const order = await spreadApi.enter({ ...ticket, request_id: pendingId.current.id });
      setNotice(order.status === "FILLED" ? `Paper spread opened · ${order.id.slice(0, 8)} · both legs recorded.` : "Entry rejected by current server checks. The rejected order is saved in the order log.");
      if (order.status === "FILLED") { setConfirmations({ trend_confirmed: false, candle_confirmed: false, event_clear: false }); setReason(""); setTab("positions"); }
      else { pendingId.current = { signature: "", id: "" }; setPreview(null); }
      await refreshDesk();
    } catch (e) { setError(e instanceof Error ? e.message : "Entry failed"); }
    finally { setBusy(false); }
  };
  const closeSpread = async () => {
    if (!exitTrade) return;
    setBusy(true);
    try {
      const result = await spreadApi.close(exitTrade.id, exitReason, exitNotes);
      setNotice(result.status === "CLOSED" ? `Spread closed · ${money(result.net_pnl, true)} after costs.` : "Exit request saved. The monitor will retry when the session and both leg quotes are usable.");
      setExitTrade(null); await refreshDesk();
    } catch (e) { setError(e instanceof Error ? e.message : "Close failed"); }
    finally { setBusy(false); }
  };

  const summary = desk?.summary;
  const monitorStale = Boolean(desk && (!desk.monitor.at || new Date(desk.checked_at).getTime() - new Date(desk.monitor.at).getTime() > 45000));
  const trackedTrade = desk?.trades.find(t => t.id === selectedTrade) || desk?.trades.find(t => t.status === "OPEN") || desk?.trades[0];
  useEffect(() => {
    let alive = true, loading = false;
    setPremiumMarks([]); setPremiumError("");
    if (!trackedTrade) return;
    const tradeId = trackedTrade.id;
    const load = async () => {
      if (loading) return;
      loading = true;
      try { const data = await spreadApi.marks(tradeId); if (alive) { setPremiumMarks(data); setPremiumError(""); } }
      catch { if (alive) setPremiumError("Spread observations could not refresh. The backend monitor continues independently."); }
      finally { loading = false; }
    };
    load(); const timer = window.setInterval(load, 5000);
    return () => { alive = false; clearInterval(timer); };
  }, [trackedTrade?.id]);
  const payoffOption = useMemo<EChartsOption>(() => ({ ...baseChart, xAxis: { type: "value", name: "NIFTY at expiry", nameLocation: "middle", nameGap: 28, splitLine: { show: false } }, yAxis: { type: "value", name: "Net P&L · ₹", splitLine: { lineStyle: { color: "#1d2836" } } },
    series: preview?.credit != null ? [{ type: "line", showSymbol: false, lineStyle: { color: "#2DD4A8", width: 2.5 }, data: payoff(strategy, Number(shortStrike), Number(longStrike), preview.credit, preview.qty, preview.round_trip_fees), markLine: { silent: true, symbol: "none", lineStyle: { color: "#8B9AAB", type: "dashed" }, data: [{ yAxis: 0 }] } }] : [] }), [preview, strategy, shortStrike, longStrike]);
  const priceOption = useMemo<EChartsOption>(() => {
    const candles = chart?.candles || [], ema = new Map(chart?.ema.map(p => [p.ts, p.value]));
    return { ...baseChart, grid: { left: 65, right: 75, top: 28, bottom: 55 },
      xAxis: { type: "category", data: candles.map(c => ist(c.ts)), boundaryGap: true, axisLabel: { formatter: (value: string) => interval === "1day" ? value.slice(0, 6) : value.slice(8, 13) }, axisLine: { lineStyle: { color: "#243041" } } },
      dataZoom: [{ type: "inside", start: 30, end: 100 }, { type: "slider", height: 16, bottom: 6, borderColor: "#243041", textStyle: { color: "#8B9AAB" } }],
      series: [{ name: "NIFTY 50", type: "candlestick", data: candles.map(c => [c.open, c.close, c.low, c.high]), itemStyle: { color: "#2DD4A8", color0: "#F07178", borderColor: "#2DD4A8", borderColor0: "#F07178" },
        markLine: { silent: true, symbol: "none", label: { color: "#8B9AAB", formatter: "{b}" }, data: [...(Number(level) > 0 ? [{ yAxis: Number(level), name: "S/R level", lineStyle: { color: "#E5C07B", type: "dashed" as const } }] : []), ...(Number(shortStrike) > 0 ? [{ yAxis: Number(shortStrike), name: "Short", lineStyle: { color: "#F07178", type: "dotted" as const } }] : [])] } },
        { name: "20 EMA · closed bars", type: "line", showSymbol: false, connectNulls: false, data: candles.map(c => ema.get(c.ts) ?? null), lineStyle: { color: "#61AFEF", width: 1.5 } } ] };
  }, [chart, interval, level, shortStrike]);
  const premiumOption: EChartsOption = { ...baseChart, xAxis: { type: "time", axisLabel: { formatter: (value: number) => new Date(value).toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false }) } }, yAxis: { type: "value", name: "Closing debit · pts", splitLine: { lineStyle: { color: "#1d2836" } } }, series: [{ type: "line", showSymbol: premiumMarks.length < 2, data: premiumMarks.map(m => [m.ts, m.debit]), lineStyle: { color: "#61AFEF" }, markLine: trackedTrade ? { symbol: "none", label: { formatter: "{b}", color: "#8B9AAB" }, data: [{ yAxis: trackedTrade.target_debit, name: "Target", lineStyle: { color: "#2DD4A8" } }, { yAxis: trackedTrade.stop_debit, name: "Stop", lineStyle: { color: "#F07178" } }, { yAxis: trackedTrade.credit, name: "Entry", lineStyle: { color: "#8B9AAB" } }] } : undefined }] };
  const equityOption: EChartsOption = { ...baseChart, xAxis: { type: "time" }, yAxis: { type: "value", scale: true, name: "Account equity · ₹", splitLine: { lineStyle: { color: "#1d2836" } } }, series: [{ type: "line", showSymbol: true, data: desk?.equity_curve.map(p => [p.ts, p.equity]) || [], lineStyle: { color: "#2DD4A8" }, areaStyle: { color: "rgba(45,212,168,.07)" } }] };
  const drawdownOption: EChartsOption = { ...baseChart, xAxis: { type: "time" }, yAxis: { type: "value", name: "Realized drawdown · ₹", splitLine: { lineStyle: { color: "#1d2836" } } }, series: [{ type: "line", showSymbol: true, data: desk?.equity_curve.map(p => [p.ts, -p.drawdown]) || [], lineStyle: { color: "#F07178" }, areaStyle: { color: "rgba(240,113,120,.15)" } }] };

  return <div className="spread-desk">
    <div className="spread-heading"><div><div className="spread-eyebrow">STRATEGY LAB / PAPER ACCOUNT</div><h2>NIFTY Credit Spreads <span>v1.0</span></h2><p>Defined risk. Clear rules. Every decision recorded.</p></div><div className="spread-heading-actions"><span className="badge warn">PAPER ONLY</span><button onClick={() => { refreshDesk(); refreshMarket(); }}>↻ Refresh</button><button onClick={() => setShowSettings(true)}>Account settings</button></div></div>
    <div className="spread-feed"><span><i className={`dot ${market?.session.active && market?.options_session.active ? "ok" : "warn"}`} />{market?.session.active && market?.options_session.active ? "Market open" : market?.session.phase === "closed" ? "Market closed" : "Checking exchange session"}</span><span>Bid/ask depth · {ist(market?.quote_at)}</span><span>Account refresh 5s · depth up to 60s</span><span className="spread-monitor">Exit monitor · {ist(desk?.monitor.at)}</span></div>
    {error && <div className="error-box" role="alert">{error}</div>}
    {notice && <div className="spread-notice" role="status">{notice}<button aria-label="Dismiss notification" onClick={() => setNotice("")}>×</button></div>}
    {summary?.marks_stale && <div className="spread-warning">Some open spread marks are stale or unavailable. P&L uses the last usable observation; exits wait for executable quotes.</div>}
    {monitorStale && <div className="spread-warning">The exit monitor has not completed a check recently. Keep the backend running; automatic exits are delayed until it resumes.</div>}
    <div className="spread-metrics">
      <Stat label="Paper equity" value={money(summary?.equity)} note={`Starting capital ${money(desk?.settings.capital)}`} />
      <Stat label="Net P&L" value={summary ? money(summary.unrealized_pnl == null ? null : summary.realized_pnl + summary.unrealized_pnl, true) : "—"} tone={summary && summary.realized_pnl + (summary.unrealized_pnl || 0) < 0 ? "neg" : "pos"} note={`Realized ${money(summary?.realized_pnl, true)}`} />
      <Stat label="Open risk / 2% budget" value={money(summary?.open_risk)} note={`Limit ${money(summary?.risk_limit)} · ${summary?.open_count ?? 0} open`} />
      <Stat label="Closed trades" value={`${summary?.closed_count ?? 0} / 50`} note="First validation milestone" />
      <Stat label="Win rate" value={summary?.win_rate == null ? "—" : `${points(summary.win_rate, 1)}%`} note="After configured costs" />
    </div>
    <nav className="spread-tabs" aria-label="Credit spread workspace">{[["workspace", "Trade workspace"], ["positions", `Positions (${summary?.open_count ?? 0})`], ["journal", "Journal & analytics"], ["orders", "Order log"], ["rules", "Strategy rules"]].map(([key, label]) => <button key={key} className={tab === key ? "active" : ""} onClick={() => setTab(key)}>{label}</button>)}</nav>

    {tab === "workspace" && <>
      <div className="spread-workspace">
        <div className="spread-chart-stack">
          <Panel title="NIFTY 50 · market structure" extra={<div className="spread-segmented">{[["1day", "Daily"], ["1hour", "1 hour"], ["15minute", "15 min"]].map(([value, label]) => <button key={value} className={interval === value ? "active" : ""} onClick={() => { setChart(null); setIntervalValue(value); }}>{label}</button>)}</div>}>
            <div className="spread-chart-meta"><strong>{points(market?.spot)}</strong><span className="spread-ema">● 20 EMA {points(chart?.ema_value)}</span><span>{chart?.trend ? `${chart.trend} · completed bar` : "Awaiting candles"}</span></div>
            {chartError ? <div className="empty-note">{chartError}</div> : chart?.candles.length ? <EChartPanel option={priceOption} height={355} /> : <div className="spread-empty-chart">Loading retained market candles…</div>}
            <div className="spread-footnote">All chart times IST · EMA uses completed candles · zoom or drag to inspect.</div>
          </Panel>
          <div className="spread-small-charts">
            <Panel title="Expiry payoff" extra={<span className="muted">After estimated costs</span>}>{preview?.credit != null ? <EChartPanel option={payoffOption} height={230} /> : <div className="spread-empty-chart small">Complete the ticket to inspect risk and reward.</div>}<div className="spread-footnote">Expiry scenario; intraday value changes with time and volatility.</div></Panel>
            <Panel title="Spread debit monitor" extra={desk?.trades.length ? <select aria-label="Spread to chart" value={trackedTrade?.id || ""} onChange={e => setSelectedTrade(e.target.value)}>{desk.trades.map(t => <option key={t.id} value={t.id}>{t.short_strike}/{t.long_strike} · {t.status.toLowerCase()}</option>)}</select> : undefined}>{premiumError && <div className="spread-warning">{premiumError}</div>}{premiumMarks.length ? <EChartPanel option={premiumOption} height={230} /> : <div className="spread-empty-chart small">Executable spread observations appear after entry.</div>}<div className="spread-footnote">Latest 3,000 captured debits · target and stop apply to the net spread.</div></Panel>
          </div>
        </div>
        <Panel title="Build a paper spread" className="spread-ticket" extra={<span className="badge">2 legs · overnight allowed</span>}>
          <div className="panel-body">
            <div className="spread-strategies">{(["BEAR_CALL", "BULL_PUT"] as Strategy[]).map(s => <button key={s} className={strategy === s ? "active" : ""} onClick={() => { setStrategy(s); setShort(""); setLong(""); setConfirmations({ trend_confirmed: false, candle_confirmed: false, event_clear: false }); setLevel(""); }}><span>{s === "BEAR_CALL" ? "↘" : "↗"}</span>{names[s]}<small>{s === "BEAR_CALL" ? "Bearish / neutral-bearish" : "Bullish / neutral-bullish"}</small></button>)}</div>
            {(marketError || market?.error) && <div className="spread-warning">{marketError || market?.error}</div>}
            <label className="spread-field">Expiry<select value={expiry} onChange={e => { marketEpoch.current++; setExpiry(e.target.value); setPreview(null); setShort(""); setLong(""); }}>{!market?.expiries.length && <option value="">Awaiting listed contracts</option>}{market?.expiries.map(e => <option key={e.date} value={e.date} disabled={e.dte < 7 || e.dte > 21}>{e.date} · {e.dte} DTE{e.dte < 7 || e.dte > 21 ? " · outside rules" : ""}</option>)}</select></label>
            <div className="spread-leg-input"><span className="neg">SELL</span><label className="spread-field">Short {side}<select value={shortStrike} onChange={e => setShort(e.target.value)}><option value="">Select short strike</option>{options.map(o => <option key={o.key} value={o.strike}>{points(o.strike, 0)} · Δ {points(o.delta, 3)} · bid {points(o.bid)}</option>)}</select></label></div>
            <div className="spread-leg-input"><span className="pos">BUY</span><label className="spread-field">Protective {side}<select value={longStrike} onChange={e => setLong(e.target.value)}><option value="">Select hedge</option>{hedges.map(o => <option key={o.key} value={o.strike}>{points(o.strike, 0)} · ask {points(o.ask)}</option>)}</select></label></div>
            <div className="spread-input-grid"><label className="spread-field">Lots<input type="number" min="1" max="1000" step="1" value={lots} onChange={e => setLots(e.target.value)} /></label><label className="spread-field">{strategy === "BEAR_CALL" ? "Resistance" : "Support"} level<input type="number" min="1" step="0.05" placeholder="From 1-hour chart" value={level} onChange={e => setLevel(e.target.value)} /></label></div>
            <label className="spread-field">Entry thesis<textarea rows={2} maxLength={2000} placeholder="Structure, level and confirmation candle…" value={reason} onChange={e => setReason(e.target.value)} /></label>
            <div className="spread-attestations">{[["trend_confirmed", "1-hour structure agrees; direction is clear"], ["candle_confirmed", "15-minute confirmation candle has closed"], ["event_clear", "Reviewed major events and overnight gap risk"]].map(([key, label]) => <label key={key}><input type="checkbox" checked={confirmations[key as keyof typeof confirmations]} onChange={e => setConfirmations(c => ({ ...c, [key]: e.target.checked }))} />{label}</label>)}</div>
            <div className="spread-ticket-numbers"><div><span>Entry credit</span><strong>{points(preview?.credit)} <small>pts</small></strong></div><div><span>Quantity</span><strong>{preview?.qty ?? "—"} <small>units</small></strong></div><div><span>Max gross profit</span><strong className="pos">{money(preview?.max_profit)}</strong></div><div><span>Max gross loss</span><strong className="neg">{money(preview?.max_loss)}</strong></div><div><span>Target debit / 50%</span><strong>{points(preview?.target_debit)}</strong></div><div><span>Stop debit / 2×</span><strong>{points(preview?.stop_debit)}</strong></div></div>
            <div className="spread-footnote">Lot size {preview?.lot_size || "from contract master"} · round-trip fees {money(preview?.round_trip_fees)} · slippage {points(desk?.settings.slippage)} pts per leg.</div>
            <button className="primary spread-submit" disabled={!preview?.eligible || previewing || busy || Boolean(error || marketError)} onClick={sendOrder}>{busy ? "Recording paper order…" : previewing ? "Checking rules…" : preview?.eligible ? "Open paper spread →" : "Entry blocked · complete all checks"}</button>
            <div className="spread-footnote">Simulated fills at sell bid / buy ask, adjusted for slippage. The server rechecks risk before recording both legs.</div>
          </div>
        </Panel>
      </div>
      <Panel title="Pre-entry checklist" extra={<span className={`badge ${preview?.eligible ? "live" : "warn"}`}>{preview ? `${preview.checks.filter(c => c.passed).length} / ${preview.checks.length} passed` : "Awaiting complete ticket"}</span>}><div className="spread-checks">{preview ? preview.checks.map(c => <div key={c.code} className={c.passed ? "passed" : "blocked"} title={c.detail}><span>{c.passed ? "✓" : "○"}</span><div><strong>{c.label}</strong><small>{c.detail}</small></div></div>) : <div className="empty-note">Choose both legs, enter the chart level and entry thesis to evaluate all strategy rules. Check the three manual confirmations after reviewing the charts and events.</div>}</div></Panel>
    </>}

    {tab === "positions" && <Panel title="Open spreads" extra={<span className="badge">Automatic exits {desk?.settings.auto_exit ? "on" : "off"}</span>}><div className="spread-position-list">{desk?.trades.filter(t => t.status === "OPEN").length ? desk.trades.filter(t => t.status === "OPEN").map(t => <article className="spread-position" key={t.id}><div className="spread-position-title"><div><h3>{names[t.strategy]} <span>{t.short_strike} / {t.long_strike}</span></h3><span className="muted">{t.expiry} · {t.lots} lot(s) × {t.lot_size} · opened {ist(t.created_at)}</span></div><span className={`badge ${t.mark_fresh ? "live" : "warn"}`}>{t.exit_requested ? "Exit queued" : t.mark_fresh ? "Current mark" : "Awaiting executable mark"}</span></div><div className="spread-position-stats"><Stat label="Entry credit" value={`${points(t.credit)} pts`} /><Stat label="Closing debit" value={`${points(t.last_debit)} pts`} /><Stat label="Net MTM · estimated exit fees" value={money(t.unrealized_pnl, true)} tone={(t.unrealized_pnl ?? 0) < 0 ? "neg" : "pos"} /><Stat label="Risk reserved" value={money(t.risk_reserved)} /><Stat label="Target / stop debit" value={`${points(t.target_debit)} / ${points(t.stop_debit)}`} /></div><div className="spread-position-bottom"><span className="muted">Mark {ist(t.mark_at)} · close by 2 DTE{t.mark_error ? ` · ${t.mark_error}` : ""}</span><button disabled={busy || Boolean(t.exit_requested)} onClick={() => { setExitTrade(t); setExitReason("MANUAL"); setExitNotes(""); }}>Close both legs</button></div></article>) : <div className="spread-empty"><strong>No open spreads</strong><p>Your next paper trade starts with the entry checklist.</p><button onClick={() => setTab("workspace")}>Go to trade workspace →</button></div>}</div>{desk?.monitor.error && <div className="spread-warning">Monitor: {desk.monitor.error}</div>}</Panel>}

    {tab === "journal" && <>
      <div className="spread-metrics"><Stat label="Expectancy / closed trade" value={money(summary?.expectancy, true)} /><Stat label="Return on theoretical risk" value={summary?.return_on_risk == null ? "—" : `${points(summary.return_on_risk)}%`} /><Stat label="Max realized drawdown" value={money(summary?.max_drawdown)} /><Stat label="Profit factor" value={points(summary?.profit_factor)} note="Unavailable until a net loss is observed" /><Stat label="Recorded fees" value={money(summary?.fees)} /></div>
      <div className="spread-small-charts"><Panel title="Realized equity curve" extra={<span className="muted">After all configured fees</span>}>{desk?.equity_curve.length ? <EChartPanel option={equityOption} height={260} /> : <div className="spread-empty-chart small">The equity curve begins with your first closed spread.</div>}</Panel><Panel title="Drawdown" extra={<span className="muted">Closed-trade equity only</span>}>{desk?.equity_curve.length ? <EChartPanel option={drawdownOption} height={260} /> : <div className="spread-empty-chart small">Drawdown appears as closed trades accumulate.</div>}</Panel></div>
      <Panel title="Trade journal" extra={<a className="spread-download" href="/api/credit-spreads/export?kind=trades" download>↓ Export CSV</a>}><div className="table-wrap"><table className="data"><thead><tr>{["Opened / closed · IST", "Strategy / strikes", "Expiry / DTE", "Δ / IV", "Credit → debit", "Risk / net P&L", "MAE / MFE", "Reason / status"].map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>{desk?.trades.map(t => <tr key={t.id}><td>{ist(t.created_at)}<small>{ist(t.closed_at)}</small></td><td>{names[t.strategy]}<small>{t.short_strike} / {t.long_strike} · {t.width} pts · {t.lots} lots</small></td><td>{t.expiry}<small>{t.dte} DTE at entry</small></td><td>{points(t.entry_delta, 3)}<small>IV {points(t.entry_iv)}%</small></td><td>{points(t.credit)} → {points(t.exit_debit ?? t.last_debit)}<small>Fees {money(t.entry_fees + (t.exit_fees || 0))}</small></td><td>{money(t.risk_reserved)}<small className={(t.status === "CLOSED" ? t.net_pnl : t.unrealized_pnl || 0) < 0 ? "neg" : "pos"}>{money(t.status === "CLOSED" ? t.net_pnl : t.unrealized_pnl, true)}</small></td><td>{money(t.mae)}<small>{money(t.mfe)}</small></td><td className="spread-thesis">{t.entry_reason}<small>{t.exit_reason || t.status}{t.exit_requested?.notes ? ` · ${t.exit_requested.notes}` : ""}</small><details><summary>Entry checks</summary>{t.entry_checks.map(c => <p key={c.code}>{c.passed ? "✓" : "○"} {c.label}</p>)}</details></td></tr>)}</tbody></table>{!desk?.trades.length && <div className="empty-note">No journal entries yet. Entries, exits, fees and observed excursions are saved automatically.</div>}</div><div className="spread-footnote">MAE/MFE use captured executable marks after estimated fees. They may miss movements between captures. Validate across 50–100 trades and multiple market regimes.</div></Panel>
    </>}

    {tab === "orders" && <Panel title="Paper order audit log" extra={<a className="spread-download" href="/api/credit-spreads/export?kind=orders" download>↓ Export orders CSV</a>}><div className="table-wrap"><table className="data"><thead><tr>{["Recorded · IST", "Order / spread", "Action", "Leg fills", "Net points", "Fees", "Status / reason"].map(h => <th key={h}>{h}</th>)}</tr></thead><tbody>{desk?.orders.map(o => <tr key={o.id}><td>{ist(o.created_at)}<small>Quote {ist(o.quote_at)}</small></td><td className="mono">{o.id.slice(0, 8)}<small>{o.trade_id?.slice(0, 8) || "No spread opened"}</small></td><td>{o.action.replaceAll("_", " ")}</td><td>{o.legs.length ? o.legs.map(l => <div key={l.key}><span className={l.side === "BUY" ? "pos" : "neg"}>{l.side}</span> {l.qty} × {points(l.price)}<small>{l.key}</small></div>) : "—"}</td><td>{points(o.net_price)}</td><td>{money(o.fees)}</td><td><span className={`badge ${o.status === "FILLED" ? "live" : "warn"}`}>{o.status}</span><small>{o.reason}</small>{o.status === "REJECTED" && <details><summary>Failed checks</summary>{o.checks?.filter(c => !c.passed).map(c => <p key={c.code}>{c.label}: {c.detail}</p>)}</details>}</td></tr>)}</tbody></table>{!desk?.orders.length && <div className="empty-note">No orders recorded. Filled entries, rejected entries, exit requests and filled exits appear here.</div>}</div><div className="spread-footnote">Latest 500 order records shown. Both leg fills share one transaction and spread ID. Queued exit requests retain their original audit record; a separate exit fill records completion.</div></Panel>}

    {tab === "rules" && <div className="spread-rules"><Panel title="NIFTY Credit Spread Trading System · version 1.0"><div className="panel-body"><p>Rules supplied in your strategy document. Bear call spreads are primary; bull put spreads are used for bullish structure. Daily provides context, 1-hour establishes direction and levels, and a completed 15-minute candle confirms entry.</p><dl>{[["Entry window", "Monday–Thursday · 10:00–14:30 IST · verified open exchange session"], ["Contract selection", "Listed NIFTY expiry 7–21 calendar DTE · actual contract lot size · same expiry for both legs"], ["Short option", "OTM beyond identified resistance (call) or support (put) · absolute delta 0.15–0.25"], ["Spread", "100–300 points wide · net executable credit ≥ 15% of width"], ["Risk", "Maximum theoretical loss ≤ 1% per position, ≤ 2% combined; this desk also reserves estimated round-trip fees"], ["Profit target", "Buy back the spread at 50% of original credit"], ["Stop-loss", "Buy back the spread at 2× original credit, using actual available quotes even after a gap"], ["Other exits", "Close by 2 calendar DTE; request technical exit after a 1-hour close beyond the thesis level and a failed retest"], ["No averaging", "One open spread per direction; no adding lots to recover a loss"], ["Validation", "Record 50–100 trades · evaluate net expectancy, return on risk, and drawdown across regimes"]].map(([term, detail]) => <div key={term}><dt>{term}</dt><dd>{detail}</dd></div>)}</dl></div></Panel><Panel title="Execution and monitoring"><div className="panel-body"><p>All activity is simulated and persisted in PostgreSQL. Entry sells the short at bid and buys the hedge at ask; exits buy the short at ask and sell the hedge at bid. Slippage is applied adversely to each leg. Both legs require sufficient displayed quantity.</p><p>The backend checks open spreads every 10 seconds while the API is running. Bid/ask depth comes from the retained Upstox REST chain, normally refreshed once per minute; streaming price or Greek updates do not make older depth fresh. A gap may fill beyond the stop threshold. Unusable quotes defer an exit and remain visible.</p><p>Structure, the completed confirmation candle, event clearance and technical invalidation require your review. The automated trend gate uses the latest completed 1-hour close against its 20 EMA. Unknown, stale and closed-market data cannot create a fill.</p><p>Fees are an editable per-leg order estimate, not a live tax calculator. Equity and drawdown analytics use closed trades; current account equity also includes the latest available open-spread marks. Account assumptions are locked while a spread is open.</p><p>The supplied target/stop combination requires a win rate above 66.7% before charges if every exit hits its exact target or stop. The strategy remains a hypothesis to validate.</p><p className="muted">Contract metadata and market fields follow <a href="https://upstox.com/developer/api-documentation/get-pc-option-chain/" target="_blank" rel="noreferrer">Upstox option chain documentation ↗</a> and <a href="https://www.nseindia.com/static/products-services/equity-derivatives-contract-specifications" target="_blank" rel="noreferrer">NSE contract specifications ↗</a>.</p><Link className="spread-download" href="/paper">Open general paper orders →</Link></div></Panel></div>}

    {showSettings && desk && <SettingsModal settings={desk.settings} locked={desk.summary.open_count > 0} onCancel={() => setShowSettings(false)} onSave={async value => { await spreadApi.settings(value); setShowSettings(false); setNotice("Paper account settings saved."); await refreshDesk(); }} />}
    {exitTrade && <div className="spread-modal-backdrop"><section className="spread-modal" role="dialog" aria-modal="true" aria-labelledby="close-title"><h2 id="close-title">Close paper spread</h2><p>{names[exitTrade.strategy]} · {exitTrade.short_strike} / {exitTrade.long_strike} · {exitTrade.expiry}</p><label className="spread-field">Exit reason<select value={exitReason} onChange={e => setExitReason(e.target.value)}><option value="MANUAL">Manual exit</option><option value="TECHNICAL_INVALIDATION">Technical invalidation · 1-hour close + failed retest</option></select></label><label className="spread-field">Exit notes<textarea value={exitNotes} onChange={e => setExitNotes(e.target.value)} maxLength={2000} placeholder="Record the reason for closing…" /></label><p className="muted">The request is saved immediately. Both legs fill together when the exchange is open and quotes are usable.</p><div className="spread-modal-actions"><button disabled={busy} onClick={() => setExitTrade(null)}>Cancel</button><button className="primary" disabled={busy} onClick={closeSpread}>{busy ? "Recording…" : "Close paper spread"}</button></div></section></div>}
    <div className="spread-page-footer">NIFTY CREDIT SPREAD SYSTEM / V1.0<span>Paper execution · persistent journal · IST market clock</span></div>
  </div>;
}

function Stat({ label, value, note, tone = "" }: { label: string; value: string; note?: string; tone?: string }) {
  return <div className="spread-stat"><span>{label}</span><strong className={tone}>{value}</strong>{note && <small>{note}</small>}</div>;
}

function SettingsModal({ settings, locked, onCancel, onSave }: { settings: SpreadSettings; locked: boolean; onCancel: () => void; onSave: (settings: SpreadSettings) => Promise<void> }) {
  const [values, setValues] = useState(settings), [error, setError] = useState(""), [busy, setBusy] = useState(false);
  return <div className="spread-modal-backdrop"><form className="spread-modal" role="dialog" aria-modal="true" aria-labelledby="settings-title" onSubmit={async e => { e.preventDefault(); setBusy(true); try { await onSave(values); } catch (e) { setError(e instanceof Error ? e.message : "Save failed"); } finally { setBusy(false); } }}><h2 id="settings-title">Paper account settings</h2><p className="muted">Starting capital and assumed execution costs for this strategy.</p>{locked && <div className="spread-warning">Close open spreads before changing account assumptions.</div>}{error && <div className="error-box">{error}</div>}<label className="spread-field">Starting capital · ₹<input autoFocus type="number" min="1000" max="10000000000" required disabled={locked} value={values.capital} onChange={e => setValues(v => ({ ...v, capital: Number(e.target.value) }))} /></label><label className="spread-field">Estimated fee per leg order · ₹<input type="number" min="0" max="10000" step="0.01" required disabled={locked} value={values.fee_per_leg} onChange={e => setValues(v => ({ ...v, fee_per_leg: Number(e.target.value) }))} /></label><label className="spread-field">Adverse slippage per leg · points<input type="number" min="0" max="100" step="0.01" required disabled={locked} value={values.slippage} onChange={e => setValues(v => ({ ...v, slippage: Number(e.target.value) }))} /></label><label className="spread-checkbox"><input type="checkbox" disabled={locked} checked={values.auto_exit} onChange={e => setValues(v => ({ ...v, auto_exit: e.target.checked }))} />Automatically exit at target, stop or 2 DTE</label><p className="muted">Fee estimate applies once per leg order, regardless of lots. Enter an all-in estimate for brokerage and charges. Historical trade assumptions remain in the journal.</p><div className="spread-modal-actions"><button type="button" onClick={onCancel}>Cancel</button><button type="submit" className="primary" disabled={locked || busy}>{busy ? "Saving…" : "Save settings"}</button></div></form></div>;
}
