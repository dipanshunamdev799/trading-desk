import type { IpoRow } from "@/lib/api";

export function ipoNumber(value: unknown, digits = 2): string {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toLocaleString("en-IN", { maximumFractionDigits: digits, minimumFractionDigits: digits }) : "—";
}
export function ipoDate(value?: string | null, withTime = false): string {
  if (!value) return "Not announced";
  if (!value.includes("T")) return value;
  const date = new Date(value);
  if (!Number.isFinite(date.getTime())) return "—";
  return date.toLocaleString("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short",
    ...(withTime ? { hour: "2-digit", minute: "2-digit", hour12: false } as const : {}) });
}
export function safeIpoLink(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  try { const url = new URL(value); return url.protocol === "https:" ? url.href : undefined; } catch { return undefined; }
}
export function visibleIpos(rows: IpoRow[], stage: string, segment: string, query: string, sort: string): IpoRow[] {
  const result = rows.filter(row => (stage === "active" ? ["upcoming", "open"].includes(row.stage) : stage === "all" || row.stage === stage)
    && (segment === "all" || row.issue_type === segment)
    && `${row.name} ${row.industry || ""} ${row.symbol || ""}`.toLowerCase().includes(query.trim().toLowerCase()));
  function numeric(row: IpoRow): number | null {
    if (sort === "qib") return typeof row.signals.qib?.value === "number" ? row.signals.qib.value : null;
    if (sort === "gmp") return (row.signals.gmp?.value as { percent?: number | null } | null)?.percent ?? null;
    return null;
  }
  return result.sort((a, b) => {
    if (sort !== "date") {
      const av = numeric(a), bv = numeric(b);
      if (av !== bv) return av == null ? 1 : bv == null ? -1 : bv - av;
    }
    return (a.bidding_start_date || "9999").localeCompare(b.bidding_start_date || "9999") || a.name.localeCompare(b.name);
  });
}
