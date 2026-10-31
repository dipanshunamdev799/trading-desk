"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import AppShell from "@/components/AppShell";
import ChartPanel from "@/components/ChartPanel";
import { Metric } from "@/components/Bits";
import MaxPainStudy from "@/components/MaxPainStudy";
import { api, fmtNum, fmtPnl, fmtTs, type BacktestDetail, type BacktestSummary } from "@/lib/api";

export default function BacktestsPage() {
  return (
    <AppShell title="Backtests">
      <Suspense fallback={<div className="empty-note">Loading backtests…</div>}>
        <BacktestsContent />
      </Suspense>
    </AppShell>
  );
}

function BacktestsContent() {
  const params = useSearchParams();
  const initialSlug = params.get("slug") || "";
  const [list, setList] = useState<BacktestSummary[]>([]);
  const [selected, setSelected] = useState<string>(initialSlug);
  const [detailResult, setDetail] = useState<BacktestDetail | null>(null);
  const detail = detailResult?.slug === selected ? detailResult : null;
  const [rescanId, setRescanId] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setError(null);
    let alive = true;
    (async () => {
      try {
        const rows = await api.backtests();
        if (!alive) return;
        setList(rows);
        setSelected((cur) => cur || rows[0]?.slug || "");
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "Failed to list backtests");
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    setError(null);
    let alive = true;
    (async () => {
      try {
        const d = await api.backtest(selected);
        if (alive) setDetail(d);
      } catch (e) {
        if (alive) setError(e instanceof Error ? e.message : "Failed to load backtest");
      }
    })();
    return () => {
      alive = false;
    };
  }, [selected, rescanId]);

  const equityPoints = useMemo(() => {
    if (!detail?.equity?.length) return undefined;
    return detail.equity.map((p) => ({ ts: p.ts || "", value: p.equity }));
  }, [detail]);

  return (
    <div className="stack">
      {error && <div className="error-box">{error}</div>}

      <div className="panel">
        <div className="panel-header">
          <h2>Backtest outputs</h2>
          <div className="row">
            <span className="badge">folder · backtests/*.json</span>
            <button
              onClick={async () => {
                try {
                  const rows = await api.backtests();
                  setList(rows);
                  setSelected((cur) => cur || rows[0]?.slug || "");
                  setRescanId(value => value + 1);
                } catch (e) {
                  setError(e instanceof Error ? e.message : "sync failed");
                }
              }}
            >
              Rescan
            </button>
          </div>
        </div>
        <div className="panel-body tight table-wrap">
          {loading ? (
            <div className="empty-note">Loading…</div>
          ) : list.length === 0 ? (
            <div className="empty-note">
              No backtest files found. Drop JSON into <code>backtests/</code> — name, strategy,
              metrics, equity[], trades[].
            </div>
          ) : (
            <table className="data">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Strategy</th>
                  <th>Instrument</th>
                  <th>Interval</th>
                  <th>Range</th>
                  <th>Return / closer rate</th>
                  <th>Drawdown / cases</th>
                </tr>
              </thead>
              <tbody>
                {list.map((b) => (
                  <tr
                    key={b.slug}
                    onClick={() => setSelected(b.slug)}
                    style={{
                      cursor: "pointer",
                      background: selected === b.slug ? "var(--surface-2)" : undefined,
                    }}
                  >
                    <td>{b.name}</td>
                    <td>{b.strategy ?? "—"}</td>
                    <td className="mono">{b.instrument_key ?? "—"}</td>
                    <td>{b.interval ?? "—"}</td>
                    <td className="mono muted">
                      {b.start_date ?? "?"} → {b.end_date ?? "?"}
                    </td>
                    <td className="num">{b.metrics.kind === "max_pain_convergence" ? b.metrics.convergence_rate == null ? "—" : `${fmtNum(b.metrics.convergence_rate as number, 1)}% closer` : fmtPnl(b.metrics.total_return as number)}</td>
                    <td className="num">{b.metrics.kind === "max_pain_convergence" ? `${b.metrics.observations ?? 0} cases` : fmtNum(b.metrics.max_drawdown as number)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {detail?.research ? <MaxPainStudy key={detail.slug} study={detail.research} /> : detail && (
        <>
          <div className="metric-strip">
            <Metric
              label="Total return"
              value={fmtPnl(detail.metrics.total_return as number)}
              tone={(detail.metrics.total_return as number) >= 0 ? "pos" : "neg"}
            />
            <Metric label="Sharpe" value={fmtNum(detail.metrics.sharpe as number)} />
            <Metric
              label="Max drawdown"
              value={fmtNum(detail.metrics.max_drawdown as number)}
              tone="neg"
            />
            <Metric label="Trades" value={String(detail.trades.length || detail.metrics.trades || 0)} />
            <Metric label="Win rate" value={fmtNum((detail.metrics.win_rate as number) ?? NaN)} />
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Equity curve · {detail.name}</h2>
              <span className="muted mono">{detail.slug}</span>
            </div>
            <div className="panel-body tight">
              {equityPoints?.length ? (
                <ChartPanel candles={[]} equity={equityPoints} height={380} />
              ) : (
                <div className="chart-empty">
                  <div>No equity series in this file</div>
                  <div className="muted">Include an &quot;equity&quot; array for the curve.</div>
                </div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Trades</h2>
              <span className="muted">{detail.trades.length} rows</span>
            </div>
            <div className="panel-body tight table-wrap">
              {detail.trades.length === 0 ? (
                <div className="empty-note">No trades in this backtest file.</div>
              ) : (
                <table className="data">
                  <thead>
                    <tr>
                      <th>Entry</th>
                      <th>Exit</th>
                      <th>Side</th>
                      <th>Qty</th>
                      <th>Entry px</th>
                      <th>Exit px</th>
                      <th>PnL</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.trades.map((t, i) => {
                      const pnl = Number(t.pnl);
                      return (
                        <tr key={i}>
                          <td className="mono muted">{fmtTs(t.entry_ts as string)}</td>
                          <td className="mono muted">{fmtTs(t.exit_ts as string)}</td>
                          <td>{String(t.side ?? "—")}</td>
                          <td className="num">{fmtNum(Number(t.qty), 0)}</td>
                          <td className="num">{fmtNum(Number(t.entry_price))}</td>
                          <td className="num">{fmtNum(Number(t.exit_price))}</td>
                          <td className={`num ${pnl >= 0 ? "pos" : "neg"}`}>{fmtPnl(pnl)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
