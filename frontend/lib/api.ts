export const API_BASE = "/api";

export type Candle = {
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
  oi?: number | null;
};

export type CandleSeries = {
  instrument_key: string;
  interval: string;
  source: string;
  count: number;
  candles: Candle[];
  partial?: boolean;
  hint?: string | null;
};

export type IvPoint = {
  date: string; time: string; observed_at: string; iv: number; call_iv: number; put_iv: number;
  strike: number; spot: number | null; expected_move: number | null; lower: number | null; upper: number | null;
  days_to_expiry: number; source: string; iv_rank: number | null; iv_percentile: number | null;
  history_sessions: number;
};
export type IvHistory = {
  instrument_key: string; expiry: string; as_of: string; points: IvPoint[]; daily_history: IvPoint[];
  history_sessions: number; history_target: number; history_partial: boolean; rank_hint: string;
  data_available: boolean; fetched_at: string; hint: string | null; iv_basis: string; rank_basis: string;
  move_basis: string; source: string;
};

export type Health = {
  ok: boolean;
  database: string;
  upstox_token: boolean;
  version: string;
};

export type BacktestSummary = {
  slug: string;
  name?: string | null;
  strategy?: string | null;
  instrument_key?: string | null;
  interval?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  metrics: Record<string, number | string>;
  source_path?: string | null;
  created_at?: string | null;
};

export type BacktestDetail = BacktestSummary & {
  equity: { ts?: string | null; equity: number; drawdown?: number | null }[];
  trades: Record<string, unknown>[];
  research?: import("./maxpainResearch").MaxPainResearch | null;
};

export type PaperOrder = {
  id: number;
  client_order_id: string;
  instrument_key: string;
  side: "BUY" | "SELL";
  order_type: string;
  qty: number;
  limit_price?: number | null;
  status: string;
  filled_qty: number;
  avg_fill_price?: number | null;
  created_at: string;
  updated_at: string;
  notes?: string | null;
};

export type PaperPosition = {
  instrument_key: string;
  qty: number;
  avg_price: number;
  realized_pnl: number;
  updated_at: string;
};

export type PaperSummary = {
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  open_positions: number;
  positions: {
    instrument_key: string;
    qty: number;
    avg_price: number;
    mark: number;
    unrealized_pnl: number;
    realized_pnl: number;
  }[];
};

export type CoverageRow = {
  instrument_key: string;
  interval: string;
  bars: number;
  first_ts?: string | null;
  last_ts?: string | null;
};

export type IntegrationStatus = {
  path: string[];
  hypertables: string[];
  retention: string;
  counts: Record<string, number>;
  process_metrics: Record<string, number>;
};

export type MaxPainStrike = {
  strike: number;
  call_oi: number;
  put_oi: number;
  call_prev_oi: number | null;
  put_prev_oi: number | null;
  call_ltp: number | null;
  put_ltp: number | null;
  call_premium_date?: string | null;
  put_premium_date?: string | null;
};

export type HistoricalPremiumPrices = {
  basis: string;
  date: string;
  source: string;
  required: number;
  available: number;
  complete: boolean;
  exact: number;
  carried_forward: number;
  carried: { strike: number; side: "CE" | "PE"; close: number; price_date: string; age_days: number; carried_forward: boolean }[];
};

export type OptionGreekValues = { delta: number | null; gamma: number | null; theta: number | null; vega: number | null; iv: number | null };
export type GreekProvenance = { greeks_source: string; greeks_at: string | null; iv_source?: string; iv_at?: string | null };
export type OptionGreekRow = { strike: number; call: OptionGreekValues; put: OptionGreekValues; call_provenance?: GreekProvenance; put_provenance?: GreekProvenance };
export type MaxPainGreeks = {
  instrument_key: string; expiry: string; as_of: string; source: string; source_url: string;
  reported_at: string | null; observed_at: string | null; status: "unavailable" | "snapshot" | "retained" | "historical" | "live" | "latest_rest" | "rest_fallback";
  data_available: boolean; required: number; available: number; complete_legs: number; complete: boolean;
  rows: OptionGreekRow[]; spot: number | null; hint: string | null; basis: string;
  live_legs?: number; transport?: string;
};

export type MaxPainSnapshot = {
  expiry: string;
  as_of: string;
  view?: "latest" | "historical";
  market_context?: { active: boolean; phase: string; session_date: string | null; market_status: string; last_trade_at: string | null } | null;
  instrument_key: string;
  lot_size: number | null;
  oi_unit?: "underlying_units";
  spot: number | null;
  max_pain: number | null;
  min_payout: number | null;
  tied_strikes: number[];
  broadness_pts: number | null;
  warnings: string[];
  provider_max_pain: number | null;
  provider_spot: number | null;
  call_oi_total: number | null;
  put_oi_total: number | null;
  pcr: number | null;
  pcr_observation?: { at: string; pcr: number; source: "websocket" } | null;
  spot_minus_max_pain: number | null;
  strikes: MaxPainStrike[];
  payout_curve: {
    candidates: number[];
    call_payout: number[];
    put_payout: number[];
    total_payout: number[];
  };
  insights: { time?: string; max_pain?: number; spot_price?: number }[];
  fetched_at: string;
  source: string;
  data_available?: boolean;
  hint?: string | null;
  availability?: { payout: string | null; oi: string | null; oi_change: string | null; premiums: string | null; greeks?: string | null };
  option_greeks?: MaxPainGreeks;
  premium_prices?: HistoricalPremiumPrices | null;
  fallback?: {
    requested_expiry: string;
    using_expiry: string;
    reason: string;
  } | null;
  requested_expiry?: string;
  premium_pnl?: {
    assumption?: string;
    identity?: string;
    min_pnl_is_max_payout?: boolean;
    error?: string;
    scenarios?: Record<
      string,
      {
        scenario: string;
        premium_value: number;
        lot_size: number;
        call_oi_coverage_pct: number;
        put_oi_coverage_pct: number;
        min_pnl_price: number;
        min_pnl_value: number;
        breakeven_prices: number[];
        pnl_at_spot: number | null;
        pnl_at_max_pain: number | null;
        warnings: string[];
        candidates: number[];
        call_pnl: number[];
        put_pnl: number[];
        combined_pnl: number[];
        buyer_call_pnl?: number[];
        buyer_put_pnl?: number[];
        buyer_combined_pnl?: number[];
        max_buy_pnl_price?: number;
        max_buy_pnl_value?: number;
      }
    >;
  };
};

export type MaxPainIntraday = {
  expiry: string;
  as_of: string;
  instrument_key: string;
  bucket_minutes: number;
  insights: MaxPainSnapshot["insights"];
  fetched_at: string;
  data_available: boolean;
  hint?: string | null;
};

export type PcrPoint = { time: string; pcr: number | null; spot: number | null; source?: string;
  volume_pcr?: number | null; call_volume?: number; put_volume?: number; volume_observed_at?: string; volume_source?: string };
export type PcrHistory = { instrument_key: string; expiry: string; as_of: string; bucket_minutes: number;
  points: PcrPoint[]; data_available: boolean; source: string; fetched_at: string; hint: string | null;
  oi_pcr_available?: boolean; volume_pcr_available?: boolean; volume_basis?: string; volume_hint?: string | null; oi_hint?: string | null };

export type MaxPainHistoryPoint = {
  expiry: string;
  obs_date: string;
  obs_time: string;
  max_pain: number;
  spot: number;
  expiry_close: number | null;
  kind: string;
  error_pts: number | null;
};

export type ExpiryRow = {
  expiry: string;
  weekly: boolean;
  lot_size: number | null;
  n_contracts: number;
  past?: boolean;
  issue_date?: string;
  cycle?: "weekly" | "monthly" | "unknown";
  available?: boolean;
  verified?: boolean;
};

export type InstrumentHit = {
  name?: string;
  short_name?: string;
  trading_symbol?: string;
  instrument_key: string;
  segment?: string;
  exchange?: string;
  instrument_type?: string;
  isin?: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  ipos: () => request<IpoCatalogue>("/ipos", { cache: "no-store" }),
  ipo: (id: string) => request<IpoDetail>(`/ipos/${encodeURIComponent(id)}`, { cache: "no-store" }),
  health: () => request<Health>("/health"),
  candles: (params: {
    instrument_key: string;
    interval: string;
    from_date?: string;
    to_date?: string;
    force_refresh?: boolean;
  }) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") q.set(k, String(v));
    });
    return request<CandleSeries>(`/market/candles?${q.toString()}`);
  },
  backtests: () => request<BacktestSummary[]>("/backtests"),
  backtest: (slug: string) => request<BacktestDetail>(`/backtests/${encodeURIComponent(slug)}`),
  paperOrders: () => request<PaperOrder[]>("/paper/orders"),
  paperPositions: () => request<PaperPosition[]>("/paper/positions"),
  paperSummary: () => request<PaperSummary>("/paper/summary"),
  placeOrder: (payload: {
    instrument_key: string;
    side: "BUY" | "SELL";
    qty: number;
    order_type?: string;
    limit_price?: number | null;
    notes?: string | null;
  }) =>
    request<PaperOrder>("/paper/orders", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  coverage: () => request<CoverageRow[]>("/data/coverage"),
  integrationStatus: () => request<IntegrationStatus>("/data/integration", { cache: "no-store" }),
  expiries: (instrument_key = "NSE_INDEX|Nifty 50", include_past = true) =>
    request<ExpiryRow[]>(
      `/options/expiries?instrument_key=${encodeURIComponent(instrument_key)}&include_past=${include_past}&include_unverified=true&past_days=180`
    ),
  maxPain: (params: {
    expiry?: string;
    as_of?: string;
    bucket?: number;
    instrument_key?: string;
    view?: "latest" | "historical";
  } = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") q.set(k, String(v));
    });
    const qs = q.toString();
    return request<MaxPainSnapshot>(`/options/max-pain${qs ? `?${qs}` : ""}`, { cache: "no-store" });
  },
  maxPainIntraday: (params: { expiry: string; as_of: string; instrument_key: string }) => {
    const query = new URLSearchParams(params);
    return request<MaxPainIntraday>(`/options/max-pain/intraday?${query.toString()}`, { cache: "no-store" });
  },
  maxPainSessions: (params: { expiry: string; instrument_key: string }) => {
    return request<{ expiry: string; instrument_key: string; dates: string[] }>(`/options/max-pain/sessions?${new URLSearchParams(params).toString()}`, { cache: "no-store" });
  },
  pcrIntraday: (params: { expiry: string; as_of: string; instrument_key: string }) => {
    return request<PcrHistory>(`/options/pcr/intraday?${new URLSearchParams(params).toString()}`, { cache: "no-store" });
  },
  ivHistory: (params: { expiry: string; as_of: string; instrument_key: string }) => {
    return request<IvHistory>(`/options/iv/history?${new URLSearchParams(params).toString()}`, { cache: "no-store" });
  },
  maxPainHistory: (params: {
    expiry?: string;
    as_of?: string;
    history_days?: number;
    signal_time?: string;
    instrument_key?: string;
  } = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") q.set(k, String(v));
    });
    const qs = q.toString();
    return request<{ count: number; points: MaxPainHistoryPoint[] }>(
      `/options/max-pain/history${qs ? `?${qs}` : ""}`, { cache: "no-store" }
    );
  },
  searchInstruments: (q: string, records = 12) =>
    request<InstrumentHit[] | { data?: InstrumentHit[] }>(
      `/market/search?q=${encodeURIComponent(q)}&records=${records}`
    ),
};

export type IpoFactor = {
  id: string; number: number; label: string; group: string; unit: string;
  value: unknown; status: "available" | "pending" | "unavailable" | "stale" | "review";
  source: string; source_url: string | null; fetched_at: string | null;
  reported_at: string | null; period: string | null; note: string | null;
};
export type IpoCompany = {
  id: string; name: string; stage: string; status: string; industry?: string | null;
  issue_type: string; minimum_price?: number | null; maximum_price?: number | null;
  issue_size?: number | null; bidding_start_date?: string | null; bidding_end_date?: string | null;
  lot_size?: number | null; minimum_quantity?: number | null; cut_off_price?: number | null;
  face_value?: number | null; listing_price?: number | null; listing_exchange?: string | null;
  rhp_url?: string | null; drhp_url?: string | null; symbol?: string | null; isin?: string | null;
  catalog_source: string; fetched_at: string; timeline?: Record<string, string | null>;
  registrar_info?: Record<string, string | null>;
};
export type IpoSourceHealth = { source: string; attempted_at: string; succeeded_at: string | null; error: string | null };
export type IpoRow = IpoCompany & { coverage: number; conflicts: string[]; has_public_research: boolean; signals: Record<string, IpoFactor> };
export type IpoCatalogue = { ipos: IpoRow[]; count: number; checked_at: string; refresh_seconds: number; sources: IpoSourceHealth[]; recent_listing_limit: number };
export type IpoDetail = {
  company: IpoCompany; factors: IpoFactor[]; coverage: number; conflicts: string[]; checked_at: string;
  gmp_history: { at: string; value: number | null }[];
  subscription_history: { at: string; qib?: number | null; nii?: number | null; retail?: number | null; total?: number | null }[];
  observations: { observed_at: string; reported_at: string | null; source: string; metric: string; value: number | null }[];
  financials: { periods?: string[]; rows?: Record<string, (number | null)[]> };
  sources: { kind: string; source_url: string; fetched_at: string; reported_at: string | null }[];
  source_errors: IpoSourceHealth[]; raw_upstox: Record<string, unknown> | null;
};

export function fmtNum(n: number | null | undefined, digits = 2): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function fmtPnl(n: number | null | undefined): string {
  const s = fmtNum(n);
  if (n === null || n === undefined) return s;
  return n > 0 ? `+${s}` : s;
}

export function fmtTs(value?: string | number | null): string {
  if (!value) return "—";
  const d = typeof value === "number" ? new Date(value * 1000) : new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toISOString().replace("T", " ").slice(0, 19) + " UTC";
}

export function toUnix(ts: string | number): number {
  if (typeof ts === "number") return ts < 1e12 ? ts : Math.floor(ts / 1000);
  const d = new Date(ts).getTime() / 1000;
  return Math.floor(d);
}
