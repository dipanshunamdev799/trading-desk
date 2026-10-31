import type { Candle } from "./api";

export type Strategy = "BEAR_CALL" | "BULL_PUT";
export type SpreadSettings = { capital: number; fee_per_leg: number; slippage: number; auto_exit: boolean };
export type SpreadLeg = { key: string; type: "CE" | "PE"; strike: number; lot_size: number | null; bid: number | null; ask: number | null; bid_qty: number | null; ask_qty: number | null; delta: number | null; iv: number | null; ltp: number | null };
export type SpreadMarket = { options: SpreadLeg[]; expiries: { date: string; dte: number }[]; expiry: string | null; spot: number | null; quote_at: string | null; checked_at: string; error: string | null; source: string; session: { active?: boolean; phase?: string }; options_session: { active?: boolean } };
export type SpreadChart = { interval: string; candles: Candle[]; ema: { ts: string; value: number }[]; trend: string | null; closed_at: string | null; ema_value: number | null; checked_at: string; source: string };
export type SpreadTicket = { request_id: string; strategy: Strategy; expiry: string; short_strike: number; long_strike: number; lots: number; level: number; trend_confirmed: boolean; candle_confirmed: boolean; event_clear: boolean; entry_reason: string };
export type SpreadCheck = { code: string; label: string; passed: boolean; detail: string };
export type SpreadPreview = { eligible: boolean; checks: SpreadCheck[]; credit: number | null; qty: number; lot_size: number | null; width: number; max_profit: number | null; max_loss: number | null; risk_reserved: number | null; round_trip_fees: number; target_debit: number | null; stop_debit: number | null; quote_at: string | null; dte: number };
export type SpreadTrade = SpreadTicket & { id: string; status: "OPEN" | "CLOSED"; created_at: string; closed_at?: string; short: SpreadLeg; long: SpreadLeg; qty: number; lot_size: number; width: number; credit: number; target_debit: number; stop_debit: number; last_debit: number | null; max_profit: number; max_loss: number; risk_reserved: number; entry_delta: number; entry_iv: number | null; dte: number; entry_fees: number; exit_fees?: number; exit_debit?: number; exit_reason?: string; exit_requested: { reason: string; notes: string; at: string } | null; net_pnl: number; unrealized_pnl: number | null; mark_at?: string; mark_fresh: boolean; mark_error?: string; mae: number; mfe: number; return_on_risk?: number; entry_checks: SpreadCheck[] };
export type SpreadOrder = { id: string; trade_id?: string; created_at: string; action: string; status: string; net_price?: number; fees?: number; reason?: string; quote_at?: string; legs: { key: string; side: string; qty: number; price: number }[]; checks?: SpreadCheck[]; ticket?: SpreadTicket };
export type SpreadDashboard = { settings: SpreadSettings; checked_at: string; monitor: { at: string | null; error: string | null }; summary: { equity: number | null; realized_pnl: number; unrealized_pnl: number | null; open_count: number; closed_count: number; open_risk: number; risk_limit: number; win_rate: number | null; expectancy: number | null; max_drawdown: number; return_on_risk: number | null; profit_factor: number | null; fees: number; marks_stale: boolean }; trades: SpreadTrade[]; orders: SpreadOrder[]; marks: { trade_id: string; ts: string; debit: number; pnl: number }[]; equity_curve: { ts: string; equity: number; drawdown: number }[] };

async function request<T>(path: string, body?: unknown, method = "POST"): Promise<T> {
  const response = await fetch(`/api/credit-spreads${path}`, body === undefined ? { cache: "no-store" } : { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(typeof data?.detail === "string" ? data.detail : `Paper trading API returned ${response.status}.`);
  }
  return response.json();
}

export const spreadApi = {
  dashboard: () => request<SpreadDashboard>("/dashboard"),
  market: (expiry: string) => request<SpreadMarket>(`/market${expiry ? `?expiry=${encodeURIComponent(expiry)}` : ""}`),
  chart: (interval: string) => request<SpreadChart>(`/chart?interval=${encodeURIComponent(interval)}`),
  preview: (ticket: SpreadTicket) => request<SpreadPreview>("/preview", ticket),
  enter: (ticket: SpreadTicket) => request<SpreadOrder>("/orders", ticket),
  close: (id: string, reason: string, notes: string) => request<SpreadTrade>(`/trades/${id}/close`, { reason, notes }),
  marks: (id: string) => request<SpreadDashboard["marks"]>(`/trades/${id}/marks`),
  settings: (settings: SpreadSettings) => request<SpreadSettings>("/settings", settings, "PUT"),
};

export function money(value: number | null | undefined, signed = false) {
  return value == null ? "—" : `${signed && value > 0 ? "+" : ""}${new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value)}`;
}
export function points(value: number | null | undefined, decimals = 2) {
  return value == null ? "—" : value.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}
export function ist(value?: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false }) + " IST";
}

export function payoff(strategy: Strategy, short: number, long: number, credit: number, qty: number, fees: number) {
  const width = Math.abs(long - short), start = Math.min(short, long) - width * 1.5, end = Math.max(short, long) + width * 1.5;
  return Array.from({ length: 81 }, (_, i) => {
    const spot = start + (end - start) * i / 80;
    const debit = strategy === "BEAR_CALL" ? Math.max(spot - short, 0) - Math.max(spot - long, 0) : Math.max(short - spot, 0) - Math.max(long - spot, 0);
    return [spot, (credit - debit) * qty - fees];
  });
}
