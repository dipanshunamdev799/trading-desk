import type { EChartsOption } from "@/components/EChartPanel";
import type { MaxPainGreeks, OptionGreekRow, OptionGreekValues } from "@/lib/api";

export type GreekMetric = keyof OptionGreekValues;
export const GREEK_LABELS: Record<GreekMetric, string> = { delta: "Delta", gamma: "Gamma", theta: "Theta", vega: "Vega", iv: "IV (%)" };

export function formatGreek(value: number | null | undefined, metric: GreekMetric): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const digits = metric === "gamma" ? 6 : metric === "iv" ? 2 : 4;
  return value.toLocaleString("en-IN", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

export function focusGreekStrike(rows: OptionGreekRow[], spot: number | null, selection: number | null): number | null {
  if (rows.some(row => row.strike === selection)) return selection;
  if (!rows.length) return null;
  if (spot == null || !Number.isFinite(spot)) return rows[0].strike;
  return rows.reduce((best, row) => Math.abs(row.strike - spot) < Math.abs(best.strike - spot) ? row : best).strike;
}

export function greekChartOption(data: MaxPainGreeks, metric: GreekMetric, focus: number | null): EChartsOption {
  const label = GREEK_LABELS[metric];
  const markers: object[] = [];
  if (data.spot != null) markers.push({ xAxis: data.spot, name: "Spot at capture", label: { formatter: `Spot ${data.spot.toLocaleString("en-IN")}`, position: "insideEndTop", color: "#8B9AAB" }, lineStyle: { color: "#8B9AAB", type: "dotted" } });
  if (focus != null) markers.push({ xAxis: focus, name: "Selected strike", label: { formatter: `Strike ${focus.toLocaleString("en-IN")}`, position: "insideStartTop", color: "#2DD4A8" }, lineStyle: { color: "#2DD4A8", type: "dashed" } });
  return {
    backgroundColor: "transparent", animation: false,
    legend: { top: 4, data: ["Call", "Put"], textStyle: { color: "#8B9AAB" } },
    grid: { left: metric === "gamma" ? 90 : 76, right: 28, top: 45, bottom: 56 },
    tooltip: { trigger: "axis", confine: true, backgroundColor: "#121820", borderColor: "#243041", textStyle: { color: "#E8EDF2" },
      formatter: (input: unknown) => {
        const items = (Array.isArray(input) ? input : [input]) as { axisValue: number; seriesName: string; value: [number, number | null] }[];
        return [`Strike ${Number(items[0]?.axisValue).toLocaleString("en-IN")}`, ...items.map(item => `${item.seriesName} ${label}: ${item.value?.[1] == null ? "Unavailable" : formatGreek(item.value[1], metric)}`)].join("<br/>");
      } },
    xAxis: { type: "value", min: "dataMin", max: "dataMax", scale: true, name: "Strike", nameLocation: "middle", nameGap: 33,
      nameTextStyle: { color: "#8B9AAB" }, axisLabel: { color: "#8B9AAB", hideOverlap: true }, splitLine: { show: false } },
    yAxis: { type: "value", name: label, nameTextStyle: { color: "#8B9AAB" }, axisLabel: { color: "#8B9AAB", formatter: (value: number) => formatGreek(value, metric) }, splitLine: { lineStyle: { color: "#1A2330" } } },
    series: ([['call', '#E06C75', 'Call'], ['put', '#61AFEF', 'Put']] as const).map(([side, color, name], index) => ({
      name, type: "line", connectNulls: false, showSymbol: data.rows.length < 25, symbolSize: 5,
      data: data.rows.map(row => [row.strike, row[side][metric]]), itemStyle: { color }, lineStyle: { width: 2 },
      ...(index === 0 ? { markLine: { silent: true, symbol: "none", data: markers } } : {}),
    })),
  };
}
