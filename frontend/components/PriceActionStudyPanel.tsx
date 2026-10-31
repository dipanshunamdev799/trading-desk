"use client";

import { useState } from "react";
import { studyTime, studyColor, type PriceActionStudy, type StudyEvent, type StudyOverlay } from "@/lib/priceAction";

export default function PriceActionStudyPanel({ study, overlay, selectedConcepts, onConcept, onFocus }: {
  study: PriceActionStudy; overlay: StudyOverlay; selectedConcepts: number[];
  onConcept: (id: number) => void; onFocus: (event: StudyEvent) => void;
}) {
  const [tab, setTab] = useState("events");
  const [search, setSearch] = useState("");
  const matched = new Set([...study.events.map(e => e.concept), ...study.lines.map(l => l.concept), ...study.zones.map(z => z.concept)]);
  return <details className="price-study-details">
    <summary>Inspect checklist & matches <span>{matched.size} / 47 concepts present · {overlay.events.length} visible events</span></summary>
    <div className="price-study-tabs" role="tablist" aria-label="Price action details">
      {[['events', 'Matched events'], ['checklist', 'All 47 concepts'], ['rules', 'Method & data']].map(([value, label]) => <button type="button" role="tab" aria-selected={tab === value} key={value} onClick={() => setTab(value)}>{label}</button>)}
    </div>
    <div className="price-study-scroll" role="tabpanel">
      {tab === "events" && <>{overlay.events.length ? [...overlay.events].reverse().map(event => <button type="button" className="price-study-event" key={event.id} onClick={() => onFocus(event)} title="Focus this confirmation candle">
        <time>{studyTime(event.known_at)}</time><strong style={{ color: studyColor(event.side) }}>{event.label}</strong><span>{event.detail}</span>
      </button>) : <p className="muted">No matches for the selected layers in this session. This does not imply a trading signal.</p>}</>}
      {tab === "checklist" && <><input aria-label="Find a price action concept" type="search" placeholder="Find a concept…" value={search} onChange={e => setSearch(e.target.value)} />
        <div className="price-study-checklist">{study.catalog.filter(row => `${row.label} ${row.rule}`.toLowerCase().includes(search.toLowerCase())).map(row => {
          const last = study.events.filter(event => event.concept === row.id).at(-1);
          const present = matched.has(row.id);
          const absent = [7, 8].includes(row.id) && !study.previous_session ? "Data unavailable" : row.id === 39 && !study.lines.some(l => l.concept === 39) ? "Range unavailable" : !study.completed_bars ? "No closed bars" : "No match";
          return <button type="button" aria-pressed={selectedConcepts.includes(row.id)} className={`price-study-concept${selectedConcepts.includes(row.id) ? " selected" : ""}`} key={row.id} onClick={() => { onConcept(row.id); if (last && !selectedConcepts.includes(row.id)) onFocus(last); }}>
            <strong><small>{row.id.toString().padStart(2, "0")}</small> {row.label}</strong><span className={present ? "present" : "muted"}>{last ? `Last match ${studyTime(last.known_at)}` : present ? "Reference on chart" : absent}</span><p>{row.rule}</p>
          </button>;
        })}</div></>}
      {tab === "rules" && <div className="price-study-method">
        <p>Study session <strong>{study.session || "unavailable"}</strong> · {study.completed_bars} closed bars · {study.forming_bars} forming. Previous recorded daily session: {study.previous_session || "unavailable"}.</p>
        <p>Two bars confirm each swing. ATR is the simple mean of 14 preceding true ranges. Level tolerance = max(0.015% of price, 0.12 × prior ATR). Latest tolerance: {study.level_tolerance?.toFixed(2) || "—"} points. Opening range: {study.orb_minutes} minutes. Round levels: {study.round_step} points.</p>
        <p>Compact labels: SWP = sweep, RET = retest, FAIL = false break, ENG = engulfing, PB = pullback, ORB = opening-range break, BOS = break of structure, CHoCH = change of character, FVG = fair value gap, OB? = order-block candidate. Labels are spaced out; every arrow remains inspectable by hovering its candle or opening Matched events.</p>
        {study.notes.map(note => <p key={note}>{note}</p>)}
        <p>Start with 15-minute structure and levels, then inspect 5-minute closed setups. Use the Max Pain page for dated OI and PCR context. Pattern matches are research annotations; they do not establish a profitable CE/PE entry. Invalidation, option premium, spread and position risk still need a separate trade plan.</p>
        <p>Flags, triangles, neckline reversals and institutional-style zones use the explicit rules in the checklist. “Candidate” does not identify actual institutional orders. NIFTY spot has no directly traded volume, so volume confirmation and VWAP are not inferred.</p>
        <p>Reading: <a href="https://zerodha.com/varsity/chapter/support-and-resistance/" target="_blank" rel="noreferrer">Support & resistance</a> · <a href="https://zerodha.com/varsity/chapter/multiple-candlestick-patterns-part-1/" target="_blank" rel="noreferrer">Candlestick context</a>. Numerical detection thresholds are this app’s rules.</p>
      </div>}
    </div>
  </details>;
}
