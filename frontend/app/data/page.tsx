"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api, fmtNum, fmtTs, type CoverageRow, type IntegrationStatus } from "@/lib/api";

export default function DataPage() {
  return (
    <AppShell title="Data">
      <DataContent />
    </AppShell>
  );
}

function DataContent() {
  const [rows, setRows] = useState<CoverageRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [integration, setIntegration] = useState<IntegrationStatus | null>(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [data, status] = await Promise.all([api.coverage(), api.integrationStatus()]);
        if (alive) { setRows(data); setIntegration(status); }
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "Failed to load coverage");
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  return (
    <div className="stack">
      <div className="panel">
        <div className="panel-header">
          <h2>How data flows</h2>
        </div>
        <div className="panel-body">
          <p className="muted" style={{ margin: 0, lineHeight: 1.7 }}>
            UI request → memory cache → PostgreSQL / TimescaleDB → Upstox on a miss.
            Fetched market data is saved before it is returned. Completed history is retained;
            live data refreshes at minute boundaries. Missing observations stay unavailable.
          </p>
          {integration && <>
            <div className="metric-strip" style={{ marginTop: 16 }}>
              {[
                ["Stored candle rows", integration.counts.candle_rows],
                ["Option candle rows", integration.counts.option_candle_rows],
                ["Retained contracts", integration.counts.option_contracts],
                ["Max Pain points", integration.counts.max_pain_points],
                ["Archived responses", integration.counts.archived_responses],
              ].map(([label, value]) => <div className="metric" key={String(label)}>
                <div className="label">{label}</div><div className="value">{fmtNum(Number(value), 0)}</div>
              </div>)}
            </div>
            <p className="muted" style={{ marginBottom: 0 }}>
              TimescaleDB: {integration.hypertables.join(", ")} · {integration.retention}.
            </p>
          </>}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Candle cache coverage</h2>
          <span className="badge db">PostgreSQL · TimescaleDB</span>
        </div>
        <div className="panel-body tight table-wrap">
          {loading ? (
            <div className="empty-note">Loading…</div>
          ) : error ? (
            <div className="error-box">{error}</div>
          ) : rows.length === 0 ? (
            <div className="empty-note">
              Cache is empty. Load a chart to pull bars from Upstox into Postgres.
            </div>
          ) : (
            <table className="data">
              <thead>
                <tr>
                  <th>Instrument</th>
                  <th>Interval</th>
                  <th>Bars</th>
                  <th>First</th>
                  <th>Last</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={`${r.instrument_key}-${r.interval}`}>
                    <td className="mono">{r.instrument_key}</td>
                    <td>{r.interval}</td>
                    <td className="num">{fmtNum(r.bars, 0)}</td>
                    <td className="mono muted">{fmtTs(r.first_ts)}</td>
                    <td className="mono muted">{fmtTs(r.last_ts)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
