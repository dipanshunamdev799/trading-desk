"use client";

import { useEffect, useMemo, useState } from "react";
import AppShell from "@/components/AppShell";
import EChartPanel from "@/components/EChartPanel";
import ExpandableChartPanel from "@/components/ExpandableChartPanel";
import IpoFactorCard from "@/components/IpoFactorCard";
import { ipoDate, ipoNumber as n, safeIpoLink, visibleIpos } from "@/components/ipoResearch";
import { startMinutePolling } from "@/lib/minutePolling";
import { api, type IpoCatalogue, type IpoDetail, type IpoRow } from "@/lib/api";

const STAGES = [["active", "Upcoming & open"], ["announced", "Dates pending"], ["closed", "Awaiting listing"], ["listed", "Recent listings"], ["all", "All"]];
const GROUPS = ["Demand", "Structure", "Valuation", "Fundamentals", "Sentiment"];

function TrendChart({ detail, kind }: { detail: IpoDetail; kind: "gmp" | "demand" }) {
  const dated = kind === "gmp" ? detail.gmp_history : detail.subscription_history;
  const option = useMemo(() => ({
    backgroundColor: "transparent", animation: false,
    legend: { top: 4, textStyle: { color: "#8B9AAB" } },
    grid: { left: 68, right: 24, top: 46, bottom: 58 },
    tooltip: { trigger: "axis" as const, confine: true, backgroundColor: "#121820", borderColor: "#243041", textStyle: { color: "#E8EDF2" },
      valueFormatter: (value: unknown) => value == null ? "Unavailable" : `${kind === "gmp" ? "₹" : ""}${n(value)}${kind === "gmp" ? "" : "×"}` },
    xAxis: { type: "category" as const, data: dated.map(point => ipoDate(point.at, true)), axisLabel: { color: "#8B9AAB", hideOverlap: true } },
    yAxis: { type: "value" as const, name: kind === "gmp" ? "GMP (₹)" : "Subscription (×)", nameTextStyle: { color: "#8B9AAB" }, axisLabel: { color: "#8B9AAB" }, splitLine: { lineStyle: { color: "#243041" } } },
    series: kind === "gmp" ? [{ name: "Published GMP", type: "line" as const, data: detail.gmp_history.map(point => point.value), connectNulls: false, itemStyle: { color: "#E5C07B" } }]
      : ([['qib', '#2DD4A8'], ['nii', '#E5C07B'], ['retail', '#61AFEF'], ['total', '#B8A0E0']] as const).map(([key, color]) => ({ name: key.toUpperCase(), type: "line" as const,
        data: detail.subscription_history.map(point => point[key] ?? null), connectNulls: false, itemStyle: { color } })),
  }), [detail, kind, dated]);
  return <ExpandableChartPanel title={kind === "gmp" ? "GMP history" : "Day-wise subscription history"}>
    <div className="panel-header"><div><h2>{kind === "gmp" ? "GMP history" : "Day-wise subscription history"}</h2>
      <p className="maxpain-caption">{kind === "gmp" ? "Unofficial published observations · missing quotes stay empty" : "Publisher-dated observations only · QIB often builds late"}</p></div></div>
    <div className="panel-body">{dated.length ? <EChartPanel option={option} height={270} /> : <div className="chart-empty" style={{ height: 240 }}>{kind === "gmp" ? "No published GMP history for this IPO." : "No publisher-dated demand history available. Earlier bidding days are not reconstructed from today's totals."}</div>}</div>
  </ExpandableChartPanel>;
}

function DemandNumber({ row, id }: { row: IpoRow; id: string }) {
  const value = row.signals[id]?.value;
  if (value == null) return <span className="muted">{["upcoming", "announced"].includes(row.stage) ? "Pending" : "—"}</span>;
  return <span className="mono">{n(id === "nii" ? (value as { nii: number }).nii : value)}×</span>;
}

export default function IpoPage() {
  const [catalogue, setCatalogue] = useState<IpoCatalogue | null>(null);
  const [detail, setDetail] = useState<IpoDetail | null>(null);
  const [selected, setSelected] = useState("");
  const [stage, setStage] = useState("active");
  const [segment, setSegment] = useState("all");
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("date");
  const [refresh, setRefresh] = useState(0);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  useEffect(() => startMinutePolling({ live: true, load: api.ipos,
    onData: result => { setCatalogue(result); setError(null); },
    onError: reason => setError(reason instanceof Error ? reason.message : "IPO refresh failed"), onLoading: setLoading }), [refresh]);
  const rows = useMemo(() => visibleIpos(catalogue?.ipos || [], stage, segment, query, sort), [catalogue, stage, segment, query, sort]);
  useEffect(() => {
    if (!rows.some(row => row.id === selected)) setSelected(rows[0]?.id || "");
  }, [rows, selected]);
  useEffect(() => {
    setDetail(null); setDetailError(null);
    if (!selected) { setDetailLoading(false); return; }
    return startMinutePolling({ live: true, load: () => api.ipo(selected),
      onData: result => {
        if (result.company.id !== selected) { setDetailError("The IPO response does not match this selection."); return; }
        setDetail(result); setDetailError(null);
      }, onError: reason => setDetailError(reason instanceof Error ? reason.message : "IPO detail refresh failed"), onLoading: setDetailLoading });
  }, [selected, refresh]);
  const current = detail?.company.id === selected ? detail : null;
  const counts = useMemo(() => ({
    scheduled: catalogue?.ipos.filter(row => row.stage === "upcoming").length || 0,
    open: catalogue?.ipos.filter(row => row.stage === "open").length || 0,
    announced: catalogue?.ipos.filter(row => row.stage === "announced").length || 0,
    closed: catalogue?.ipos.filter(row => row.stage === "closed").length || 0,
  }), [catalogue]);
  const sourceErrors = catalogue?.sources.filter(source => source.error) || [];
  return <AppShell title="IPO research"><div className="stack ipo-page">
    <section className="panel ipo-intro"><div><span className="ipo-eyebrow">PRIMARY MARKET / INDIA</span><h2>IPO research desk</h2>
      <p>Demand, issue structure and fundamentals in one view. Follow the evidence behind each number.</p></div>
      <div className="ipo-sync"><span className={`badge ${error ? "warn" : "live"}`}>{error ? "Refresh failed · retained data" : loading ? "Checking sources…" : "Auto-refresh · 1 min"}</span>
        <span className="muted">{catalogue ? `Page checked ${ipoDate(catalogue.checked_at, true)} IST` : "Loading retained IPO universe…"}</span>
        <button type="button" disabled={loading || detailLoading} onClick={() => setRefresh(value => value + 1)}>Refresh</button></div></section>
    {error && <div className="error-box" role="status">{error}</div>}
    {sourceErrors.length > 0 && <div className="ipo-source-warning" role="status">Some sources could not refresh. Retained values keep their retrieval dates.
      <details><summary>Inspect source status ({sourceErrors.length})</summary>{sourceErrors.map(source => <p key={source.source}>{source.source}: {source.error}</p>)}</details></div>}
    <div className="metric-strip ipo-counts">{[["Scheduled launches", counts.scheduled], ["Bidding window open", counts.open], ["Dates not announced", counts.announced], ["Awaiting listing", counts.closed]].map(([label, value]) =>
      <div className="metric" key={label}><div className="label">{label}</div><div className="value">{value}</div></div>)}</div>
    <section className="panel"><div className="ipo-filterbar">
      <div className="ipo-tabs" role="group" aria-label="IPO stage">{STAGES.map(([key, label]) => <button type="button" key={key} aria-pressed={stage === key} className={stage === key ? "primary" : ""} onClick={() => setStage(key)}>{label}</button>)}</div>
      <div className="row"><label className="sr-only" htmlFor="ipo-search">Search IPOs</label><input id="ipo-search" type="search" placeholder="Search company or sector…" value={query} onChange={event => setQuery(event.target.value)} />
        <label className="sr-only" htmlFor="ipo-segment">IPO segment</label><select id="ipo-segment" value={segment} onChange={event => setSegment(event.target.value)}><option value="all">All segments</option><option value="regular">Mainboard</option><option value="sme">SME</option></select>
        <label className="sr-only" htmlFor="ipo-sort">Sort IPOs</label><select id="ipo-sort" value={sort} onChange={event => setSort(event.target.value)}><option value="date">Opening date</option><option value="qib">QIB demand ↓</option><option value="gmp">GMP premium ↓</option></select></div>
    </div><div className="ipo-universe-wrap"><table className="data ipo-universe"><thead><tr><th>Company / stage</th><th>Bid window</th><th className="num">Issue size</th><th className="num ipo-qib">QIB ×</th><th className="num">NII ×</th><th className="num">Retail ×</th><th className="num">Total ×</th><th className="num">GMP / premium</th><th>Evidence</th></tr></thead>
      <tbody>{rows.map(row => { const gmp = row.signals.gmp?.value as { rupees: number; percent: number | null } | null; return <tr key={row.id} className={selected === row.id ? "is-selected" : ""}>
        <td><button type="button" className="ipo-company-button" onClick={() => setSelected(row.id)} aria-pressed={selected === row.id}>{row.name}</button><div className="ipo-row-meta"><span className={`badge ${row.stage === "open" ? "live" : ""}`}>{row.stage === "announced" ? "Dates pending" : row.stage}</span><span>{row.issue_type === "sme" ? "SME" : "Mainboard"}{row.conflicts.length ? " · verify source differences" : ""}</span></div></td>
        <td className="mono">{row.bidding_start_date || "Not announced"}<br /><span className="muted">{row.bidding_end_date || ""}</span></td><td className="num">{row.issue_size == null ? "—" : `₹${n(row.issue_size)} Cr`}</td>
        <td className="num ipo-qib"><DemandNumber row={row} id="qib" /></td><td className="num"><DemandNumber row={row} id="nii" /></td><td className="num"><DemandNumber row={row} id="retail" /></td><td className="num"><DemandNumber row={row} id="total" /></td>
        <td className="num">{gmp ? <><span className="mono">₹{n(gmp.rupees)}</span><br /><small className={gmp.percent != null && gmp.percent < 0 ? "neg" : "pos"}>{gmp.percent == null ? "Price pending" : `${n(gmp.percent)}%`}</small></> : <span className="muted">Not quoted</span>}</td>
        <td><span className="mono">{row.coverage}/24</span><br /><small className="muted">{row.catalog_source === "Upstox" ? row.has_public_research ? "Upstox + public" : "Upstox" : "Public source"}</small></td></tr>; })}</tbody></table>
      {!rows.length && <div className="empty-note">{loading && !catalogue ? "Loading IPOs…" : "No IPOs match these filters. Try another stage or segment."}</div>}</div>
      <p className="ipo-table-note">QIB is the primary demand indicator. Bids can arrive late; early zeros are not a verdict. GMP is unofficial. Sources have their own update schedules.</p></section>
    <section className="ipo-research-heading"><div><span className="ipo-eyebrow">SELECTED ISSUE / 24-FACTOR VIEW</span><h2>{current?.company.name || rows.find(row => row.id === selected)?.name || "Select an IPO"}</h2></div>
      <span className="muted">{detailLoading ? "Checking detailed sources…" : current ? `${current.coverage}/24 factors populated · qualitative items may need review` : ""}</span></section>
    {detailError && <div className="error-box" role="status">{detailError}{current ? " · Showing the last successful detail response." : ""}</div>}
    {current && <>
      <section className="panel ipo-issue-summary"><div className="ipo-issue-facts"><div><span>Price band</span><strong>{current.company.minimum_price ? `₹${n(current.company.minimum_price)}–₹${n(current.company.maximum_price)}` : current.company.maximum_price ? `Upper price ₹${n(current.company.maximum_price)}` : "Not announced"}</strong></div>
        <div><span>Lot / minimum quantity</span><strong>{n(current.company.lot_size, 0)} / {n(current.company.minimum_quantity, 0)} shares</strong></div>
        <div><span>Minimum application at upper price</span><strong>{current.company.minimum_quantity && current.company.maximum_price ? `₹${n(current.company.minimum_quantity * current.company.maximum_price, 0)}` : "Not published"}</strong></div>
        <div><span>Listing / exchange</span><strong>{ipoDate(current.company.timeline?.listing_date)} · {current.company.listing_exchange || "Not published"}</strong></div></div>
        <div className="row">{[[current.company.rhp_url, "Read RHP"], [current.company.drhp_url, "Read DRHP"]].map(([url, label]) => safeIpoLink(url) ? <a key={label} className="ipo-document-link" href={safeIpoLink(url)} target="_blank" rel="noreferrer">{label} ↗</a> : null)}<span className="muted">{current.company.catalog_source} · {current.company.symbol || "Symbol pending"}</span></div></section>
      {current.conflicts.length > 0 && <div className="ipo-source-warning">{current.conflicts.map(conflict => <p key={conflict}>{conflict}</p>)}</div>}
      {current.source_errors.length > 0 && <div className="ipo-source-warning">Some detail sources failed to update. <details><summary>Inspect retained-source errors</summary>{current.source_errors.map(source => <p key={source.source}>{source.source}: {source.error}</p>)}</details></div>}
      {GROUPS.map(group => <section key={group} className="ipo-factor-section"><div className="ipo-group-heading"><h2>{group}</h2><span className="muted">{group === "Demand" ? "QIB first · compare bidding day and time" : group === "Sentiment" ? "Attribution and coverage matter" : "Read the period and source with each figure"}</span></div>
        <div className="ipo-factor-grid">{current.factors.filter(factor => factor.group === group).map(factor => <IpoFactorCard key={factor.id} factor={factor} />)}</div></section>)}
      <div className="grid-2"><TrendChart detail={current} kind="gmp" /><TrendChart detail={current} kind="demand" /></div>
      {!!current.financials.periods?.length && <section className="panel"><div className="panel-header"><h2>Published financial periods</h2><span className="muted">₹ crore · quarterly and annual periods shown separately</span></div><div className="table-wrap"><table className="data"><thead><tr><th>Measure</th>{current.financials.periods.map(period => <th className="num" key={period}>{period}</th>)}</tr></thead><tbody>{Object.entries(current.financials.rows || {}).map(([label, values]) => <tr key={label}><td>{label}</td>{values.map((value, index) => <td className="num" key={index}>{n(value)}</td>)}</tr>)}</tbody></table></div></section>}
      <section className="panel"><div className="panel-header"><h2>Collection history & additional Upstox inputs</h2></div><div className="panel-body ipo-extra">
        <details><summary>Collected subscription snapshots ({current.observations.filter(row => ['qib','nii','retail','total','total_subscription'].includes(row.metric)).length})</summary><p className="muted">Collection time is when this app observed the reading. A missing publisher date is not replaced with the collection date.</p><div className="table-wrap"><table className="data"><thead><tr><th>Collected (IST)</th><th>Publisher time</th><th>Source</th><th>Metric</th><th>Multiple</th></tr></thead><tbody>{current.observations.filter(row => ['qib','nii','retail','total','total_subscription'].includes(row.metric)).slice(-100).reverse().map((row, index) => <tr key={index}><td>{ipoDate(row.observed_at, true)}</td><td>{row.reported_at ? ipoDate(row.reported_at, true) : "Not supplied"}</td><td>{row.source}</td><td>{row.metric}</td><td>{n(row.value)}×</td></tr>)}</tbody></table></div></details>
        <details><summary>IPO timeline & registrar</summary><div className="ipo-timeline">{Object.entries(current.company.timeline || {}).filter(([,value]) => value).map(([key, value]) => <div key={key}><span className="muted">{key.replaceAll("_", " ")}</span><span>{value}</span></div>)}{Object.entries(current.company.registrar_info || {}).filter(([,value]) => value).map(([key,value]) => <div key={key}><span className="muted">Registrar · {key.replaceAll("_", " ")}</span><span>{value}</span></div>)}</div></details>
        <details><summary>All available Upstox fields</summary>{current.raw_upstox ? <pre>{JSON.stringify(current.raw_upstox, null, 2)}</pre> : <p className="muted">This IPO was discovered in the public feed and is not currently matched to an Upstox record.</p>}</details>
      </div></section>
    </>}
    {!current && detailLoading && <div className="panel panel-body muted" role="status">Loading sourced factors and retained history…</div>}
    <p className="ipo-footnote">Upcoming coverage includes scheduled launches and a separate undated announcement pipeline. Recent listing comparisons cover the retained Upstox cohort (up to 30 recent listings per refresh). No application or investment recommendation is generated.</p>
  </div></AppShell>;
}
