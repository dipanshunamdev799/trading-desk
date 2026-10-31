"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { Metric } from "@/components/Bits";
import {
  api,
  fmtNum,
  fmtPnl,
  fmtTs,
  type PaperOrder,
  type PaperPosition,
  type PaperSummary,
} from "@/lib/api";

export default function PaperPage() {
  return (
    <AppShell title="Paper trading">
      <PaperContent />
    </AppShell>
  );
}

function PaperContent() {
  const [summary, setSummary] = useState<PaperSummary | null>(null);
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [positions, setPositions] = useState<PaperPosition[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [instrumentKey, setInstrumentKey] = useState("NSE_EQ|INE002A01018");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [qty, setQty] = useState("10");
  const [orderType, setOrderType] = useState("MARKET");
  const [limitPrice, setLimitPrice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [s, o, p] = await Promise.all([
        api.paperSummary(),
        api.paperOrders(),
        api.paperPositions(),
      ]);
      setSummary(s);
      setOrders(o);
      setPositions(p);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load paper portfolio");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.placeOrder({
        instrument_key: instrumentKey,
        side,
        qty: Number(qty),
        order_type: orderType,
        limit_price: limitPrice ? Number(limitPrice) : null,
      });
      setLimitPrice("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Order failed");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="stack">
      <div className="panel"><div className="panel-header"><div><h2>NIFTY Credit Spread System</h2><span className="muted">Two-leg paper trades, live charts, strategy checks and a persistent journal.</span></div><Link className="badge live" href="/credit-spreads">Open strategy desk →</Link></div></div>
      {error && <div className="error-box">{error}</div>}

      <div className="metric-strip">
        <Metric
          label="Total P&L"
          value={fmtPnl(summary?.total_pnl)}
          tone={summary && summary.total_pnl >= 0 ? "pos" : "neg"}
        />
        <Metric
          label="Realized"
          value={fmtPnl(summary?.realized_pnl)}
          tone={summary && summary.realized_pnl >= 0 ? "pos" : "neg"}
        />
        <Metric
          label="Unrealized"
          value={fmtPnl(summary?.unrealized_pnl)}
          tone={summary && summary.unrealized_pnl >= 0 ? "pos" : "neg"}
        />
        <Metric label="Open positions" value={String(summary?.open_positions ?? 0)} />
      </div>

      <div className="grid-2">
        <div className="panel">
          <div className="panel-header">
            <h2>Positions</h2>
            <button onClick={refresh}>Refresh</button>
          </div>
          <div className="panel-body tight table-wrap">
            {summary?.positions?.length ? (
              <table className="data">
                <thead>
                  <tr>
                    <th>Instrument</th>
                    <th>Qty</th>
                    <th>Avg</th>
                    <th>Mark</th>
                    <th>Unrealized</th>
                    <th>Realized</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.positions.map((p) => (
                    <tr key={p.instrument_key}>
                      <td className="mono">{p.instrument_key}</td>
                      <td className="num">{fmtNum(p.qty, 0)}</td>
                      <td className="num">{fmtNum(p.avg_price)}</td>
                      <td className="num">{fmtNum(p.mark)}</td>
                      <td className={`num ${p.unrealized_pnl >= 0 ? "pos" : "neg"}`}>
                        {fmtPnl(p.unrealized_pnl)}
                      </td>
                      <td className={`num ${p.realized_pnl >= 0 ? "pos" : "neg"}`}>
                        {fmtPnl(p.realized_pnl)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-note">No paper positions yet.</div>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2>Order ticket</h2>
            <span className="badge warn">paper only</span>
          </div>
          <div className="panel-body">
            <form className="stack" onSubmit={submit}>
              <div className="field">
                <label>Instrument key</label>
                <input
                  value={instrumentKey}
                  onChange={(e) => setInstrumentKey(e.target.value)}
                  required
                  spellCheck={false}
                />
              </div>
              <div className="row">
                <div className="field">
                  <label>Side</label>
                  <select value={side} onChange={(e) => setSide(e.target.value as "BUY" | "SELL")}>
                    <option value="BUY">BUY</option>
                    <option value="SELL">SELL</option>
                  </select>
                </div>
                <div className="field">
                  <label>Qty</label>
                  <input value={qty} onChange={(e) => setQty(e.target.value)} required />
                </div>
                <div className="field">
                  <label>Type</label>
                  <select value={orderType} onChange={(e) => setOrderType(e.target.value)}>
                    <option value="MARKET">MARKET</option>
                    <option value="LIMIT">LIMIT</option>
                  </select>
                </div>
              </div>
              {orderType === "LIMIT" && (
                <div className="field">
                  <label>Limit price</label>
                  <input
                    value={limitPrice}
                    onChange={(e) => setLimitPrice(e.target.value)}
                    placeholder="0.00"
                  />
                </div>
              )}
              <button className="primary" type="submit" disabled={submitting}>
                {submitting ? "Submitting…" : `Paper ${side.toLowerCase()}`}
              </button>
              <p className="muted" style={{ margin: 0 }}>
                Fills immediately at mark (last daily close, else Upstox LTP). No real orders are
                sent.
              </p>
            </form>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2>Orders</h2>
          <span className="muted">{orders.length} rows</span>
        </div>
        <div className="panel-body tight table-wrap">
          {orders.length === 0 ? (
            <div className="empty-note">No paper orders yet.</div>
          ) : (
            <table className="data">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Side</th>
                  <th>Instrument</th>
                  <th>Qty</th>
                  <th>Type</th>
                  <th>Avg fill</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td className="mono muted">{fmtTs(o.created_at)}</td>
                    <td className={o.side === "BUY" ? "pos" : "neg"}>{o.side}</td>
                    <td className="mono">{o.instrument_key}</td>
                    <td className="num">{fmtNum(o.qty, 0)}</td>
                    <td>{o.order_type}</td>
                    <td className="num">{fmtNum(o.avg_fill_price)}</td>
                    <td>
                      <span className="badge live">{o.status}</span>
                    </td>
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
