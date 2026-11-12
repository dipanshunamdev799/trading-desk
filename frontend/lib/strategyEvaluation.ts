import { API_BASE } from "@/lib/api";

export type EvaluationInput = {
  id: string;
  label: string;
  group: string;
  available: boolean;
  signal?: number | null;
  reliability?: number | null;
  strength?: number | null;
  source?: string | null;
  reported_at?: string | null;
  observed_at?: string | null;
  reason?: string;
  value?: unknown;
  scored?: boolean;
  predictive_status?: string;
  scoring_status?: "weighted" | "descriptor" | "context" | "unavailable";
};

export type EvaluationFactor = EvaluationInput & {
  weight: number;
  raw_relevance?: number;
  alignment?: number | null;
  stance: string;
  contribution_points: number;
  exclusion_reason?: string;
};

export type EvaluatedStrategy = {
  id: string;
  name: string;
  configuration: string;
  direction: string | number;
  setup_triggered: boolean;
  status: string;
  score: number;
  confidence_score: number;
  coverage: number;
  conflict: number;
  reasons: string[];
  factors: EvaluationFactor[];
  groups?: { id: string; weight: number; alignment: number; reliability: number; available: boolean; contribution_points: number }[];
  historical_evidence?: unknown;
  calibrated_probability?: number | null;
};

export type StrategyEvaluation = {
  generated_at: string;
  as_of: string;
  market_context: {
    regime?: string;
    spot?: number | null;
    atr?: number | null;
    session_phase?: string;
    bar_at?: string | null;
    fresh?: boolean;
    [key: string]: unknown;
  };
  input_audit: EvaluationInput[];
  strategies: EvaluatedStrategy[];
  notes: string[];
  errors: string[];
  methodology?: Record<string, unknown>;
};

export async function fetchStrategyEvaluation(signal?: AbortSignal): Promise<StrategyEvaluation> {
  const response = await fetch(`${API_BASE}/strategies/evaluate`, { cache: "no-store", signal });
  if (!response.ok) {
    let message = `Strategy evaluation failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch { /* Retain the HTTP status when the service returns no JSON. */ }
    throw new Error(message);
  }
  return response.json() as Promise<StrategyEvaluation>;
}

export function evaluationNumber(value: unknown, decimals = 1): string {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toLocaleString("en-IN", { minimumFractionDigits: decimals, maximumFractionDigits: decimals })
    : "—";
}

export function evaluationPercent(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value) ? `${evaluationNumber(value * 100)}%` : "—";
}

export function evaluationTime(value: string | null | undefined): string {
  if (!value) return "Time unavailable";
  const date = new Date(value);
  return Number.isFinite(date.getTime())
    ? `${new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: false }).format(date)} IST`
    : "Time unavailable";
}

export function directionLabel(value: string | number): string {
  if (value === 1 || value === "bullish" || value === "long") return "Bullish";
  if (value === -1 || value === "bearish" || value === "short") return "Bearish";
  return "No direction";
}

export function statusLabel(value: string): string {
  return ({ candidate: "Research candidate", watch: "Watch", insufficient_data: "Insufficient data", blocked: "Blocked" } as Record<string, string>)[value]
    || value.replace(/_/g, " ");
}

export function inputScoringStatus(input: EvaluationInput): "weighted" | "descriptor" | "context" | "unavailable" {
  if (!input.available || input.scoring_status === "unavailable") return "unavailable";
  const directional = typeof input.signal === "number" && Number.isFinite(input.signal);
  const reliable = typeof input.reliability === "number" && Number.isFinite(input.reliability) && input.reliability > 0;
  // Source presence and a measured direction do not establish predictive use.
  if (input.scoring_status === "descriptor" || input.scoring_status === "context") return input.scoring_status;
  if (input.scoring_status === "weighted" || input.scored === true) return directional && reliable ? "weighted" : "descriptor";
  if (input.scored === false) return input.predictive_status || directional ? "descriptor" : "context";
  return directional && reliable ? "weighted" : directional || input.predictive_status ? "descriptor" : "context";
}

export function inputScoringLabel(input: EvaluationInput): string {
  return { weighted: "Scored", descriptor: "Measured descriptor", context: "Context only", unavailable: "Unavailable" }[inputScoringStatus(input)];
}

export function auditValue(value: unknown): string {
  if (value == null) return "Not supplied";
  if (typeof value === "string") return value;
  if (typeof value === "number") return evaluationNumber(value, 2);
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return `${value.length} ${value.length === 1 ? "observation" : "observations"}`;
  if (typeof value === "object") {
    return Object.entries(value).slice(0, 3).map(([key, item]) => `${key.replace(/_/g, " ")}: ${item !== null && typeof item === "object" ? Array.isArray(item) ? `${item.length} observations` : "details" : auditValue(item)}`).join(" · ");
  }
  return String(value);
}

export function readable(value: unknown): string {
  if (value == null) return "Not supplied";
  if (typeof value === "string") return value.replace(/_/g, " ");
  if (typeof value === "number") return evaluationNumber(value, 2);
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (Array.isArray(value)) return value.map(readable).join(" · ");
  if (typeof value === "object") return Object.entries(value).map(([key, item]) => `${key.replace(/_/g, " ")}: ${readable(item)}`).join("; ");
  return String(value);
}
