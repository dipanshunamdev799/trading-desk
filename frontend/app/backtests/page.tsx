"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import AppShell from "@/components/AppShell";
import ChartPanel from "@/components/ChartPanel";
import { Metric } from "@/components/Bits";
import MaxPainStudy from "@/components/MaxPainStudy";
import { api, fmtNum, fmtPnl, fmtTs, type BacktestDetail, type BacktestSummary } from "@/lib/api";

function ratioLabel(value: unknown, signed = false): string {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  return `${signed && value > 0 ? "+" : ""}${fmtNum(value * 100, 1)}%`;
}

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
      <section className="panel" aria-labelledby="backtest-intro-title">
        <div className="panel-body" style={{ padding: "22px 24px" }}>
          <span className="badge db">Learn from a saved result</span>
          <h2 id="backtest-intro-title" style={{ margin: "12px 0 8px", fontSize: 23, fontWeight: 500, letterSpacing: "-.025em" }}>What would this strategy have done?</h2>
          <p className="muted" style={{ margin: "0 0 16px", maxWidth: 820, lineHeight: 1.7 }}>A backtest applies trading rules to historical data. Choose a result below, follow its account value over time, then inspect the individual trades. Research studies show their own outcomes and comparisons. Past results describe that test and its assumptions.</p>
          <div className="row" style={{ gap: "10px 24px", color: "var(--muted)", fontSize: 12 }}><span><b className="pos">01</b> Choose a result</span><span><b className="pos">02</b> Read the curve</span><span><b className="pos">03</b> Inspect the trades</span></div>
        </div>
      </section>
      {error && <div className="error-box">{error}</div>}

      <div className="panel">
        <div className="panel-header">
          <h2>Choose a saved result</h2>
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
                    <td>
                      <button type="button" aria-pressed={selected === b.slug} onClick={(event) => { event.stopPropagation(); setSelected(b.slug); }} style={{ background: "transparent", color: selected === b.slug ? "var(--accent)" : "var(--ink)", borderColor: selected === b.slug ? "#2b5d50" : "var(--border)", textAlign: "left", minHeight: 38, padding: "7px 10px" }}>{b.name}</button>
                      {b.slug.startsWith("sample-") && <span className="badge warn" style={{ marginLeft: 8 }}>Sample</span>}
                    </td>
                    <td>{b.strategy ?? "—"}</td>
                    <td className="mono">{b.instrument_key ?? "—"}</td>
                    <td>{b.interval ?? "—"}</td>
                    <td className="mono muted">
                      {b.start_date ?? "?"} → {b.end_date ?? "?"}
                    </td>
                    <td className="num">{b.metrics.kind === "max_pain_convergence" ? b.metrics.convergence_rate == null ? "—" : `${fmtNum(b.metrics.convergence_rate as number, 1)}% closer` : ratioLabel(b.metrics.total_return, true)}</td>
                    <td className="num">{b.metrics.kind === "max_pain_convergence" ? `${b.metrics.observations ?? 0} cases` : ratioLabel(b.metrics.max_drawdown)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {detail?.slug.startsWith("sample-") && <div className="panel"><div className="panel-body"><span className="badge warn">Illustrative sample</span><p className="muted" style={{ margin: "8px 0 0", lineHeight: 1.6 }}>This included example is for learning how to read the screen. It is not a live strategy result.</p></div></div>}
      {detail?.research ? <MaxPainStudy key={detail.slug} study={detail.research} /> : detail && (
        <>
          <details className="panel">
            <summary style={{ cursor: "pointer", padding: "14px 18px", color: "var(--info)" }}>What do these performance metrics mean?</summary>
            <div className="panel-body" style={{ borderTop: "1px solid var(--border)", lineHeight: 1.8, color: "var(--muted)" }}>
              <p style={{ margin: "0 0 8px" }}><strong style={{ color: "var(--ink)" }}>Return</strong> measures the change from the starting account value. <strong style={{ color: "var(--ink)" }}>Drawdown</strong> is the largest fall from an earlier peak. Read both together.</p>
              <p style={{ margin: "0 0 8px" }}><strong style={{ color: "var(--ink)" }}>Sharpe</strong> compares return above a reference rate with the variability of returns. Its meaning depends on the test period and calculation.</p>
              <p style={{ margin: 0 }}><strong style={{ color: "var(--ink)" }}>Win rate</strong> is the share of profitable trades. A high win rate can still lose money if losing trades are larger.</p>
            </div>
          </details>
          <div className="metric-strip">
            <Metric
              label="Total return"
              value={ratioLabel(detail.metrics.total_return, true)}
              tone={(detail.metrics.total_return as number) >= 0 ? "pos" : "neg"}
            />
            <Metric label="Sharpe" value={fmtNum(detail.metrics.sharpe as number)} />
            <Metric
              label="Max drawdown"
              value={ratioLabel(detail.metrics.max_drawdown)}
              tone="neg"
            />
            <Metric label="Trades" value={String(detail.trades.length || detail.metrics.trades || 0)} />
            <Metric label="Win rate" value={ratioLabel(detail.metrics.win_rate)} />
          </div>

          <div className="panel">
            <div className="panel-header">
              <div><h2>Equity curve · {detail.name}</h2><p className="muted" style={{ fontSize: 12, margin: "5px 0 0" }}>The simulated account value over time. Look for declines as well as growth.</p></div>
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
