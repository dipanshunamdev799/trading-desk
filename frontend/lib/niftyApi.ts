import { API_BASE, type Candle } from "@/lib/api";
import type { PriceActionResponse } from "./priceAction";

export type NiftyFactor = {
  id: string;
  section_id: string;
  label: string;
  priority: string;
  kind: "driver" | "indicator" | "context";
  unit: string;
  description: string;
  source_url: string | null;
  cadence: string;
  status: "available" | "stale" | "missing";
  value: unknown;
  previous_value: unknown;
  change: number | null;
  change_pct: number | null;
  trend: string | null;
  context: unknown;
  source: string | null;
  reported_at: string | null;
  reporting_date?: string | null;
  quality?: string | null;
  quality_note?: string | null;
  observed_at: string | null;
  history: { ts: string; value: number }[];
  historical_context?: unknown;
  basis?: string | null;
  expiry?: string | null;
  strikes?: Record<string, unknown>[];
  availability_note: string;
};

export type NiftySection = { id: string; title: string; description: string; factors: NiftyFactor[] };
export type NiftyEvent = {
  id: string; title: string; event_at: string; source: string; source_url: string | null;
  category: string; impact?: string; actual?: unknown; forecast?: unknown; previous?: unknown;
};
export type NiftyDashboard = {
  generated_at: string; last_refresh: string | null; refreshing: boolean;
  summary: { total: number; available: number; stale: number; missing: number; drivers: number; indicators: number };
  sections: NiftySection[]; candles: Candle[];
  source_errors: { source: string; error: string }[];
  events: NiftyEvent[]; expiries: Record<string, unknown>[]; notes: string[];
};
export type NiftyHistory = {
  factor_id: string;
  observations: { reported_at: string | null; reporting_date?: string | null; observed_at: string; value: unknown; source: string; source_url: string | null; unit?: string; quality_note?: string | null; change: number | null; change_pct: number | null }[];
};
export type NiftyCorrelation = {
  factor_id: string; coefficient: number | null; sample_count: number; method: string; note: string;
};

async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}/nifty${path}`, {
    cache: "no-store", method: body === undefined ? "GET" : "POST",
    ...(body === undefined ? {} : { headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  });
  if (!response.ok) {
    let message = `NIFTY request failed (${response.status})`;
    try {
      const result = await response.json();
      if (typeof result.detail === "string") message = result.detail;
      else if (result.detail) message = JSON.stringify(result.detail);
    } catch { /* Retain the HTTP status when the service returns no JSON. */ }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export const niftyApi = {
  priceAction: (params: Record<string, string>) => request<PriceActionResponse>(`/price-action?${new URLSearchParams(params)}`),
  dashboard: () => request<NiftyDashboard>("/dashboard"),
  refresh: () => request<{ status: "started" | "running" }>("/refresh", {}),
  history: (id: string) => request<NiftyHistory>(`/factors/${encodeURIComponent(id)}/history?limit=365`),
  correlation: (id: string) => request<NiftyCorrelation>(`/correlations?factor_id=${encodeURIComponent(id)}`),
  importObservations: (observations: unknown[]) => request<unknown>("/observations", { observations }),
  importEvents: (events: unknown[]) => request<unknown>("/events", { events }),
};
