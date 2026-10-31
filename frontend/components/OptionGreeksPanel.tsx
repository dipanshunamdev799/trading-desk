"use client";

import { useMemo, useState } from "react";
import type { MaxPainGreeks, GreekProvenance, MaxPainSnapshot } from "@/lib/api";
import EChartPanel from "@/components/EChartPanel";
import ExpandableChartPanel from "@/components/ExpandableChartPanel";
import SnapshotChartPanel from "@/components/SnapshotChartPanel";
import { focusGreekStrike, formatGreek, greekChartOption, GREEK_LABELS, type GreekMetric } from "@/components/optionGreeksCharts";
import { downloadOptionGreeksCsv } from "@/lib/optionGreeksCsv";

function GreekCsvButton({ data, feedFresh, chart = false }: { data?: MaxPainGreeks; feedFresh?: boolean; chart?: boolean }) {
  return <button type="button" disabled={!data?.data_available || !data.rows.length}
    aria-label={chart ? "Download chart option Greeks CSV" : "Download option Greeks CSV"}
    title={data?.data_available ? `Download all ${data.rows.length} strikes, calls and puts, with snapshot timestamps` : "Option Greeks are unavailable for this selection"}
    onClick={() => { if (data?.data_available && data.rows.length) downloadOptionGreeksCsv(data, feedFresh); }}>Download CSV</button>;
}

function timestamp(value: string | null | undefined) {
  if (!value || !Number.isFinite(Date.parse(value))) return "Unavailable";
  return new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", dateStyle: "medium", timeStyle: "medium" }).format(new Date(value));
}

function sourceTitle(value: GreekProvenance | undefined, metric: GreekMetric) {
  if (!value) return undefined;
  const source = metric === "iv" ? value.iv_source : value.greeks_source;
  return `${source === "websocket" ? "Live feed" : "REST snapshot"} · ${timestamp(metric === "iv" ? value.iv_at : value.greeks_at)} IST`;
}

export default function OptionGreeksPanel({ data, asOf, expiry, loading, selectedStrike, onSelectStrike, feedFresh, chartContext }: {
  data?: MaxPainGreeks; asOf: string; expiry: string; loading: boolean;
  selectedStrike: number | null; onSelectStrike: (strike: number) => void;
  feedFresh?: boolean;
  chartContext?: { snapshot: MaxPainSnapshot | null; asOf: string; expiry: string; instrumentKey: string; dates: string[]; loading: boolean; refreshId: number };
}) {
  const [metric, setMetric] = useState<GreekMetric>("delta");
  const [range, setRange] = useState("near");
  const current = data?.as_of === asOf && data.expiry === expiry && (!chartContext || data.instrument_key === chartContext.instrumentKey) ? data : undefined;
  const rows = current?.rows || [];
  const focus = focusGreekStrike(rows, current?.spot ?? null, selectedStrike);
  const atm = focusGreekStrike(rows, current?.spot ?? null, null);
  const center = rows.findIndex(row => row.strike === focus);
  const visible = range === "all" ? rows : rows.slice(Math.max(0, center - 5), center + 6);
  const ready = current?.data_available;
  const header = current?.status === "live" ? feedFresh === false ? "Retained feed snapshot" : `${current.live_legs ?? 0} legs streamed` : current?.status === "latest_rest" ? "Latest available · market closed" : current?.status === "rest_fallback" ? "REST fallback" : current?.status === "historical" ? "Saved session snapshot" : current?.status === "retained" ? "Retained snapshot" : "Captured snapshot";
  return <section className="stack maxpain-greeks" aria-label="Option Greeks">
    <div className="panel">
      <div className="panel-header">
        <div><h2>Option Greeks</h2><p className="maxpain-caption">Delta · Gamma · Theta · Vega · IV · calls & puts</p><p className="maxpain-caption">Expiry {expiry || "—"} · as of {asOf} IST</p></div>
        <div className="row">{ready && <span className={`badge ${current.status === "retained" ? "warn" : "db"}`}>{current.available}/{current.required} legs with data · {header}</span>}
          <GreekCsvButton data={current} feedFresh={feedFresh} /></div>
      </div>
      {ready ? <>
        <div className="panel-body greek-controls">
          <div className="greek-source"><a href="https://upstox.com/developer/api-documentation/get-pc-option-chain/" target="_blank" rel="noreferrer">Upstox option chain ↗</a>
            <span>Captured {timestamp(current.observed_at)} IST</span><span>{current.reported_at ? `Latest feed timestamp ${timestamp(current.reported_at)} IST` : "Source Greek timestamp not supplied"}</span></div>
          <div className="row">
            <div className="field"><label htmlFor="greek-focus-strike">Focus strike</label><select id="greek-focus-strike" value={focus ?? ""} onChange={event => onSelectStrike(Number(event.target.value))}>{rows.map(row => <option key={row.strike} value={row.strike}>{row.strike.toLocaleString("en-IN")}{row.strike === atm && current.spot != null ? " · nearest spot" : ""}</option>)}</select></div>
            <div className="field"><label htmlFor="greek-table-range">Strike range</label><select id="greek-table-range" value={range} onChange={event => setRange(event.target.value)}><option value="near">Near focus (±5 strikes)</option><option value="all">All strikes</option></select></div>
          </div>
          {current.hint && <p className="greek-coverage" role="status">{current.hint}</p>}
          {current.status === "live" && feedFresh === false && <p className="greek-coverage" role="status">The live feed is unavailable or idle. Showing the last captured values while REST refreshes.</p>}
          {current.status === "historical" && <p className="greek-coverage">This is the latest snapshot saved that session, with its original capture time. It is not necessarily the closing Greeks.</p>}
          {current.status === "retained" && <p className="greek-coverage">Showing a previously captured snapshot. Check its capture time before comparing with newer OI or spot readings.</p>}
        </div>
        <div className="table-wrap greek-table-wrap"><table className="data greek-table">
          <caption className="sr-only">Per-option call and put Greeks by strike for {expiry} on {asOf}</caption>
          <thead><tr><th colSpan={5} className="greek-call">Call</th><th rowSpan={2} className="greek-strike">Strike</th><th colSpan={5} className="greek-put">Put</th></tr>
            <tr>{(["iv", "vega", "theta", "gamma", "delta"] as GreekMetric[]).map(key => <th key={`call-${key}`} className="num greek-call" scope="col">{GREEK_LABELS[key]}</th>)}{(["delta", "gamma", "theta", "vega", "iv"] as GreekMetric[]).map(key => <th key={`put-${key}`} className="num greek-put" scope="col">{GREEK_LABELS[key]}</th>)}</tr></thead>
          <tbody>{visible.map(row => <tr key={row.strike} className={row.strike === focus ? "is-selected" : undefined}>
            {(["iv", "vega", "theta", "gamma", "delta"] as GreekMetric[]).map(key => <td key={`call-${key}`} className="num mono" title={sourceTitle(row.call_provenance, key)}>{formatGreek(row.call[key], key)}</td>)}
            <th scope="row" className="greek-strike"><button type="button" aria-pressed={row.strike === focus} onClick={() => onSelectStrike(row.strike)}>{row.strike.toLocaleString("en-IN")}{row.strike === atm && current.spot != null && <small>nearest spot</small>}</button></th>
            {(["delta", "gamma", "theta", "vega", "iv"] as GreekMetric[]).map(key => <td key={`put-${key}`} className="num mono" title={sourceTitle(row.put_provenance, key)}>{formatGreek(row.put[key], key)}</td>)}
          </tr>)}</tbody>
        </table></div>
        <div className="panel-body greek-help"><p>{current.basis} Missing fields show —; a supplied zero remains zero.</p>
          <details><summary>What do these fields mean?</summary><p><strong>Delta</strong> describes premium sensitivity to the underlying price. <strong>Gamma</strong> describes how Delta changes. <strong>Theta</strong> describes time sensitivity. <strong>Vega</strong> describes volatility sensitivity. <strong>IV</strong> is implied volatility, rather than a Greek.</p><p>These are provider model values for individual options. Theta/Vega follow the provider’s scaling conventions. They are not an OI-weighted exposure or a directional forecast. Rho is not supplied by this option-chain endpoint.</p></details>
        </div>
      </> : <div className="chart-empty greek-empty" role="status">{loading ? "Loading option Greeks…" : current?.hint || "Option Greeks are unavailable for this selection."}</div>}
    </div>
    {chartContext ? <SnapshotChartPanel title="Option Greeks by strike" {...chartContext}>
      {({ snapshot, asOf: chartDate, loading: chartLoading }) => <GreekStrikeChart data={snapshot?.option_greeks} asOf={chartDate} expiry={expiry}
        loading={chartLoading} metric={metric} setMetric={setMetric} selectedStrike={selectedStrike} onSelectStrike={onSelectStrike} feedFresh={feedFresh} />}
    </SnapshotChartPanel> : ready && <ExpandableChartPanel title="Option Greeks by strike">
      <GreekStrikeChart data={current} asOf={asOf} expiry={expiry} loading={loading} metric={metric} setMetric={setMetric} selectedStrike={selectedStrike} onSelectStrike={onSelectStrike} feedFresh={feedFresh} />
    </ExpandableChartPanel>}
  </section>;
}

function GreekStrikeChart({ data, asOf, expiry, loading, metric, setMetric, selectedStrike, onSelectStrike, feedFresh }: {
  data?: MaxPainGreeks; asOf: string; expiry: string; loading: boolean; metric: GreekMetric;
  setMetric: (metric: GreekMetric) => void; selectedStrike: number | null; onSelectStrike: (strike: number) => void;
  feedFresh?: boolean;
}) {
  const current = data?.as_of === asOf && data.expiry === expiry ? data : undefined;
  const rows = current?.rows || [];
  const focus = focusGreekStrike(rows, current?.spot ?? null, selectedStrike);
  const option = useMemo(() => current?.data_available ? greekChartOption(current, metric, focus) : null, [current, metric, focus]);
  return <>
    <div className="panel-header"><div><h2>Option Greeks by strike</h2><p className="maxpain-caption">Per-option values · expiry {expiry} · as of {asOf || "—"} IST</p>
      {current?.observed_at && <p className="maxpain-caption">Captured {timestamp(current.observed_at)} IST</p>}</div>
      <div className="row"><div className="field"><label htmlFor="greek-chart-metric">Chart metric</label><select id="greek-chart-metric" value={metric} onChange={event => setMetric(event.target.value as GreekMetric)}>{Object.entries(GREEK_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select></div>
        <GreekCsvButton data={current} feedFresh={feedFresh} chart /></div></div>
    <div className="panel-body tight">{option ? <EChartPanel option={option} height={290} onClick={event => { const row = rows[event.dataIndex]; if (row) onSelectStrike(row.strike); }} />
      : <div className="chart-empty" style={{ height: 290 }}>{loading ? "Loading option Greeks…" : current?.hint || "Option Greeks are unavailable for this selection."}</div>}</div>
  </>;
}
