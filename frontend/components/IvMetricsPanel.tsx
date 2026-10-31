"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type IvHistory } from "@/lib/api";
import { useChartAsOf } from "@/lib/chartAsOf";
import { startMinutePolling } from "@/lib/minutePolling";
import EChartPanel from "./EChartPanel";
import ExpandableChartPanel from "./ExpandableChartPanel";
import { ivChartOption, ivFormat } from "./ivCharts";

type Props = { expiry: string; asOf: string; instrumentKey: string; instrumentLabel: string; dates: string[]; live: boolean; refreshId: number };

export default function IvMetricsPanel(props: Props) {
  const scope = useChartAsOf(props.asOf, props.dates);
  return <ExpandableChartPanel title="IV metrics & expected move" asOf={scope.control} onExpandedChange={scope.onExpandedChange}>
    <IvMetricsContent key={`${props.instrumentKey}|${props.expiry}|${scope.date}|${scope.independent}`} {...props} asOf={scope.date} live={props.live && !scope.independent} />
  </ExpandableChartPanel>;
}

function IvMetricsContent({ expiry, asOf, instrumentKey, instrumentLabel, live, refreshId }: Props) {
  const [data, setData] = useState<IvHistory | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!expiry || !asOf) return;
    return startMinutePolling({ live,
      load: () => api.ivHistory({ expiry, as_of: asOf, instrument_key: instrumentKey }),
      onData: result => {
        if (result.expiry !== expiry || result.as_of !== asOf || result.instrument_key !== instrumentKey) { setError("IV response does not match this chart's underlying, expiry and date."); return; }
        setData(result); setError(null);
      },
      onError: reason => setError(reason instanceof Error ? reason.message : "IV history could not be loaded"), onLoading: setLoading,
    });
  }, [expiry, asOf, instrumentKey, live, refreshId]);
  const current = data?.expiry === expiry && data.as_of === asOf && data.instrument_key === instrumentKey ? data : null;
  const points = current?.points || [];
  const latest = points.at(-1);
  const option = useMemo(() => ivChartOption(asOf, points, current?.history_partial ?? true), [asOf, points, current?.history_partial]);
  return <>
    <div className="panel-header"><div><h2>IV metrics & expected move</h2>
      <p className="maxpain-caption">{instrumentLabel} · expiry {expiry || "—"} · {asOf || "checking session…"} · one-minute captures · IST</p>
      {current && <p className="maxpain-caption iv-history-hint">{current.rank_hint}</p>}
    </div><span className="badge db">{loading ? "Updating…" : live ? "Feed / REST · 1 min refresh" : "Saved captures"}</span></div>
    <div className="iv-metric-strip" aria-live="polite">
      <div><span>ATM IV</span><strong>{latest ? `${ivFormat(latest.iv)}%` : "—"}</strong></div>
      <div><span>IV Rank{current?.history_partial ? " · sample" : ""}</span><strong>{ivFormat(latest?.iv_rank)}</strong></div>
      <div><span>IV Percentile{current?.history_partial ? " · sample" : ""}</span><strong>{ivFormat(latest?.iv_percentile)}</strong></div>
      <div><span>Expected move to expiry</span><strong>{latest?.expected_move != null ? `±${ivFormat(latest.expected_move)} pts` : "—"}</strong></div>
    </div>
    <div className="panel-body tight">
      {error && <div className="error-box" role="status">{error}{points.length ? " Showing retained observations for this selection." : ""}</div>}
      {points.length ? <EChartPanel option={option} height={480} /> : <div className="chart-empty" style={{ height: 280 }}>{loading ? "Loading IV metrics…" : current?.hint || "No IV observations available for this selection."}</div>}
      <p className="maxpain-caption iv-chart-key" style={{ padding: "0 18px 12px", margin: 0 }}>IV = same-strike ATM call/put mean · Rank/Percentile = expiry-specific saved daily history · Expected move = spot × IV × √(time to expiry / 365).{latest && <> Last capture {latest.time} IST · ATM {ivFormat(latest.strike)} · model range {ivFormat(latest.lower)}–{ivFormat(latest.upper)}.</>} Missing minutes stay as gaps.</p>
    </div>
    <details className="iv-method"><summary>Calculation & data coverage</summary><p>{current?.iv_basis}</p><p>{current?.rank_basis}</p><p>{current?.move_basis}</p><p>IV Rank = 100 × (current IV − low) / (high − low). A flat range has no rank. IV Percentile = percentage of prior saved daily readings strictly below current IV. Both require at least two prior sessions; partial samples are labelled. Prior readings use their actual acquisition dates and can precede the close. ATM strikes can change as spot moves. Different expiries are analysed separately.</p><p>Historical reads use original database captures. Current-session reads prefer fresh WebSocket IV and spot with the existing REST fallback. An overnight response cannot fill an earlier session. No IV is inferred from OI or closing premiums.</p></details>
  </>;
}
