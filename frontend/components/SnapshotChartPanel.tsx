"use client";

import { useEffect, useState, type ReactNode } from "react";
import { api, type MaxPainSnapshot } from "@/lib/api";
import { useChartAsOf } from "@/lib/chartAsOf";
import ExpandableChartPanel from "./ExpandableChartPanel";

export default function SnapshotChartPanel({ title, snapshot, asOf, dates, instrumentKey, expiry, loading, refreshId, children }: {
  title: string; snapshot: MaxPainSnapshot | null; asOf: string; dates: string[];
  instrumentKey: string; expiry: string; loading: boolean; refreshId: number;
  children: (state: { snapshot: MaxPainSnapshot | null; loading: boolean; asOf: string }) => ReactNode;
}) {
  const scope = useChartAsOf(asOf, dates);
  const [result, setResult] = useState<{ key: string; data: MaxPainSnapshot } | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<{ key: string; message: string } | null>(null);
  const key = `${instrumentKey}|${expiry}|${scope.date}`;
  useEffect(() => {
    if (!scope.independent || !scope.date || !expiry) return;
    let cancelled = false;
    setPending(true); setError(null); setResult(null);
    api.maxPain({ instrument_key: instrumentKey, expiry, as_of: scope.date, view: "historical" }).then(data => {
      if (data.instrument_key !== instrumentKey || data.expiry !== expiry || data.as_of !== scope.date || data.view !== "historical") {
        throw new Error("The response does not match this chart's underlying, expiry and date.");
      }
      if (!cancelled) setResult({ key, data });
    }).catch(reason => { if (!cancelled) setError({ key, message: reason instanceof Error ? reason.message : "Chart data could not be loaded." }); })
      .finally(() => { if (!cancelled) setPending(false); });
    return () => { cancelled = true; };
  }, [scope.independent, scope.date, expiry, instrumentKey, refreshId, key]);
  const ownData = result?.key === key ? result.data : null;
  const ownError = error?.key === key ? error.message : null;
  return <ExpandableChartPanel title={title} asOf={scope.control} onExpandedChange={scope.onExpandedChange}>
    {scope.independent && ownError && <div className="error-box" role="status">{ownError}</div>}
    {children({ snapshot: scope.independent ? ownData : snapshot,
      loading: scope.independent ? pending || !ownData && !ownError : loading, asOf: scope.date })}
  </ExpandableChartPanel>;
}
