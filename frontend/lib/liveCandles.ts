import type { Candle } from "./api";
import type { LiveQuote } from "./liveMarket";

// Use only exact provider bars. A partial stream must not fabricate a complete
// five-minute/hourly/weekly bar or alter a selected historical range.
export function mergeLiveCandles(candles: Candle[], quote: LiveQuote | undefined, interval: string, from?: string, to?: string): Candle[] {
  const providerInterval = ({ "1minute": "I1", "30minute": "I30", "1day": "1d" } as Record<string, string>)[interval];
  if (!quote || !providerInterval) return candles;
  const today = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  const rows = new Map(candles.map(row => [Date.parse(row.ts), row]));
  for (const bar of quote._live_candles || []) {
    if (bar.interval !== providerInterval) continue;
    const at = typeof bar.ts === "number" || /^\d+$/.test(String(bar.ts)) ? Number(bar.ts) : Date.parse(bar.ts);
    if (!Number.isFinite(at) || at > Date.now()) continue;
    const day = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(at));
    if (day !== today || (from && day < from) || (to && day > to) || ![bar.open, bar.high, bar.low, bar.close].every(Number.isFinite)) continue;
    if (interval === "1day") {
      for (const [key, row] of rows) {
        const existingDay = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(row.ts));
        if (existingDay === day) rows.delete(key);
      }
    }
    rows.set(at, { ts: new Date(at).toISOString(), open: bar.open, high: bar.high, low: bar.low, close: bar.close, volume: bar.vol == null ? null : Number(bar.vol) });
  }
  return [...rows.values()].sort((a, b) => Date.parse(a.ts) - Date.parse(b.ts));
}
