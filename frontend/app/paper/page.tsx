"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import { Metric } from "@/components/Bits";
import { api, fmtNum, fmtPnl, fmtTs, type PaperOrder, type PaperSummary } from "@/lib/api";
import "./paper.css";

const INSTRUMENTS = [
  { label: "Reliance Industries", key: "NSE_EQ|INE002A01018" },
  { label: "TCS", key: "NSE_EQ|INE467B01029" },
  { label: "HDFC Bank", key: "NSE_EQ|INE040A01034" },
  { label: "ICICI Bank", key: "NSE_EQ|INE090A01021" },
  { label: "Infosys", key: "NSE_EQ|INE009A01021" },
  { label: "State Bank of India", key: "NSE_EQ|INE062A01020" },
];

function instrumentName(key: string) {
  return INSTRUMENTS.find(instrument => instrument.key === key)?.label || key;
}

export default function PaperPage() {
  return <AppShell title="Paper trading"><PaperContent /></AppShell>;
}

function PaperContent() {
  const [summary, setSummary] = useState<PaperSummary | null>(null);
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [orderError, setOrderError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedInstrument, setSelectedInstrument] = useState(INSTRUMENTS[0].key);
  const [customKey, setCustomKey] = useState("");
  const [side, setSide] = useState<"BUY" | "SELL">("BUY");
  const [qty, setQty] = useState("1");
  const [orderType, setOrderType] = useState("MARKET");
  const [limitPrice, setLimitPrice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const instrumentKey = selectedInstrument === "custom" ? customKey.trim() : selectedInstrument;
  const quantity = Number(qty);
  const validQuantity = Number.isSafeInteger(quantity) && quantity > 0;
  const validLimit = Number.isFinite(Number(limitPrice)) && Number(limitPrice) > 0;
  const validInstrument = /^[A-Z0-9_]+\|[^|]+$/.test(instrumentKey);
  const ready = validInstrument && validQuantity && (orderType !== "LIMIT" || validLimit);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const [portfolio, history] = await Promise.all([api.paperSummary(), api.paperOrders()]);
      setSummary(portfolio);
      setOrders(history);
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load your paper account");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!ready || submitting) return;
    setSubmitting(true);
    setOrderError(null);
    setNotice(null);
    try {
      const order = await api.placeOrder({
        instrument_key: instrumentKey,
        side,
        qty: quantity,
        order_type: orderType,
        limit_price: orderType === "LIMIT" ? Number(limitPrice) : null,
      });
      setNotice(`Paper ${order.side.toLowerCase()} recorded: ${fmtNum(order.filled_qty, 0)} unit${order.filled_qty === 1 ? "" : "s"} of ${instrumentName(order.instrument_key)} at ₹${fmtNum(order.avg_fill_price)}. Review your position below.`);
      setLimitPrice("");
      await refresh();
    } catch (reason) {
      setOrderError(reason instanceof Error ? reason.message : "The paper order could not be recorded");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="paper-page stack">
      <section className="paper-intro">
        <div><span className="paper-eyebrow">PRACTICE / SIMULATED ORDERS</span><h2>Learn by placing a paper trade.</h2><p>Choose a stock, review your order, then follow its position. Every order on this page is simulated.</p></div>
        <span className="badge live">Paper account</span>
      </section>

      <ol className="paper-steps" aria-label="Paper trading workflow">
        <li><span>01</span><div><strong>Choose a stock</strong><small>Start with one unit.</small></div></li>
        <li><span>02</span><div><strong>Review your order</strong><small>Check the side and fill method.</small></div></li>
        <li><span>03</span><div><strong>Follow the result</strong><small>Compare your position and fill.</small></div></li>
      </ol>

      {error && <div className="error-box paper-error" role="alert"><div><strong>{summary ? "Account refresh failed" : "Paper account is unavailable"}</strong><p>{error}{summary ? " Showing the last loaded account values." : " Retry to load positions and order history."}</p></div><button type="button" disabled={refreshing} onClick={() => void refresh()}>{refreshing ? "Retrying…" : "Retry connection"}</button></div>}
      {notice && <div className="paper-notice" role="status">{notice}</div>}

      <div className="paper-workspace">
        <section className="panel paper-ticket" aria-labelledby="paper-ticket-title">
          <div className="panel-header"><div><span className="paper-eyebrow">YOUR NEXT ORDER</span><h2 id="paper-ticket-title">Build a paper trade</h2></div><span className="badge warn">Simulation</span></div>
          <div className="panel-body">
            <form className="paper-form" onSubmit={submit}>
              <div className="field"><label htmlFor="paper-instrument">Stock</label><select id="paper-instrument" value={selectedInstrument} onChange={event => setSelectedInstrument(event.target.value)} aria-describedby="paper-instrument-help">{INSTRUMENTS.map(instrument => <option key={instrument.key} value={instrument.key}>{instrument.label}</option>)}<option value="custom">Use a custom instrument key…</option></select><p className="paper-help" id="paper-instrument-help">Pick a familiar stock or enter another supported instrument.</p></div>
              {selectedInstrument === "custom" && <div className="field"><label htmlFor="paper-custom-key">Custom instrument key</label><input id="paper-custom-key" value={customKey} onChange={event => setCustomKey(event.target.value)} placeholder="NSE_EQ|INE002A01018" required spellCheck={false} aria-invalid={customKey.length > 0 && !validInstrument} aria-describedby="paper-custom-help" /><p className="paper-help" id="paper-custom-help">Use the exchange and identifier shown in the chart explorer, for example NSE_EQ|INE002A01018.</p></div>}
              <div className="paper-field-pair">
                <div className="field"><label htmlFor="paper-side">Action</label><select id="paper-side" value={side} onChange={event => setSide(event.target.value as "BUY" | "SELL")} aria-describedby="paper-side-help"><option value="BUY">Buy</option><option value="SELL">Sell</option></select></div>
                <div className="field"><label htmlFor="paper-quantity">Quantity · units</label><input id="paper-quantity" type="number" inputMode="numeric" min="1" step="1" max={Number.MAX_SAFE_INTEGER} value={qty} onChange={event => setQty(event.target.value)} required aria-describedby="paper-quantity-help" /></div>
              </div>
              <p className="paper-help" id="paper-side-help">{side === "BUY" ? "Buy adds units to your position or reduces an existing short position." : "Sell reduces owned units. Selling more than you own creates a simulated short position."}</p>
              <p className="paper-help" id="paper-quantity-help">Quantity means units, not rupees. Start with 1 to understand the workflow.</p>
              <div className="field"><label htmlFor="paper-order-type">Fill method</label><select id="paper-order-type" value={orderType} onChange={event => setOrderType(event.target.value)} aria-describedby="paper-type-help"><option value="MARKET">Market · use the available mark</option><option value="LIMIT">Limit · simulate at a chosen price</option></select><p className="paper-help" id="paper-type-help">{orderType === "MARKET" ? "This simulator fills immediately using the latest stored daily close, or an Upstox quote when no daily close is stored." : "This simulator fills immediately at your entered price. It does not wait for the market to reach a limit."}</p></div>
              {orderType === "LIMIT" && <div className="field"><label htmlFor="paper-limit-price">Simulated fill price · ₹ per unit</label><input id="paper-limit-price" type="number" inputMode="decimal" min="0.01" step="0.01" value={limitPrice} onChange={event => setLimitPrice(event.target.value)} required placeholder="Enter a price" /></div>}
              <div className="paper-review" aria-live="polite" aria-atomic="true"><span className="paper-eyebrow">ORDER REVIEW</span><strong><span className={side === "BUY" ? "pos" : "neg"}>{side === "BUY" ? "Buy" : "Sell"}</span> {validQuantity ? `${quantity} unit${quantity === 1 ? "" : "s"}` : "a quantity"} of {instrumentKey ? instrumentName(instrumentKey) : "your instrument"}</strong><span>{orderType === "LIMIT" ? validLimit ? `Immediate simulated fill at ₹${fmtNum(Number(limitPrice))} per unit${validQuantity ? ` · ₹${fmtNum(quantity * Number(limitPrice))} order value` : ""}` : "Enter a positive price to complete the review." : "Immediate simulated fill at the available mark. The fill price appears in order history."}</span>{!ready && <span className="paper-review-required">{!validInstrument ? "Enter a valid instrument key to continue." : !validQuantity ? "Enter a whole-number quantity of at least 1." : "Enter a positive fill price to continue."}</span>}</div>
              {orderError && <div className="error-box" role="alert">{orderError}</div>}
              <button className="primary paper-submit" type="submit" disabled={submitting || !ready}>{submitting ? "Recording paper order…" : `Place paper ${side.toLowerCase()}`}</button>
              <p className="paper-help paper-fill-note">A market order needs an available price. Fees are not included in this general paper account.</p>
            </form>
          </div>
        </section>

        <section className="panel paper-positions" aria-labelledby="paper-positions-title">
          <div className="panel-header"><div><span className="paper-eyebrow">FOLLOW YOUR TRADE</span><h2 id="paper-positions-title">Your positions</h2></div><button type="button" disabled={refreshing} onClick={() => void refresh()}>{refreshing ? "Refreshing…" : "Refresh"}</button></div>
          <div className="panel-body tight table-wrap">
            {summary?.positions?.length ? <table className="data"><caption className="sr-only">Paper positions with average and current mark prices, unrealized and realized profit or loss</caption><thead><tr><th scope="col">Instrument</th><th scope="col">Units</th><th scope="col">Avg price</th><th scope="col">Mark</th><th scope="col">Unrealized</th><th scope="col">Realized</th></tr></thead><tbody>{summary.positions.map(position => <tr key={position.instrument_key}><td title={position.instrument_key}>{instrumentName(position.instrument_key)}</td><td className="num">{fmtNum(position.qty, 0)}</td><td className="num">₹{fmtNum(position.avg_price)}</td><td className="num">₹{fmtNum(position.mark)}</td><td className={`num ${position.unrealized_pnl >= 0 ? "pos" : "neg"}`}>{fmtPnl(position.unrealized_pnl)}</td><td className={`num ${position.realized_pnl >= 0 ? "pos" : "neg"}`}>{fmtPnl(position.realized_pnl)}</td></tr>)}</tbody></table> : <div className="paper-empty"><span className="paper-empty-symbol" aria-hidden="true">↗</span><h3>{loading ? "Loading your positions…" : error && !summary ? "Positions could not be loaded" : "Your first position starts here"}</h3><p>{loading ? "Checking your saved paper account." : error && !summary ? "Use Retry connection above to check your saved account." : "Choose a stock and place a paper order. Its quantity, average fill and profit or loss will appear here."}</p>{!loading && !error && <a href="#paper-instrument">Choose a stock →</a>}</div>}
          </div>
          <div className="paper-reading"><h3>Read your position</h3><dl><div><dt>Average price</dt><dd>The average fill price of your current position.</dd></div><div><dt>Mark</dt><dd>The price used to value your position. A saved daily close may be used.</dd></div><div><dt>Unrealized P&amp;L</dt><dd>Profit or loss on units you still hold.</dd></div><div><dt>Realized P&amp;L</dt><dd>Profit or loss recorded when units are closed.</dd></div></dl><p>To close a long position, sell the same number of units. To close a short position, buy them back.</p></div>
        </section>
      </div>

      <section aria-label="Paper account summary"><div className="paper-section-title"><h2>Account at a glance</h2><span className="muted">P&amp;L means profit and loss</span></div><div className="metric-strip"><Metric label="Total P&L" value={fmtPnl(summary?.total_pnl)} tone={summary ? summary.total_pnl >= 0 ? "pos" : "neg" : undefined} /><Metric label="Realized · closed units" value={fmtPnl(summary?.realized_pnl)} tone={summary ? summary.realized_pnl >= 0 ? "pos" : "neg" : undefined} /><Metric label="Unrealized · held units" value={fmtPnl(summary?.unrealized_pnl)} tone={summary ? summary.unrealized_pnl >= 0 ? "pos" : "neg" : undefined} /><Metric label="Open positions" value={summary ? String(summary.open_positions) : "—"} /></div></section>

      <section className="panel" aria-labelledby="paper-history-title"><div className="panel-header"><div><h2 id="paper-history-title">Order history</h2><p className="paper-help">Compare your requested quantity with the recorded fill.</p></div><span className="muted">{loading ? "Loading…" : summary ? `${orders.length} recorded` : "Unavailable"}</span></div><div className="panel-body tight table-wrap">{orders.length ? <table className="data"><thead><tr><th scope="col">Time</th><th scope="col">Action</th><th scope="col">Instrument</th><th scope="col">Units</th><th scope="col">Method</th><th scope="col">Avg fill</th><th scope="col">Status</th></tr></thead><tbody>{orders.map(order => <tr key={order.id}><td className="mono muted">{fmtTs(order.created_at)}</td><td className={order.side === "BUY" ? "pos" : "neg"}>{order.side}</td><td title={order.instrument_key}>{instrumentName(order.instrument_key)}</td><td className="num">{fmtNum(order.qty, 0)}</td><td>{order.order_type === "LIMIT" ? "Chosen price" : "Market mark"}</td><td className="num">₹{fmtNum(order.avg_fill_price)}</td><td><span className={`badge ${order.status === "FILLED" ? "live" : "warn"}`}>{order.status}</span></td></tr>)}</tbody></table> : <div className="paper-history-empty">{loading ? "Loading saved orders…" : error && !summary ? "Order history is unavailable until the account reconnects." : "No orders recorded yet. Your submitted paper orders and fill prices will appear here."}</div>}</div></section>

      <section className="paper-next"><div><span className="paper-eyebrow">WHEN YOU ARE READY</span><h2>Practice a two-leg options strategy</h2><p>The credit spread desk has its own paper account, entry checklist and trade journal.</p></div><Link href="/credit-spreads">Explore credit spreads <span aria-hidden="true">→</span></Link></section>
    </div>
  );
}
