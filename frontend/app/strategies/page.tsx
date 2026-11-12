"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import AppShell from "@/components/AppShell";
import { auditValue, directionLabel, evaluationNumber as number, evaluationPercent as percent, evaluationTime as time, fetchStrategyEvaluation, inputScoringLabel, inputScoringStatus, readable, statusLabel, type EvaluatedStrategy, type StrategyEvaluation } from "@/lib/strategyEvaluation";
import "./strategies.css";

function signed(value: number | null | undefined, decimals = 1): string {
  return typeof value === "number" && Number.isFinite(value) ? `${value > 0 ? "+" : ""}${number(value, decimals)}` : "—";
}

function Meter({ value, tone = "positive" }: { value: number; tone?: string }) {
  return <div className={`evaluation-meter ${tone}`} aria-hidden="true"><span style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div>;
}

function Stat({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return <div className="evaluation-stat"><span>{label}</span><strong>{value}</strong>{detail && <small>{detail}</small>}</div>;
}

function StrategyDetail({ strategy }: { strategy: EvaluatedStrategy }) {
  const active = strategy.factors.filter(factor => factor.weight > 0);
  const excluded = strategy.factors.filter(factor => !(factor.weight > 0));
  return <section className="panel evaluation-detail" aria-labelledby="strategy-detail-title">
    <div className="panel-header"><div><div className="evaluation-eyebrow">WEIGHTED ASSESSMENT</div><h2 id="strategy-detail-title">{strategy.name}</h2><p className="evaluation-caption">{strategy.configuration}</p></div><span className={`evaluation-status ${strategy.status}`}>{statusLabel(strategy.status)}</span></div>
    <div className="evaluation-detail-stats">
      <Stat label="Confidence · research score" value={`${number(strategy.confidence_score)} / 100`} detail="Evidence-adjusted support; no win probability" />
      <Stat label="Consolidated alignment" value={signed(strategy.score)} detail="Signed contributions before confidence adjustments" />
      <Stat label="Input coverage" value={percent(strategy.coverage)} detail="Missing inputs reduce confidence" />
      <Stat label="Signal conflict" value={percent(strategy.conflict)} detail="Independent domains disagreeing" />
    </div>
    <div className="evaluation-thesis"><strong>{directionLabel(strategy.direction)} · {strategy.setup_triggered ? "Setup triggered" : "Setup not triggered"}</strong><ul>{strategy.reasons.map((reason, index) => <li key={`${index}-${reason}`}>{readable(reason)}</li>)}</ul></div>
    {strategy.groups?.length ? <div className="evaluation-domains" aria-label="Independent domain weight budgets">{strategy.groups.map(group => <div key={group.id}><strong>{readable(group.id)}</strong><span>{group.available ? `${percent(group.weight)} of weight` : "Unavailable domain"}</span><small className={group.contribution_points < 0 ? "evaluation-negative" : group.contribution_points > 0 ? "evaluation-positive" : ""}>{signed(group.contribution_points)} pts</small></div>)}</div> : null}
    <div className="table-wrap"><table className="data evaluation-factor-table"><thead><tr><th>Factor / domain</th><th>Weight</th><th>Signal alignment</th><th>Reliability</th><th>Assessment</th><th>Contribution</th><th>Reason / source</th></tr></thead><tbody>{active.map(factor => <tr key={factor.id}>
      <td><strong>{factor.label}</strong><small>{readable(factor.group)}</small></td>
      <td className="evaluation-numeric">{percent(factor.weight)}<Meter value={factor.weight * 100} /></td>
      <td className="evaluation-numeric">{signed(factor.alignment, 2)}<small>−1 opposes · +1 supports</small></td>
      <td className="evaluation-numeric">{percent(factor.reliability)}</td>
      <td><span className={`evaluation-stance ${factor.stance}`}>{readable(factor.stance)}</span></td>
      <td className={`evaluation-numeric ${(factor.contribution_points || 0) < 0 ? "evaluation-negative" : (factor.contribution_points || 0) > 0 ? "evaluation-positive" : ""}`}>{signed(factor.contribution_points)} pts</td>
      <td className="evaluation-reason">{factor.reason || "No additional explanation supplied."}<small>{factor.source || "Source unavailable"} · {time(factor.reported_at)}</small></td>
    </tr>)}</tbody><tfoot><tr><td>Total normalized weight</td><td>{percent(active.reduce((total, factor) => total + factor.weight, 0))}</td><td colSpan={3}>Signed factor contributions</td><td>{signed(active.reduce((total, factor) => total + factor.contribution_points, 0))} pts</td><td>Coverage, reliability and conflict determine the confidence score.</td></tr></tfoot></table>{!active.length && <div className="empty-note">No usable weighted factors for this strategy. Review the unavailable inputs below.</div>}</div>
    <div className="evaluation-detail-foot"><p>Factors in the same domain share a weight budget. Adding another correlated technical indicator does not create another independent vote.</p>
      {excluded.length > 0 && <details><summary>{excluded.length} excluded or unavailable factors</summary><div className="evaluation-excluded">{excluded.map(factor => <div key={factor.id}><strong>{factor.label}</strong><span>{factor.exclusion_reason || factor.reason || readable(factor.stance)}</span></div>)}</div></details>}
      {strategy.historical_evidence != null && <details><summary>Historical evidence and its limits</summary><p>{readable(strategy.historical_evidence)}</p></details>}
    </div>
  </section>;
}

export default function StrategiesPage() {
  const [data, setData] = useState<StrategyEvaluation | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string>("");
  const request = useRef<AbortController | null>(null);
  const mounted = useRef(false);
  const load = useCallback(async () => {
    if (request.current) return;
    const controller = new AbortController();
    request.current = controller;
    setLoading(true);
    try {
      const result = await fetchStrategyEvaluation(controller.signal);
      if (!mounted.current || controller.signal.aborted) return;
      setData(result);
      setError(null);
    } catch (cause) {
      if (!mounted.current || controller.signal.aborted) return;
      setError(cause instanceof Error ? cause.message : "Strategy evaluation unavailable");
    } finally {
      if (request.current === controller) request.current = null;
      if (mounted.current && !controller.signal.aborted) setLoading(false);
    }
  }, []);
  useEffect(() => {
    mounted.current = true;
    void load();
    const interval = setInterval(() => { void load(); }, 60_000);
    return () => {
      mounted.current = false;
      clearInterval(interval);
      request.current?.abort();
      request.current = null;
    };
  }, [load]);
  const ranked = useMemo(() => [...(data?.strategies || [])].sort((left, right) => right.confidence_score - left.confidence_score || right.score - left.score || left.name.localeCompare(right.name)), [data]);
  const current = ranked.find(strategy => strategy.id === selected) || ranked[0];
  const inputs = data?.input_audit || [];
  const weighted = inputs.filter(input => inputScoringStatus(input) === "weighted").length;
  const unavailable = inputs.filter(input => inputScoringStatus(input) === "unavailable").length;
  const contextual = inputs.length - weighted - unavailable;
  const context = data?.market_context;

  return <AppShell title="Strategy evaluation"><div className="evaluation-desk">
    <div className="evaluation-heading"><div><div className="evaluation-eyebrow">NIFTY / STRATEGY RESEARCH</div><h2>One market. Different requirements.</h2><p>Evaluate each setup against price, positioning and market context.</p></div><div className="evaluation-heading-actions"><span className="badge warn">Research only</span><button onClick={() => { void load(); }} disabled={loading}>{loading ? "Evaluating…" : "↻ Refresh evaluation"}</button></div></div>
    <div className="evaluation-disclosure"><strong>Confidence measures weighted evidence, not the probability of profit.</strong><span>Current scores have no validated probability calibration. Historical rankings remain research evidence.</span></div>
    {error && <div className="error-box" role="alert">{error}{data && <span> · Showing the previous evaluation from {time(data.as_of)}.</span>}</div>}
    <div className="evaluation-market-grid">
      <Stat label="NIFTY spot" value={number(context?.spot, 2)} detail={`Last completed bar · ${time(context?.bar_at)}`} />
      <Stat label={context?.fresh === false ? "Historical context" : "Market regime"} value={context?.regime ? `${context.fresh === false ? "Last observed " : ""}${readable(context.regime)}` : "Unavailable"} detail={`${context?.session_phase ? `${readable(context.session_phase)} session` : "Session status unavailable"}${context?.fresh === false ? " · stale context" : ""}`} />
      <Stat label="ATR · five-minute" value={number(context?.atr, 2)} detail="Price moves normalized to current volatility" />
      <Stat label="Weighted scoring inputs" value={data ? `${weighted} / ${inputs.length}` : "—"} detail={data ? `${contextual} descriptors / context · ${unavailable} unavailable` : "Waiting for market picture"} />
    </div>
    {data?.errors?.length ? <div className="evaluation-data-notice"><strong>Some market inputs are unavailable</strong><ul>{data.errors.map((item, index) => <li key={index}>{item}</li>)}</ul></div> : null}
    <section className="panel evaluation-ranking" aria-labelledby="strategy-ranking-title"><div className="panel-header"><div><h2 id="strategy-ranking-title">Strategy assessments</h2><p className="evaluation-caption">Ranked by current research confidence · select a strategy to inspect every contribution</p></div><span className="badge">{ranked.length} strategies</span></div>
      {ranked.length ? <div className="evaluation-cards">{ranked.map((strategy, index) => <button className={`evaluation-card ${current?.id === strategy.id ? "selected" : ""}`} key={strategy.id} onClick={() => setSelected(strategy.id)} aria-pressed={current?.id === strategy.id}>
        <div className="evaluation-card-top"><span className="evaluation-rank">{String(index + 1).padStart(2, "0")}</span><span className={`evaluation-status ${strategy.status}`}>{statusLabel(strategy.status)}</span></div>
        <strong className="evaluation-card-title">{strategy.name}</strong><span className="evaluation-card-config">{strategy.configuration}</span>
        <div className="evaluation-card-confidence"><strong>{number(strategy.confidence_score)}<small>/100</small></strong><span>Confidence<br />research score</span></div><Meter value={strategy.confidence_score} tone={strategy.confidence_score > 50 ? "positive" : "muted"} />
        <div className="evaluation-card-bottom"><span>{directionLabel(strategy.direction)}</span><span>{strategy.setup_triggered ? "Setup triggered" : "No active setup"}</span></div>
      </button>)}</div> : <div className="empty-note">{loading ? "Building the complete market picture…" : "No strategy assessments are available. Refresh to try again."}</div>}
    </section>
    {current && <StrategyDetail strategy={current} />}
    <section className="panel evaluation-inputs"><details><summary><span>Complete market input audit</span><small>{weighted} scored · {contextual} descriptors / context · {unavailable} unavailable</small></summary><div className="table-wrap"><table className="data"><thead><tr><th>Input</th><th>Domain</th><th>Scoring status</th><th>Observed value</th><th>Signal</th><th>Predictive reliability</th><th>Observation / source</th><th>Why it matters or is excluded</th></tr></thead><tbody>{inputs.map(input => {
      const status = inputScoringStatus(input);
      const receipt = `Source time: ${input.reported_at || "unavailable"}\nReceived: ${input.observed_at || "unavailable"}`;
      return <tr key={input.id}><td>{input.label}</td><td>{readable(input.group)}</td><td><span className={`evaluation-stance ${status === "weighted" ? "supports" : status}`}>{inputScoringLabel(input)}</span></td><td className="evaluation-audit-value">{input.value !== null && typeof input.value === "object" ? <details><summary>{auditValue(input.value)}</summary><pre>{JSON.stringify(input.value, null, 2)}</pre></details> : auditValue(input.value)}</td><td className="evaluation-numeric">{input.available ? signed(input.signal, 2) : "—"}</td><td>{status === "weighted" ? percent(input.reliability) : "Not scored"}{input.predictive_status && <small>{readable(input.predictive_status)}</small>}</td><td title={receipt}>{time(input.reported_at)}<small>{input.source || "Source unavailable"}</small><small>Received {time(input.observed_at)}</small></td><td className="evaluation-reason">{input.reason || "No additional explanation supplied."}</td></tr>;
    })}</tbody></table></div><p className="evaluation-caption">A measured descriptor or context observation is visible without receiving predictive weight. Signals use −1 to +1; directional inputs describe bearish to bullish evidence, while regime and volatility describe strategy suitability. Hover over observation times to inspect source and receipt timestamps. As of {time(data?.as_of)}.</p></details></section>
    {(data?.notes?.length || data?.methodology) && <section className="panel evaluation-method"><details><summary>Scoring method and evidence limits</summary><ul>{data.notes.map((note, index) => <li key={index}>{note}</li>)}</ul>{data.methodology && <dl>{Object.entries(data.methodology).map(([key, value]) => <div key={key}><dt>{readable(key)}</dt><dd>{readable(value)}</dd></div>)}</dl>}</details></section>}
    <div className="evaluation-footer">{data ? `Evaluation generated ${time(data.generated_at)} · automatic refresh every 60 seconds` : "Automatic refresh every 60 seconds"}</div>
  </div></AppShell>;
}
