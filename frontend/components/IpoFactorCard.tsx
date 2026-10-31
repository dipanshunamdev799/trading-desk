import type { ReactNode } from "react";
import type { IpoFactor } from "@/lib/api";
import { ipoDate, ipoNumber as n, safeIpoLink } from "@/components/ipoResearch";

export function FactorValue({ factor }: { factor: IpoFactor }): ReactNode {
  const v = factor.value as any;
  if (v == null) return <span className="muted">{factor.status === "pending" ? "Bidding not started" : "Not available from connected sources"}</span>;
  switch (factor.unit) {
    case "x": return <span className="mono">{typeof v === "number" ? `${n(v)}×` : <>{n(v.nii)}× <small className="muted">NII · sNII {n(v.snii)}× · bNII {n(v.bnii)}×</small></>}</span>;
    case "%": return <span className="mono">{n(v)}%</span>;
    case "cr": return <span className="mono">₹{n(v)} Cr</span>;
    case "gmp": return <span className="mono">₹{n(v.rupees)} <small className={v.percent < 0 ? "neg" : "pos"}>{n(v.percent)}%</small></span>;
    case "trend": return <span>{v.direction} <small className="muted">· ₹{n(v.change_rs)} vs prior day{v.from_peak_pct != null ? ` · ${n(v.from_peak_pct)}% from observed peak` : ""}</small></span>;
    case "structure": return <div>Fresh ₹{n(v.fresh_cr)} Cr <small>({n(v.fresh_pct)}%)</small><br />OFS ₹{n(v.ofs_cr)} Cr <small>({n(v.ofs_pct)}%)</small></div>;
    case "objects": return <ul>{v.map((row: any, i: number) => <li key={i}>{row.purpose} <span className="mono">{row.amount_cr == null ? "Amount not specified" : `₹${n(row.amount_cr)} Cr`}</span></li>)}</ul>;
    case "anchors": return <div><strong>₹{n(v.amount_cr)} Cr · {v.count} investors</strong><details><summary>Inspect disclosed allocations</summary><ul>{v.investors.map((row: any, i: number) => <li key={i}>{row.name} <span className="mono">₹{n(row.amount_cr)} Cr</span></li>)}</ul></details></div>;
    case "manager": return <div>{v.names}<small className="muted">{v.tracked_listings.length ? ` · ${v.tracked_listings.length} matched retained listings` : " · Reputation needs review"}</small>{v.tracked_listings.length > 0 && <details><summary>Inspect matched listings</summary><ul>{v.tracked_listings.map((row: any, i: number) => <li key={i}>{row.name}<span>{n(row.listing_return_pct)}% on listing · {ipoDate(row.listing_date)}</span></li>)}</ul></details>}</div>;
    case "pe": return <div className="mono">Pre-IPO {n(v.pre)}× · Post-IPO {n(v.post)}×</div>;
    case "returns": return <div className="mono">RoNW {n(v.ronw)}% · ROE {n(v.roe)}% · ROCE {n(v.roce)}%</div>;
    case "business": return <div>{v.certifications?.length ? <p>Disclosed certifications: {v.certifications.join(", ")}</p> : null}<q>{v.excerpt}</q></div>;
    case "sector": return <div>{v.industry}<small className="muted"> · Tailwind assessment pending</small></div>;
    case "history": return <div>{v.length} publisher-dated observations · inspect the trend panel below</div>;
    case "listings": return <ul>{v.map((row: any, i: number) => <li key={i}>{row.name} <span className="mono">{n(row.listing_return_pct)}%</span></li>)}</ul>;
    case "recommendations": return <ul>{v.map((row: any, i: number) => <li key={i}>{row.reviewer}: {row.opinion}</li>)}</ul>;
    default: return <span>{String(v)}</span>;
  }
}

export default function IpoFactorCard({ factor }: { factor: IpoFactor }) {
  const link = safeIpoLink(factor.source_url);
  return <article className={`ipo-factor ${factor.id === "qib" ? "ipo-factor-priority" : ""}`}>
    <div className="ipo-factor-heading"><h3><span className="muted">{factor.number.toString().padStart(2, "0")}</span> {factor.label}</h3>
      <span className={`badge ${factor.status === "stale" ? "warn" : factor.status === "available" ? "db" : ""}`}>{factor.status === "stale" ? "Stale" : factor.id === "qib" && factor.value != null ? "Primary demand signal" : factor.status === "review" ? "Needs review" : factor.status === "available" ? "Sourced" : factor.status}</span></div>
    <div className="ipo-factor-value"><FactorValue factor={factor} /></div>
    {factor.period && <div className="ipo-factor-period">{factor.period}</div>}
    {factor.note && <p className="ipo-factor-note">{factor.note}</p>}
    {factor.value != null && <div className="ipo-factor-source">{link ? <a href={link} target="_blank" rel="noreferrer">{factor.source} ↗</a> : factor.source}
      <span>{factor.reported_at ? `As of ${ipoDate(factor.reported_at, true)} IST` : "Publisher timestamp not supplied"}</span>
      <span>Retrieved {ipoDate(factor.fetched_at, true)} IST</span></div>}
  </article>;
}
