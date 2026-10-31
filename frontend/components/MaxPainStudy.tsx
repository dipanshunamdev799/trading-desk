"use client";

import { useMemo, useState } from "react";
import type { MaxPainResearch, StudyObservation } from "@/lib/maxpainResearch";
import { Metric } from "./Bits";
import EChartPanel from "./EChartPanel";
import ExpandableChartPanel from "./ExpandableChartPanel";
import { chainConvergenceOption, monthlyConvergenceOption } from "./maxpainStudyCharts";

export const studyNumber = (value: number | null | undefined, digits = 1) => value == null || !Number.isFinite(value) ? "—" : value.toLocaleString("en-IN", { maximumFractionDigits: digits, minimumFractionDigits: digits });
const pct = (value: number | null | undefined) => value == null ? "—" : `${studyNumber(value)}%`;
const verdict = (value: boolean | null) => value == null ? "At target" : value ? "Yes" : "No";

function download(rows: StudyObservation[]) {
  const columns = ["symbol", "expiry", "snapshot_date", "entry_date", "horizon", "target", "entry_open", "expiry_close", "start_gap_pct", "end_gap_pct", "closer", "moved_toward", "range_reached_target", "mirror_closer", "strict_eligible", "unpaired_strikes", "unpaired_oi_pct"] as const;
  const csv = [columns.join(","), ...rows.map(row => columns.map(key => row[key] == null ? "" : String(row[key])).join(","))].join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const anchor = document.createElement("a"); anchor.href = url; anchor.download = "max-pain-convergence-observations.csv"; anchor.click(); URL.revokeObjectURL(url);
}

export default function MaxPainStudy({ study }: { study: MaxPainResearch }) {
  const [horizon, setHorizon] = useState(1);
  const [proximity, setProximity] = useState("near");
  const [coverageMode, setCoverageMode] = useState("strict");
  const [asset, setAsset] = useState("all");
  const [page, setPage] = useState(0);
  const group = study.groups.find(row => row.horizon === horizon && row.proximity === proximity && row.coverage_mode === coverageMode);
  const rows = useMemo(() => study.observations.filter(row => row.horizon === horizon && (coverageMode === "published" || row.strict_eligible) && (proximity === "all" || row.near) && (asset === "all" || row.symbol === asset))
    .sort((a, b) => b.expiry.localeCompare(a.expiry) || a.symbol.localeCompare(b.symbol)), [study, horizon, proximity, coverageMode, asset]);
  const byChain = useMemo(() => group ? chainConvergenceOption(group) : {}, [group]);
  const byMonth = useMemo(() => group ? monthlyConvergenceOption(group) : {}, [group]);
  if (!group) return <div className="empty-note">No results for this selection.</div>;
  const summary = group.summary, confidence = group.confidence;
  const limited = summary.n < 30 || !confidence || (group.data_coverage.coverage_pct ?? 0) < 80;
  const finding = limited ? "The sample or coverage is too limited for a strong conclusion."
    : confidence.difference_low > 0 ? "Spot finished closer to frozen Max Pain more often than to the matched opposite-side target in this sample."
    : confidence.difference_high < 0 ? "The matched opposite-side target had a higher closer-finish rate than frozen Max Pain in this sample."
    : "The uncertainty interval includes no difference from the matched opposite-side target; this sample does not clearly distinguish Max Pain convergence from the control.";
  const shown = rows.slice(page * 25, page * 25 + 25);
  return <div className="stack">
    <div className="panel">
      <div className="panel-header"><div><h2>Does spot converge toward Max Pain near expiry?</h2><p className="maxpain-caption">{study.start_date} → {study.end_date} · 10 selected NSE underlyings · fixed-target research</p></div><span className="badge warn">Spot study · no strategy P&amp;L</span></div>
      <div className="panel-body">
        <div className="toolbar">
          <div className="field"><label htmlFor="study-horizon">Snapshot timing</label><select id="study-horizon" value={horizon} onChange={event => { setHorizon(Number(event.target.value)); setPage(0); }}><option value={1}>T−1 EOD · primary</option><option value={3}>T−3 EOD</option><option value={5}>T−5 EOD</option></select></div>
          <div className="field"><label htmlFor="study-proximity">Starting distance</label><select id="study-proximity" value={proximity} onChange={event => { setProximity(event.target.value); setPage(0); }}><option value="near">Within 1% of spot · primary</option><option value="all">All starting distances</option></select></div>
          <div className="field"><label htmlFor="study-coverage">OI coverage rule</label><select id="study-coverage" value={coverageMode} onChange={event => { setCoverageMode(event.target.value); setPage(0); }}><option value="strict">Paired strikes · strict primary</option><option value="published">All published contracts · sensitivity</option></select></div>
        </div>
        <p style={{ lineHeight: 1.6 }}>Max Pain is calculated from the completed session&apos;s official OI and held fixed. Evaluation starts at the <strong>next trading session&apos;s open</strong> and ends at expiry close. “Closer” means a smaller absolute distance at the end. The target never moves with later OI.</p>
        <p style={{ lineHeight: 1.6, color: "#C9B4EB" }}>{finding}</p>
        {coverageMode === "published" && <p className="muted">Sensitivity view: includes actual published contracts at unmatched strikes. It does not establish that absent counterpart contracts have zero OI. Compare with the strict primary view before drawing conclusions.</p>}
        <p className="muted">NSE files: {study.file_coverage.available_files}/{study.file_coverage.expected_sessions} available sessions, including warmup. Valid case coverage at this horizon: {pct(group.data_coverage.coverage_pct)} ({group.data_coverage.eligible} eligible, {group.data_coverage.excluded} excluded). The proximity filter is applied after these data checks.</p>
      </div>
    </div>
    <div className="metric-strip">
      <Metric label="Comparable cases" value={`${summary.n} · ${summary.expiry_dates} expiry dates`} />
      <Metric label="Finished closer to Max Pain" value={pct(summary.closer_rate)} />
      <Metric label="Opposite target control" value={pct(summary.mirror_rate)} />
      <Metric label="Difference vs control" value={summary.difference_vs_mirror == null ? "—" : `${studyNumber(summary.difference_vs_mirror)} pp`} />
      <Metric label="Moved in target direction" value={pct(summary.moved_toward_rate)} />
      <Metric label="Daily range reached target" value={pct(summary.range_reached_rate)} />
      <Metric label="Median gap reduction" value={summary.median_gap_reduction_pct_points == null ? "—" : `${studyNumber(summary.median_gap_reduction_pct_points, 3)} pp`} />
    </div>
    <p className="maxpain-caption">{confidence ? `95% expiry-date bootstrap interval: closer rate ${pct(confidence.rate_low)}–${pct(confidence.rate_high)}; difference vs control ${studyNumber(confidence.difference_low)} to ${studyNumber(confidence.difference_high)} percentage points.` : "Confidence interval unavailable: fewer than 10 distinct expiry dates."} Moving in the target direction can still finish farther away after an overshoot. Positive gap reduction means the distance shrank. Reaching the target during a daily range does not guarantee finishing closer or an executable fill.</p>
    <ExpandableChartPanel title="Convergence by option chain"><div className="panel-header"><h2>Convergence by option chain</h2><span className="muted">Every bar includes its sample size</span></div><div className="panel-body tight"><EChartPanel option={byChain} height={330} /></div></ExpandableChartPanel>
    <div className="panel"><div className="panel-header"><h2>Results by underlying</h2></div><div className="table-wrap"><table className="data"><thead><tr><th>Underlying</th><th className="num">Cases</th><th className="num">Closer</th><th className="num">Control</th><th className="num">Moved toward</th><th className="num">Initial gap</th><th className="num">Final gap</th><th className="num">Median reduction</th></tr></thead><tbody>{group.by_asset.map(row => <tr key={row.symbol}><td>{row.label}</td><td className="num">{row.n}</td><td className="num">{pct(row.closer_rate)}</td><td className="num">{pct(row.mirror_rate)}</td><td className="num">{pct(row.moved_toward_rate)}</td><td className="num">{pct(row.mean_start_gap_pct)}</td><td className="num">{pct(row.mean_end_gap_pct)}</td><td className="num">{studyNumber(row.median_gap_reduction_pct_points, 3)} pp</td></tr>)}</tbody></table></div></div>
    <ExpandableChartPanel title="Convergence through the year"><div className="panel-header"><h2>Convergence through the year</h2><span className="muted">Cases grouped by entry month</span></div><div className="panel-body tight"><EChartPanel option={byMonth} height={290} /></div></ExpandableChartPanel>
    <div className="panel">
      <div className="panel-header"><h2>Observation audit</h2><button type="button" onClick={() => download(rows)}>Download these cases · CSV</button></div>
      <div className="panel-body"><div className="row"><label htmlFor="study-asset">Audit rows</label><select id="study-asset" value={asset} onChange={event => { setAsset(event.target.value); setPage(0); }}><option value="all">All underlyings</option>{study.universe.map(row => <option key={row.symbol} value={row.symbol}>{row.label}</option>)}</select><span className="muted">{rows.length} observations · OI and spot in original historical units</span></div></div>
      <div className="table-wrap"><table className="data"><thead><tr><th>Chain</th><th>Expiry</th><th>OI snapshot</th><th>Entry session</th><th className="num">Frozen MP</th><th className="num">Entry open</th><th className="num">Expiry close</th><th className="num">Initial gap</th><th className="num">Final gap</th><th>Closer?</th></tr></thead><tbody>{shown.map(row => <tr key={`${row.symbol}|${row.expiry}|${row.horizon}`}><td>{row.symbol}</td><td className="mono">{row.expiry}</td><td className="mono">{row.snapshot_date}</td><td className="mono">{row.entry_date}</td><td className="num">{studyNumber(row.target, 2)}</td><td className="num">{studyNumber(row.entry_open, 2)}</td><td className="num">{studyNumber(row.expiry_close, 2)}</td><td className="num">{pct(row.start_gap_pct)}</td><td className="num">{pct(row.end_gap_pct)}</td><td>{verdict(row.closer)}</td></tr>)}</tbody></table></div>
      <div className="panel-body row"><button type="button" disabled={page === 0} onClick={() => setPage(value => value - 1)}>Previous</button><span className="muted">Page {page + 1} / {Math.max(1, Math.ceil(rows.length / 25))}</span><button type="button" disabled={(page + 1) * 25 >= rows.length} onClick={() => setPage(value => value + 1)}>Next</button></div>
    </div>
    <div className="panel"><div className="panel-header"><h2>Method, coverage and limitations</h2></div><div className="panel-body">
      <ol style={{ lineHeight: 1.7 }}>{study.methodology.map(text => <li key={text}>{text}</li>)}</ol>
      <p><strong>Control:</strong> an opposite-side target with the same initial distance: <code>2 × entry spot − frozen Max Pain</code>. Its result helps distinguish target direction from distance alone.</p>
      <p><strong>Already at target:</strong> {summary.already_at_target} cases are excluded from the closer-rate denominator because they cannot get strictly closer.</p>
      <details><summary>Excluded cases and source coverage</summary><ul>{Object.entries(study.exclusion_reasons).map(([reason, count]) => <li key={reason}>{reason.replaceAll("_", " ")}: {count}</li>)}</ul><table className="data"><thead><tr><th>Underlying</th><th>Expiries identified</th><th>Price sessions</th></tr></thead><tbody>{study.coverage.map(row => <tr key={row.symbol}><td>{row.label}</td><td>{row.expiries_identified}</td><td>{row.price_sessions}</td></tr>)}</tbody></table>{study.errors.length > 0 && <p>Source failures: {study.errors.map(row => `${row.symbol || row.day}: ${row.error}`).join("; ")}</p>}</details>
      <p className="muted">Sources: official NSE UDiFF derivatives bhavcopies (every selected option leg retained in TimescaleDB, with file hashes) and retained underlying daily OHLC. Generated {new Date(study.generated_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })} IST. Study version {study.version}.</p>
    </div></div>
  </div>;
}
