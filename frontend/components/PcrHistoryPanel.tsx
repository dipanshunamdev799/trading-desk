"use client";

import { useEffect, useMemo, useState } from "react";
import { api, type MaxPainSnapshot, type PcrHistory, type PcrPoint } from "@/lib/api";
import { startMinutePolling } from "@/lib/minutePolling";
import { useChartAsOf } from "@/lib/chartAsOf";
import type { LiveQuote } from "@/lib/liveMarket";
import EChartPanel from "./EChartPanel";
import ExpandableChartPanel from "./ExpandableChartPanel";
import { formatPcr, pcrChartOption, pcrTimeline } from "./pcrCharts";

function freshMinute(timestamp: string, asOf: string) {
  const at = new Date(timestamp);
  const age = Date.now() - at.getTime();
  if (!Number.isFinite(age) || age < 0 || age > 30_000) return null;
  const day = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).format(at);
  return day === asOf ? new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false }).format(at) : null;
}

type PcrPanelProps = {
  expiry: string; asOf: string; instrumentKey: string; live: boolean; refreshId: number;
  instrumentLabel: string; spotObservation?: LiveQuote; dates?: string[];
  observation?: MaxPainSnapshot["pcr_observation"];
};

export default function PcrHistoryPanel(props: PcrPanelProps) {
  const scope = useChartAsOf(props.asOf, props.dates || []);
  return <ExpandableChartPanel title={`PCR (OI & volume) vs ${props.instrumentLabel} spot`} asOf={scope.control} onExpandedChange={scope.onExpandedChange}>
    <PcrHistoryContent key={`${props.instrumentKey}|${props.expiry}|${scope.date}|${scope.independent}`} {...props}
      asOf={scope.date} live={props.live && !scope.independent} />
  </ExpandableChartPanel>;
}

function PcrHistoryContent({ expiry, asOf, instrumentKey, instrumentLabel, live, refreshId, observation, spotObservation }: PcrPanelProps) {
  const [data, setData] = useState<PcrHistory | null>(null);
  const [streamed, setStreamed] = useState<PcrPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const current = data?.expiry === expiry && data.as_of === asOf && data.instrument_key === instrumentKey ? data : null;

  useEffect(() => {
    setData(null); setStreamed([]); setError(null);
  }, [expiry, asOf, instrumentKey]);

  useEffect(() => {
    if (!expiry || !asOf) return;
    return startMinutePolling({ live,
      load: () => api.pcrIntraday({ expiry, as_of: asOf, instrument_key: instrumentKey }),
      onData: result => {
        if (result.expiry !== expiry || result.as_of !== asOf || result.instrument_key !== instrumentKey) {
          setError("PCR history does not match the selected underlying, expiry and date."); return;
        }
        setData(result); setError(null);
      },
      onError: reason => setError(reason instanceof Error ? reason.message : "PCR history could not be loaded"),
      onLoading: setLoading,
    });
  }, [expiry, asOf, instrumentKey, live, refreshId]);

  useEffect(() => {
    if (!live || !observation || !Number.isFinite(observation.pcr) || observation.pcr < 0) return;
    const time = freshMinute(observation.at, asOf);
    if (!time) return;
    setStreamed(previous => [...previous.filter(row => row.time !== time), { time, pcr: observation.pcr,
      spot: previous.find(row => row.time === time)?.spot ?? null, source: "websocket" }]);
  }, [observation, live, asOf]);

  useEffect(() => {
    if (!live || !spotObservation || !Number.isFinite(spotObservation.last_price) || spotObservation.last_price <= 0) return;
    const time = freshMinute(spotObservation.last_trade_time || spotObservation.timestamp, asOf);
    if (!time) return;
    setStreamed(previous => {
      const existing = previous.find(row => row.time === time);
      return [...previous.filter(row => row.time !== time), { ...existing, time, pcr: existing?.pcr ?? null, spot: spotObservation.last_price }];
    });
  }, [spotObservation, live, asOf]);

  const points = current?.points || [];
  const rows = useMemo(() => pcrTimeline(asOf, points, streamed), [asOf, points, streamed]);
  const available = rows.filter(row => row.pcr != null);
  const volumeAvailable = rows.filter(row => row.volume_pcr != null);
  const latestVolume = volumeAvailable[volumeAvailable.length - 1];
  const hasRatios = available.length > 0 || volumeAvailable.length > 0;
  const first = available[0], latest = available[available.length - 1];
  const change = first && latest ? latest.pcr! - first.pcr! : null;
  const option = useMemo(() => pcrChartOption(asOf, points, streamed, instrumentLabel), [asOf, points, streamed, instrumentLabel]);
  return <>
    <div className="panel-header">
      <div><h2>PCR (OI & volume) vs {instrumentLabel} spot</h2><p className="maxpain-caption">PCR ratios on left axis · spot price on right axis · expiry {expiry || "—"} · {asOf || "checking session…"} · times in IST</p>
        {!loading && current && !volumeAvailable.length && <p className="maxpain-caption">{current.volume_hint || "Volume PCR is unavailable for this selection."}</p>}
        {!loading && current && !available.length && volumeAvailable.length > 0 && <p className="maxpain-caption">{current.oi_hint || "OI PCR is unavailable for this selection."}</p>}
      </div>
      <div className="row" aria-live="polite">
        {latest && <span className="mono" style={{ color: "#C9B4EB", fontSize: 16 }}>OI {formatPcr(latest.pcr)} <small className="muted">{latest.time}</small></span>}
        {latestVolume && <span className="mono" style={{ color: "#E5C07B", fontSize: 16 }}>Vol {formatPcr(latestVolume.volume_pcr)} <small className="muted">{latestVolume.time}</small></span>}
        <span className={`badge ${error ? "warn" : "db"}`}>{loading ? "Updating…" : live ? "Live OI + 1 min history" : "Saved / dated history"}</span>
      </div>
    </div>
    <div className="panel-body tight">
      {error && <div className="error-box" role="status">{error}{hasRatios ? " Showing the last available observations." : ""}</div>}
      {hasRatios ? <>
        <div className="maxpain-caption" style={{ padding: "8px 18px 0" }}>
          {first && latest && <>OI: first {formatPcr(first.pcr)} at {first.time} · latest {formatPcr(latest.pcr)} at {latest.time} · change {change != null && change > 0 ? "+" : ""}{formatPcr(change)} · </>}{available.length} OI minutes · {volumeAvailable.length} volume minutes{current ? ` · ${current.source}` : ""}
        </div>
        <EChartPanel option={option} height={300} />
        {!rows.some(row => row.spot != null && Number.isFinite(row.spot) && row.spot > 0) && <p className="maxpain-caption" style={{ padding: "0 18px" }}>Spot history is unavailable for this selection.</p>}
      </> : <div className="chart-empty" style={{ height: 260 }}>{loading ? "Loading intraday PCR…" : current?.hint || "No PCR observations available for this selection."}</div>}
      <p className="maxpain-caption pcr-chart-key" style={{ padding: "0 18px 12px", margin: 0 }}>Solid = OI PCR. Dashed with diamonds = volume PCR (total put volume ÷ total call volume, cumulative for the session at each capture; selected expiry). Both use green rising, red falling, gray flat. Blue = {instrumentLabel} spot on a separate scale. Missing minutes stay as gaps; isolated volume captures show diamonds.</p>
    </div>
  </>;
}
