"use client";

import { useEffect, useMemo, useState } from "react";
import EChartPanel from "@/components/EChartPanel";
import ExpandableChartPanel from "@/components/ExpandableChartPanel";
import { intradayOption } from "@/components/maxpainCharts";
import { api, type MaxPainIntraday } from "@/lib/api";
import { useChartAsOf } from "@/lib/chartAsOf";
import { startMinutePolling } from "@/lib/minutePolling";

type IntradayProps = { expiry: string; asOf: string; instrumentKey: string; refreshId: number; dates?: string[] };

export default function IntradayMaxPainPanel(props: IntradayProps) {
  const scope = useChartAsOf(props.asOf, props.dates || []);
  return <ExpandableChartPanel title="Intraday Max Pain vs Spot" asOf={scope.control} onExpandedChange={scope.onExpandedChange}>
    <IntradayContent key={`${props.instrumentKey}|${props.expiry}|${scope.date}`} {...props} asOf={scope.date} />
  </ExpandableChartPanel>;
}

function IntradayContent({ expiry, asOf, instrumentKey, refreshId }: IntradayProps) {
  const [data, setData] = useState<MaxPainIntraday | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const today = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit",
  }).format(new Date());
  const live = asOf === today && expiry >= today;

  useEffect(() => {
    setData(null);
    setError(null);
    if (!expiry || !asOf) { setLoading(false); return; }
    return startMinutePolling({
      live,
      load: () => api.maxPainIntraday({ expiry, as_of: asOf, instrument_key: instrumentKey }),
      onData: (result) => {
        if (result.expiry !== expiry || result.as_of !== asOf || result.instrument_key !== instrumentKey) {
          setData(null);
          setError("The response does not match this underlying, expiry and date.");
          return;
        }
        setData(result); setError(null);
      },
      onError: (reason) => {
        setError(reason instanceof Error ? reason.message : "Intraday refresh failed");
      },
      onLoading: setLoading,
    });
  }, [expiry, asOf, instrumentKey, live, refreshId]);

  const option = useMemo(() => {
    if (!data?.insights.length) return null;
    return intradayOption({
      times: data.insights.map((row) => row.time ?? ""),
      maxPain: data.insights.map((row) => row.max_pain != null ? Number(row.max_pain) : null),
      spot: data.insights.map((row) => row.spot_price != null ? Number(row.spot_price) : null),
    });
  }, [data]);

  const updated = data ? new Date(data.fetched_at).toLocaleTimeString("en-IN", {
    timeZone: "Asia/Kolkata", hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit",
  }) : null;

  return (
    <>
      <div className="panel-header">
        <h2>Intraday Max Pain vs Spot
          <div className="maxpain-caption">As of {asOf} IST · 1-minute buckets · {live ? "auto-refresh every minute" : "historical snapshot"} · times in IST</div>
        </h2>
        <div className="row" aria-live="polite">
          <span className={`badge ${error ? "warn" : live ? "live" : "db"}`}>
            {error ? "Refresh failed" : loading ? "Updating…" : data?.data_available === false ? "No data" : live ? "Auto-refresh · 1 min" : "Historical · 1 min"}
          </span>
          <span className="muted">{data?.insights.length ?? 0} points{updated ? ` · ${error ? "last successful update" : data?.data_available ? "updated" : "checked"} ${updated} IST` : ""}</span>
        </div>
      </div>
      <div className="panel-body tight" style={{ minHeight: 400 }}>
        {error && <div className="error-box" role="status">{error}{live ? " Retrying next minute." : ""}</div>}
        {option ? <EChartPanel option={option} height={400} /> : (
          <div className="chart-empty" style={{ height: 400 }}>{loading ? "Loading one-minute insights…" : error ? "Unable to load intraday insights" : data?.hint || "No one-minute insights for this date"}</div>
        )}
      </div>
    </>
  );
}
