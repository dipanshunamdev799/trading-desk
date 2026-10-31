"use client";

import type { NiftyFactor } from "@/lib/niftyApi";

export function niftyNumber(value: unknown, digits = 2): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "Unavailable";
  const magnitude = Math.abs(value);
  if (magnitude > 0 && magnitude < 0.0000001) return value.toExponential(4).replace(/\.?0+e/, "e");
  return value.toLocaleString("en-IN", { maximumFractionDigits: magnitude > 0 && magnitude < 0.01 ? Math.max(digits, 8) : digits });
}

export function niftyDate(value: string | null | undefined, short = false): string {
  if (!value) return "Not supplied";
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata", day: "2-digit", month: "short", ...(short ? {} : { year: "numeric" }),
    hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(date);
}

export function factorStatusLabel(factor: NiftyFactor): string {
  return factor.quality === "unverified_units" ? "Units unverified" : factor.status === "missing" ? "Unavailable" : factor.status;
}

export function factorReportLabel(factor: NiftyFactor): string {
  if (factor.reporting_date) {
    const day = new Date(`${factor.reporting_date}T12:00:00+05:30`);
    if (Number.isFinite(day.getTime())) return `Session ${new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric" }).format(day)} · provisional`;
  }
  return factor.reported_at ? `Published ${niftyDate(factor.reported_at, true)} IST` : "Publisher time not supplied";
}

function cashContext(factor: NiftyFactor): Record<string, unknown> | null {
  return ["fii_cash", "dii_cash"].includes(factor.id) && factor.context != null && typeof factor.context === "object" && !Array.isArray(factor.context)
    ? factor.context as Record<string, unknown> : null;
}

export function CashFlowDetails({ factor }: { factor: NiftyFactor }) {
  const context = cashContext(factor);
  if (context?.unit_status !== "verified") return null;
  return <div className="nifty-cash-gross"><span>Buy ₹{niftyNumber(context.gross_buy_cr)} Cr</span><span>Sell ₹{niftyNumber(context.gross_sell_cr)} Cr</span></div>;
}

export function niftyLink(value: string | null | undefined): string | undefined {
  if (!value) return undefined;
  try { const url = new URL(value); return ["https:", "http:"].includes(url.protocol) ? url.href : undefined; }
  catch { return undefined; }
}

function textValue(value: unknown): string {
  if (value == null) return "Unavailable";
  if (typeof value === "number") return niftyNumber(value, 6);
  if (typeof value === "string") return value;
  if (typeof value === "boolean") return value ? "Yes" : "No";
  return JSON.stringify(value);
}

export function FactorValue({ value, unit, compact = false }: { value: unknown; unit?: string; compact?: boolean }) {
  if (value == null || (typeof value === "number" && !Number.isFinite(value))) return <span className="nifty-unavailable">Unavailable</span>;
  if (typeof value !== "object") return <>{typeof value === "number" ? niftyNumber(value) : textValue(value)}{unit && <small className="nifty-unit"> {unit}</small>}</>;
  if (Array.isArray(value)) {
    if (!value.length) return <span className="nifty-unavailable">No observations</span>;
    if (compact) return <>{value.length} <small className="nifty-unit">observations</small></>;
    const rows = value.filter(item => item !== null && typeof item === "object" && !Array.isArray(item)) as Record<string, unknown>[];
    if (rows.length === value.length) {
      const keys = Array.from(new Set(rows.flatMap(row => Object.keys(row))));
      return <div className="nifty-value-table"><table className="data"><thead><tr>{keys.map(key => <th key={key}>{key.replaceAll("_", " ")}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{keys.map(key => <td key={key}>{textValue(row[key])}</td>)}</tr>)}</tbody></table></div>;
    }
    return <ul className="nifty-value-list">{value.map((item, i) => <li key={i}>{textValue(item)}</li>)}</ul>;
  }
  const entries = Object.entries(value as Record<string, unknown>);
  if (compact) return <>{entries.length} <small className="nifty-unit">measures</small></>;
  return <dl className="nifty-value-dictionary">{entries.map(([key, item]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{item != null && typeof item === "object" ? <details><summary>{Array.isArray(item) ? `${item.length} observations` : "View measures"}</summary><FactorValue value={item} /></details> : textValue(item)}</dd></div>)}</dl>;
}

export function FactorChange({ factor }: { factor: NiftyFactor }) {
  const change = factor.change;
  const percent = factor.change_pct;
  const direction = percent ?? change;
  if (direction == null && cashContext(factor)?.unit_status === "verified" && typeof factor.value === "number") {
    return <span className={`nifty-change ${factor.value > 0 ? "pos" : factor.value < 0 ? "neg" : ""}`}>{factor.value > 0 ? "Net buying" : factor.value < 0 ? "Net selling" : "No net flow"}</span>;
  }
  return <span className={`nifty-change ${direction == null ? "" : direction > 0 ? "pos" : direction < 0 ? "neg" : ""}`}>
    {direction == null ? "Change unavailable" : <>{direction > 0 ? "↗" : direction < 0 ? "↘" : "→"} {change == null ? "" : `${change > 0 ? "+" : ""}${niftyNumber(change)}`}{percent == null ? "" : ` ${change == null ? "" : "("}${percent > 0 ? "+" : ""}${niftyNumber(percent)}%${change == null ? "" : ")"}`}</>}
    {factor.trend && <small> · {factor.trend.replaceAll("_", " ")}</small>}
  </span>;
}

export default function NiftyFactorCard({ factor, onSelect, selected = false }: { factor: NiftyFactor; onSelect: (id: string) => void; selected?: boolean }) {
  const hasValue = factor.value != null;
  const sourceUrl = niftyLink(factor.source_url);
  return <article className={`nifty-factor nifty-factor-${factor.status}${selected ? " nifty-factor-selected" : ""}`} id={`factor-${factor.id}`}>
    <div className="nifty-factor-heading"><div><span className="nifty-factor-priority">{factor.priority} <span>· {factor.kind}</span></span><h3>{factor.label}</h3></div><span className={`nifty-status nifty-status-${factor.status}`}>{factorStatusLabel(factor)}</span></div>
    <div className={`nifty-factor-value${typeof factor.value === "string" ? " nifty-factor-text" : ""}`}><FactorValue value={factor.value} unit={factor.unit} compact /></div>
    <FactorChange factor={factor} />
    <CashFlowDetails factor={factor} />
    <p className="nifty-factor-description">{factor.description}</p>
    <details className="nifty-factor-details"><summary>Evidence & context</summary><div className="nifty-factor-evidence">
      {factor.value != null && typeof factor.value === "object" && <FactorValue value={factor.value} unit={factor.unit} />}
      {factor.previous_value != null && <div className="nifty-previous">Previous: <FactorValue value={factor.previous_value} unit={factor.unit} compact /></div>}
      {factor.context != null && <div className="nifty-context"><FactorValue value={factor.context} /></div>}
      {factor.historical_context != null && <div className="nifty-context"><p>Retained historical context</p><FactorValue value={factor.historical_context} /></div>}
      {factor.strikes && factor.strikes.length > 0 && <FactorValue value={factor.strikes} />}
      {factor.basis && <p>Basis: {factor.basis}</p>}
      <p>{factor.availability_note || (hasValue ? "Source evidence is attached below." : "No sourced observation is stored for this factor.")}</p>
      <p>Expected cadence: {factor.cadence || "Source dependent"}.</p>
      <p>Collected: {niftyDate(factor.observed_at)}{factor.observed_at ? " IST" : ""}.</p>
    </div></details>
    <div className="nifty-factor-footer"><div><span>{sourceUrl ? <a href={sourceUrl} target="_blank" rel="noreferrer">{factor.source || (hasValue ? "Source" : "Suggested source")} ↗</a> : factor.source || "Source pending"}</span><span>{factorReportLabel(factor)}</span></div><button type="button" onClick={() => onSelect(factor.id)} aria-label={`Explore history for ${factor.label}`}>Explore ↗</button></div>
  </article>;
}
