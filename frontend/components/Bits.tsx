export function SourceBadge({ source }: { source?: string | null }) {
  const s = (source || "unknown").toLowerCase();
  const cls = s.includes("upstox") ? "live" : ["db", "cache", "stored"].includes(s) ? "db" : s === "empty" ? "danger" : "warn";
  const label =
    s === "cache" ? "Memory cache" : s === "db" ? "TimescaleDB" : s === "db_partial" ? "TimescaleDB · partial" : s === "stored" ? "Stored data" : s.includes("upstox") ? "Upstox · saved" : s === "empty" ? "no data" : s;
  return <span className={`badge ${cls}`}>{label}</span>;
}

export function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone?: "pos" | "neg" | undefined;
}) {
  return (
    <div className="metric">
      <div className="label">{label}</div>
      <div className={`value ${tone ?? ""}`}>{value}</div>
    </div>
  );
}
