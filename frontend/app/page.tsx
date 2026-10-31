"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import ChartPanel from "@/components/ChartPanel";
import { Metric, SourceBadge } from "@/components/Bits";
import { api, fmtPnl, type BacktestSummary, type CandleSeries, type PaperSummary } from "@/lib/api";

export default function DeskPage() {
  return (
    <AppShell title="Desk">
      <DeskContent />
    </AppShell>
  );
}

function DeskContent() {
  const [summary, setSummary] = useState<PaperSummary | null>(null);
  const [backtests, setBacktests] = useState<BacktestSummary[]>([]);
  const [series, setSeries] = useState<CandleSeries | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [s, b, c] = await Promise.all([
          api.paperSummary().catch(() => null),
          api.backtests().catch(() => []),
          api
            .candles({
              instrument_key: "NSE_INDEX|Nifty 50",
              interval: "1day",
            })
            .catch(() => null),
        ]);
        if (!alive) return;
        setSummary(s);
        setBacktests(b);
        setSeries(c);
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "Failed to load desk");
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
      {error && <div className="error-box">{error}</div>}

      <div className="metric-strip">
        <Metric
          label="Paper P&L"
          value={fmtPnl(summary?.total_pnl)}
          tone={summary && summary.total_pnl >= 0 ? "pos" : "neg"}
        />
        <Metric label="Open positions" value={String(summary?.open_positions ?? 0)} />
        <Metric label="Backtests on disk" value={String(backtests.length)} />
        <Metric
          label="Nifty bars cached"
          value={series ? String(series.count) : loading ? "…" : "0"}
        />
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>
            Quick chart · Nifty 50 <span className="muted">daily</span>
          </h2>
          <div className="row">
            {series && <SourceBadge source={series.source} />}
            <Link href="/nifty">
              <button>Open NIFTY research</button>
            </Link>
          </div>
        </div>
        <div className="panel-body tight">
          {series && series.candles.length ? (
            <ChartPanel candles={series.candles} height={360} />
          ) : (
            <div className="chart-empty">
              <div>{loading ? "Loading…" : "No bars yet"}</div>
              <div className="muted">
                Charts fill from PostgreSQL, then Upstox on miss. Drop backtest JSON in{" "}
                <code>backtests/</code>.
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Recent backtests</h2>
          <Link href="/backtests">
            <button>View all</button>
          </Link>
        </div>
        <div className="panel-body tight table-wrap">
          {backtests.length === 0 ? (
            <div className="empty-note">
              No backtest outputs yet. Put JSON files in <code>backtests/</code> and refresh.
            </div>
          ) : (
            <table className="data">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Strategy</th>
                  <th>Instrument</th>
                  <th>Interval</th>
                  <th>Return</th>
                  <th>Sharpe</th>
                </tr>
              </thead>
              <tbody>
                {backtests.slice(0, 8).map((b) => (
                  <tr key={b.slug}>
                    <td>
                      <Link href={`/backtests?slug=${encodeURIComponent(b.slug)}`}>{b.name}</Link>
                    </td>
                    <td>{b.strategy ?? "—"}</td>
                    <td className="mono">{b.instrument_key ?? "—"}</td>
                    <td>{b.interval ?? "—"}</td>
                    <td className="num">{fmtPnl(b.metrics.total_return as number)}</td>
                    <td className="num">{String(b.metrics.sharpe ?? "—")}</td>
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
