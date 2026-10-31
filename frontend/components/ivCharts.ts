import type { IvPoint } from "@/lib/api";
import type { EChartsOption } from "./EChartPanel";

export const ivFormat = (v: unknown, digits = 2) => typeof v === "number" && Number.isFinite(v) ? v.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits }) : "—";
const valid = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
const time = (v: number) => new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(v));

export function ivTimeline(day: string, points: IvPoint[]) {
  const byTime = new Map<number, IvPoint>();
  for (const point of points) {
    if (point.date !== day || !/^\d{2}:\d{2}$/.test(point.time)) continue;
    const at = Date.parse(`${day}T${point.time}:00+05:30`);
    if (!Number.isFinite(at)) continue;
    const previous = byTime.get(at);
    if (!previous || Date.parse(point.observed_at) >= Date.parse(previous.observed_at)) byTime.set(at, point);
  }
  const stamps = [...byTime.keys()].sort((a, b) => a-b);
  if (!stamps.length) return [];
  const rows: { at: number; point: IvPoint | null }[] = [];
  for (let at = stamps[0]; at <= stamps[stamps.length-1]; at += 60000) rows.push({ at, point: byTime.get(at) || null });
  return rows;
}

export function ivChartOption(day: string, points: IvPoint[], partial = true): EChartsOption {
  const rows = ivTimeline(day, points);
  const rankName = partial ? "IV Rank (sample)" : "IV Rank";
  const percentileName = partial ? "IV Percentile (sample)" : "IV Percentile";
  const line = (name: string, field: keyof IvPoint, axis: number, color: string) => ({
    name, type: "line" as const, xAxisIndex: axis, yAxisIndex: axis, showSymbol: true, symbolSize: 3,
    connectNulls: false, lineStyle: { width: 2 }, itemStyle: { color },
    data: rows.map(({ at, point }) => [at, point && valid(point[field]) ? point[field] : null]),
  });
  return { animation: false,
    graphic: points.some(p => valid(p.iv_rank) || valid(p.iv_percentile)) ? [] : [{ type: "text", left: "center", top: "49%", style: { text: "Rank / percentile need at least 2 prior saved sessions", fill: "#8B9AAB", fontSize: 11 } }],
    legend: { top: 4, right: 14, textStyle: { color: "#AAB8C7", fontSize: 11 } },
    title: [
      { text: "Annualised ATM IV (%)", top: 32, left: 68, textStyle: { color: "#8B9AAB", fontSize: 10, fontWeight: "normal" } },
      { text: "IV Rank / Percentile (0–100)", top: "37%", left: 68, textStyle: { color: "#8B9AAB", fontSize: 10, fontWeight: "normal" } },
      { text: "Expected move to expiry (± points)", top: "66%", left: 68, textStyle: { color: "#8B9AAB", fontSize: 10, fontWeight: "normal" } },
    ],
    grid: [{ left: 68, right: 26, top: 60, height: "24%" }, { left: 68, right: 26, top: "43%", height: "17%" }, { left: 68, right: 26, top: "72%", height: "17%" }],
    xAxis: [0, 1, 2].map(i => ({ type: "time", gridIndex: i, min: rows[0]?.at, max: rows.at(-1)?.at,
      axisLabel: { show: i === 2, color: "#8B9AAB", hideOverlap: true, formatter: (v: number) => time(v) },
      axisTick: { show: false }, axisLine: { lineStyle: { color: "#243041" } }, splitLine: { show: false } })),
    yAxis: [0, 1, 2].map(i => ({ type: "value", gridIndex: i, ...(i === 1 ? { min: 0, max: 100, interval: 50 } : { scale: true }),
      axisLabel: { color: "#8B9AAB", formatter: (v: number) => ivFormat(v, i === 1 ? 0 : 1) }, splitLine: { lineStyle: { color: "#202B38" } } })),
    axisPointer: { link: [{ xAxisIndex: "all" }] },
    dataZoom: [{ type: "inside", xAxisIndex: [0, 1, 2] }, { type: "slider", xAxisIndex: [0, 1, 2], bottom: 2, height: 15, borderColor: "#243041", textStyle: { color: "#8B9AAB" }, labelFormatter: (v: number) => time(v) }],
    tooltip: { trigger: "axis", confine: true, backgroundColor: "#121820", borderColor: "#243041", textStyle: { color: "#E8EDF2", fontSize: 12 },
      formatter: (raw: unknown) => {
        const item = (Array.isArray(raw) ? raw[0] : raw) as { dataIndex?: number } | undefined;
        const row = item?.dataIndex == null ? null : rows[item.dataIndex];
        if (!row?.point) return row ? `${day} · ${time(row.at)} IST<br/>No IV capture` : "";
        const p = row.point;
        return `${day} · ${time(row.at)} IST<br/><b>ATM IV: ${ivFormat(p.iv)}%</b><br/>Call / Put IV: ${ivFormat(p.call_iv)}% / ${ivFormat(p.put_iv)}%<br/>ATM strike: ${ivFormat(p.strike)}<br/>${rankName}: ${ivFormat(p.iv_rank)}<br/>${percentileName}: ${ivFormat(p.iv_percentile)}<br/>Prior saved sessions: ${p.history_sessions}/252<br/><b>Expected move: ±${ivFormat(p.expected_move)} pts</b><br/>Spot: ${ivFormat(p.spot)} · range ${ivFormat(p.lower)}–${ivFormat(p.upper)}<br/>Calendar days remaining: ${ivFormat(p.days_to_expiry, 3)}<br/>${p.source} · capture ${new Intl.DateTimeFormat('en-GB', {timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(p.observed_at))} IST`;
      } },
    series: [line("ATM IV", "iv", 0, "#E5C07B"), line(rankName, "iv_rank", 1, "#C5A1ED"),
      line(percentileName, "iv_percentile", 1, "#61AFEF"), line("Expected move ±pts", "expected_move", 2, "#2DD4A8")],
  };
}
